"""Versioned ZapZap report API."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from .github_app import GitHubAppClient
from .security import sanitize, validate_report
from .storage import ReportRepository


MAX_BODY_BYTES = 128 * 1024
RATE_LIMIT = 10
RATE_WINDOW = timedelta(hours=1)
logger = logging.getLogger("zapzap-report-service")
app = FastAPI(title="ZapZap Report API", version="1")
repository = ReportRepository(Path(os.environ.get("REPORT_DATABASE", "reports.sqlite3")))
requests_by_address = defaultdict(deque)


def _allow(address: str) -> bool:
    now = datetime.now(timezone.utc)
    queue = requests_by_address[address]
    while queue and now - queue[0] > RATE_WINDOW:
        queue.popleft()
    if len(queue) >= RATE_LIMIT:
        return False
    queue.append(now)
    return True


def issue_markdown(report: dict) -> tuple[str, str]:
    kind = report["report_type"]
    if kind == "automatic_crash":
        error = report.get("error_information") or {}
        title = f"Crash: {error.get('type', 'unexpected failure')}"
    else:
        title = f"User report: {report.get('problem_category', 'other')}"
    body = "\n".join((
        "## Report submitted through ZapZap",
        "",
        "The sender reviewed and explicitly confirmed this sanitized payload.",
        "",
        "```json",
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True),
        "```",
    ))
    return title, body


def process_report(report: dict, github=None) -> dict:
    clean = sanitize(report)
    validate_report(clean)
    group = repository.record(clean)
    issue_number = group.get("issue_number")
    if github is None:
        github = GitHubAppClient.from_environment()
    if issue_number:
        github.add_occurrence(issue_number, group["occurrences"])
    else:
        title, body = issue_markdown(clean)
        issue = github.create_issue(title, body)
        issue_number = int(issue["number"])
        repository.set_issue(group["dedup_key"], issue_number)
    return {
        "accepted": True,
        "deduplicated": bool(group["duplicate"]),
        "issue_number": issue_number,
        "public_url": f"https://github.com/{github.repository}/issues/{issue_number}",
    }


@app.post("/api/v1/reports")
async def submit_report(request: Request):
    address = request.client.host if request.client else "unknown"
    if not _allow(address):
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="report too large")
    try:
        report = json.loads(body)
        if not isinstance(report, dict):
            raise ValueError("report must be an object")
        return process_report(report)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception:
        logger.exception("report processing failed")
        raise HTTPException(status_code=503, detail="report service unavailable")


@app.get("/health")
def health():
    return {"status": "ok"}
