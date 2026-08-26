"""GitHub App issue integration; all credentials remain server-side."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import json
import os
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class GitHubAppClient:
    API = "https://api.github.com"

    def __init__(self, app_id: str, installation_id: str, private_key: str, repository: str):
        self.app_id = app_id
        self.installation_id = installation_id
        self.private_key = private_key
        self.repository = repository

    @classmethod
    def from_environment(cls):
        required = (
            "GITHUB_APP_ID", "GITHUB_APP_INSTALLATION_ID",
            "GITHUB_APP_PRIVATE_KEY", "GITHUB_REPOSITORY",
        )
        values = {key: os.environ.get(key) for key in required}
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise RuntimeError("missing GitHub App configuration: " + ", ".join(missing))
        return cls(
            values["GITHUB_APP_ID"],
            values["GITHUB_APP_INSTALLATION_ID"],
            values["GITHUB_APP_PRIVATE_KEY"].replace("\\n", "\n"),
            values["GITHUB_REPOSITORY"],
        )

    def _jwt(self):
        now = datetime.now(timezone.utc)
        header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        payload = _b64url(json.dumps({
            "iat": int((now - timedelta(seconds=30)).timestamp()),
            "exp": int((now + timedelta(minutes=9)).timestamp()),
            "iss": self.app_id,
        }).encode())
        unsigned = f"{header}.{payload}".encode()
        key = serialization.load_pem_private_key(self.private_key.encode(), password=None)
        signature = key.sign(unsigned, padding.PKCS1v15(), hashes.SHA256())
        return f"{header}.{payload}.{_b64url(signature)}"

    def _request(self, path: str, *, token: str, method="GET", data=None):
        body = json.dumps(data).encode() if data is not None else None
        request = Request(
            self.API + path,
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "ZapZap-Report-Service/1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())

    def _installation_token(self):
        result = self._request(
            f"/app/installations/{self.installation_id}/access_tokens",
            token=self._jwt(),
            method="POST",
            data={},
        )
        return result["token"]

    def create_issue(self, title: str, body: str):
        return self._request(
            f"/repos/{self.repository}/issues",
            token=self._installation_token(),
            method="POST",
            data={"title": title[:240], "body": body, "labels": ["from-zapzap"]},
        )

    def add_occurrence(self, issue_number: int, occurrences: int):
        return self._request(
            f"/repos/{self.repository}/issues/{issue_number}/comments",
            token=self._installation_token(),
            method="POST",
            data={"body": f"Another sanitized occurrence was received (total: {occurrences})."},
        )
