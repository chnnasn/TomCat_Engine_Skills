"""Verify installed entry points work without a source checkout on sys.path."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class InstalledPackageTests(unittest.TestCase):
    def run_catalog(self, args):
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        environment.pop("TOMCAT_AUTOMATION_HOME", None)
        with tempfile.TemporaryDirectory(prefix="TomCatSkills-Package-") as directory:
            result = subprocess.run(args, cwd=directory, env=environment,
                                    capture_output=True, text=True, encoding="utf-8", check=True)
        tools = json.loads(result.stdout)
        self.assertTrue(any(tool["name"] == "entity_create" for tool in tools))
        self.assertTrue(any(tool["name"] == "component_get_schema" for tool in tools))
        self.assertEqual(result.stderr, "")

    def test_module_works_outside_checkout(self):
        self.run_catalog([sys.executable, "-m", "tomcat_skills", "list"])

    def test_installed_console_entry(self):
        executable = Path(sys.executable).with_name("tomcat-skills.exe" if os.name == "nt" else "tomcat-skills")
        self.run_catalog([str(executable), "list"])

    def test_wheel_skill_launcher(self):
        skill = Path(sys.prefix) / "share/tomcat-engine-skills/skills/tomcat-editor"
        if not skill.is_dir():
            self.skipTest("Editable/user install: wheel data-file check requires a regular environment install")
        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "references/physics2d.md").is_file())
        self.run_catalog([sys.executable, str(skill / "scripts/tomcat.py"), "list"])


if __name__ == "__main__":
    unittest.main()
