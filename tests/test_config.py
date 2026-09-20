import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tomcat_skills.client import Client
from tomcat_skills.config import resolve_connection


class ConnectionConfigTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        home = patch("tomcat_skills.config.Path.home", return_value=self.home)
        home.start()
        self.addCleanup(home.stop)
        self.config = self.home / ".tomcat" / "automation.json"
        self.config.parent.mkdir()
        self.values = {"project": "../game/Project.tcproj", "port": 9182,
                       "token": "test-token-0123456789"}
        self.write_config(self.values)

    def write_config(self, values):
        self.config.write_text(json.dumps(values), encoding="utf-8")

    def test_default_file_is_independent_of_working_directory(self):
        client = Client()
        self.assertEqual(client.project, str((self.home / "game/Project.tcproj").resolve()))
        self.assertEqual(client.url, "http://127.0.0.1:9182")
        self.assertEqual(client.token, self.values["token"])

    def test_environment_and_explicit_arguments_override_file(self):
        with patch.dict(os.environ, {"TOMCAT_PROJECT": str(self.home / "env.tcproj"),
                                     "TOMCAT_AUTOMATION_PORT": "9000",
                                     "TOMCAT_AUTOMATION_TOKEN": "environment-token-0123"}):
            project, port, token = resolve_connection()
            self.assertEqual(project, str(self.home / "env.tcproj"))
            self.assertEqual(port, 9000)
            self.assertEqual(token, "environment-token-0123")
            project, port, token = resolve_connection(self.home / "explicit.tcproj", 9010, "explicit-token-0123")
            self.assertEqual(project, str(self.home / "explicit.tcproj"))
            self.assertEqual(port, 9010)
            self.assertEqual(token, "explicit-token-0123")

    def test_explicit_config_overrides_environment_config(self):
        alternate = self.home / "alternate.json"
        alternate.write_text(json.dumps(dict(self.values, port=9020)), encoding="utf-8")
        with patch.dict(os.environ, {"TOMCAT_AUTOMATION_CONFIG": str(self.config)}):
            self.assertEqual(resolve_connection(config=alternate)[1], 9020)
        with patch.dict(os.environ, {"TOMCAT_AUTOMATION_CONFIG": str(alternate)}):
            self.assertEqual(resolve_connection()[1], 9020)

    def test_legacy_environment_without_config_and_default_port(self):
        self.config.unlink()
        with patch.dict(os.environ, {"TOMCAT_PROJECT": str(self.home / "game.tcproj"),
                                     "TOMCAT_AUTOMATION_TOKEN": self.values["token"]}):
            self.assertEqual(resolve_connection()[1], 8091)

    def test_missing_explicit_file_does_not_fall_back(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            resolve_connection(config=self.home / "missing.json")

    def test_invalid_config_never_discloses_token(self):
        for invalid in [[], dict(self.values, unknown="secret"),
                        dict(self.values, port=0), dict(self.values, port=True),
                        dict(self.values, port=1.2), dict(self.values, port="bad"),
                        dict(self.values, token="short"), dict(self.values, project="")]:
            with self.subTest(config_type=type(invalid).__name__):
                self.write_config(invalid)
                with self.assertRaises(ValueError) as caught:
                    resolve_connection()
                self.assertNotIn(self.values["token"], str(caught.exception))
        self.config.write_text('{"token":"private-secret",', encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            resolve_connection()
        self.assertNotIn("private-secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
