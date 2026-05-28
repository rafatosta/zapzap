from __future__ import annotations

import os
import time
import subprocess
from typing import Optional

from copr.v3 import Client


class CoprBuilder:
    def __init__(
        self,
        username: str,
        project_name: str,
        repo_url: str,
        spec_file: str = "com.rtosta.zapzap.spec",
    ):
        self.username = username
        self.project_name = project_name
        self.repo_url = repo_url
        self.spec_file = spec_file

        self.client = Client.create_from_config_file()

    def create_github_release(
        self,
        version: str,
        notes: Optional[str] = None,
        generate_notes: bool = True,
    ) -> None:
        """
        Cria uma release no GitHub usando gh cli.
        """

        print(f"\nCriando GitHub Release: {version}")

        command = [
            "gh",
            "release",
            "create",
            version,
            "--title",
            version,
        ]

        if generate_notes:
            command.append("--generate-notes")

        if notes:
            command.extend([
                "--notes",
                notes,
            ])

        self._run_command(command)

    def build_from_tag(
        self,
        tag: str,
        chroots: Optional[list[str]] = None,
    ) -> int:
        """
        Envia build SCM para o COPR usando tag GitHub.
        """

        if chroots is None:
            chroots = [
                "fedora-44-x86_64",
                "fedora-43-x86_64",
            ]

        print("\nEnviando build para COPR...\n")

        build = self.client.build_proxy.create_from_scm(
            ownername=self.username,
            projectname=self.project_name,
            clone_url=self.repo_url,
            committish=tag,
            spec_path=self.spec_file,
            chroots=chroots,
        )

        print(f"Build enviado com sucesso.")
        print(f"Build ID: {build.id}")

        return build.id

    def watch_build(
        self,
        build_id: int,
        interval: int = 15,
    ) -> str:
        """
        Monitora o build até finalizar.
        """

        print("\nMonitorando build...\n")

        while True:
            build = self.client.build_proxy.get(build_id)

            state = build.state

            print(f"Status: {state}")

            if state in [
                "succeeded",
                "failed",
                "canceled",
                "skipped",
            ]:
                print(f"\nBuild finalizado: {state}")

                return state

            time.sleep(interval)

    def release(
        self,
        version: str,
        release_notes: Optional[str] = None,
        create_release: bool = True,
        wait_build: bool = True,
        chroots: Optional[list[str]] = None,
    ) -> int:

        if create_release:
            self.create_github_release(
                version=version,
                notes=release_notes,
            )

        build_id = self.build_from_tag(
            tag=version,
            chroots=chroots,
        )

        if wait_build:
            self.watch_build(build_id)

        return build_id
    

    @staticmethod
    def _run_command(command: list[str]) -> None:
        print(f"\nExecutando:\n{' '.join(command)}\n")

        process = subprocess.run(
            command,
            text=True,
            check=False,
        )

        if process.returncode != 0:
            raise RuntimeError(
                f"Erro ao executar comando:\n{' '.join(command)}"
            )


if __name__ == "__main__":
    VERSION = os.getenv("VERSION", "6.5")

    builder = CoprBuilder(
        username="rafatosta",
        project_name="zapzap",
        repo_url="https://github.com/rafatosta/zapzap.git",
        spec_file="com.rtosta.zapzap.spec",
    )

    builder.release(
        version=VERSION,
        release_notes="Nova release do ZapZap",
        chroots=[
            "fedora-44-x86_64",
            "fedora-43-x86_64",
        ],
    )