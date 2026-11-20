"""Tests for the host-visible temporary directory used inside Flatpak."""

import ast
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zapzap.core.environment import setup_manager
from zapzap.core.environment.setup_manager import (
    SetupManager,
    flatpak_shared_temp_dir,
)


SERVER_NAME = "zapzap-application"
SHARED_DIR = "/run/user/1000/app/com.rtosta.zapzap"


def flatpak_environment(**extra):
    return {
        "FLATPAK_ID": "com.rtosta.zapzap",
        "XDG_RUNTIME_DIR": "/run/user/1000",
        **extra,
    }


class FlatpakSharedTempDirTests(unittest.TestCase):

    def resolve(self, environment, *, legacy_socket=False, writable=True):
        return flatpak_shared_temp_dir(
            SERVER_NAME,
            environment,
            path_exists=lambda path: (
                legacy_socket and path == f"/tmp/{SERVER_NAME}"
            ),
            is_writable_dir=lambda path: writable and path == SHARED_DIR,
        )

    def test_uses_the_app_directory_flatpak_shares_with_the_host(self):
        self.assertEqual(self.resolve(flatpak_environment()), SHARED_DIR)

    def test_keeps_the_default_outside_flatpak(self):
        self.assertIsNone(self.resolve({"XDG_RUNTIME_DIR": "/run/user/1000"}))

    def test_keeps_the_default_without_a_runtime_directory(self):
        self.assertIsNone(self.resolve({"FLATPAK_ID": "com.rtosta.zapzap"}))

    def test_keeps_an_explicit_tmpdir(self):
        self.assertIsNone(
            self.resolve(flatpak_environment(TMPDIR="/var/tmp/custom"))
        )

    def test_keeps_the_private_tmp_while_an_older_instance_listens_there(self):
        self.assertIsNone(
            self.resolve(flatpak_environment(), legacy_socket=True)
        )

    def test_keeps_the_default_when_the_directory_is_not_writable(self):
        self.assertIsNone(self.resolve(flatpak_environment(), writable=False))

    def test_checks_the_real_directory_by_default(self):
        server_name = "zapzap-test-socket-that-does-not-exist"
        with tempfile.TemporaryDirectory() as runtime_dir:
            environment = {
                "FLATPAK_ID": "com.rtosta.zapzap",
                "XDG_RUNTIME_DIR": runtime_dir,
            }
            shared_dir = os.path.join(runtime_dir, "app", "com.rtosta.zapzap")

            self.assertIsNone(flatpak_shared_temp_dir(server_name, environment))

            os.makedirs(shared_dir)
            self.assertEqual(
                flatpak_shared_temp_dir(server_name, environment),
                shared_dir,
            )


class ApplyFlatpakTempDirTests(unittest.TestCase):

    def test_sets_tmpdir_when_a_shared_directory_applies(self):
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.object(
                setup_manager,
                "flatpak_shared_temp_dir",
                return_value=SHARED_DIR,
            ) as resolve,
        ):
            os.environ.pop("TMPDIR", None)
            SetupManager.apply_flatpak_temp_dir(SERVER_NAME)

            resolve.assert_called_once_with(SERVER_NAME)
            self.assertEqual(os.environ["TMPDIR"], SHARED_DIR)

    def test_leaves_the_environment_alone_otherwise(self):
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.object(
                setup_manager,
                "flatpak_shared_temp_dir",
                return_value=None,
            ),
        ):
            os.environ.pop("TMPDIR", None)
            SetupManager.apply_flatpak_temp_dir(SERVER_NAME)

            self.assertNotIn("TMPDIR", os.environ)


class TempDirBootstrapOrderTests(unittest.TestCase):

    def test_temp_dir_is_chosen_before_the_single_instance_socket(self):
        application_path = (
            Path(setup_manager.__file__).resolve().parents[2]
            / "app"
            / "application.py"
        )
        tree = ast.parse(application_path.read_text(encoding="utf-8"))
        main = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        calls = [
            node for node in ast.walk(main) if isinstance(node, ast.Call)
        ]
        temp_dir_call = next(
            node
            for node in calls
            if isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "SetupManager"
            and node.func.attr == "apply_flatpak_temp_dir"
        )
        application_call = next(
            node
            for node in calls
            if isinstance(node.func, ast.Name)
            and node.func.id == "SingleApplication"
        )

        self.assertLess(temp_dir_call.lineno, application_call.lineno)


if __name__ == "__main__":
    unittest.main()
