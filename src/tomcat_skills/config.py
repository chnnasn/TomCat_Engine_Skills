"""Machine-local connection settings, independent of the installation directory."""
import json
import os
from pathlib import Path


def resolve_connection(project=None, port=None, token=None, config=None):
    explicit = config if config is not None else os.environ.get("TOMCAT_AUTOMATION_CONFIG")
    path = Path(explicit).expanduser() if explicit is not None else Path.home() / ".tomcat" / "automation.json"
    values = {}
    try:
        values = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        if explicit is not None:
            raise ValueError("Connection config file does not exist.") from None
    except (OSError, ValueError):
        raise ValueError("Cannot read connection config: expected a UTF-8 JSON object.") from None
    if not isinstance(values, dict) or set(values) - {"project", "port", "token"}:
        raise ValueError("Connection config accepts only project, port and token.")

    def choose(value, variable, key, default=None):
        return value if value is not None else os.environ.get(variable, values.get(key, default))

    selected_project = choose(project, "TOMCAT_PROJECT", "project")
    selected_port = choose(port, "TOMCAT_AUTOMATION_PORT", "port", 8091)
    selected_token = choose(token, "TOMCAT_AUTOMATION_TOKEN", "token")
    if not isinstance(selected_project, (str, os.PathLike)) or not str(selected_project).strip():
        raise ValueError("Set project in ~/.tomcat/automation.json or TOMCAT_PROJECT.")
    project_path = Path(selected_project).expanduser()
    if project is None and "TOMCAT_PROJECT" not in os.environ and not project_path.is_absolute():
        project_path = path.resolve().parent / project_path
    if isinstance(selected_port, bool) or not isinstance(selected_port, (str, int)):
        raise ValueError("Automation port must be an integer from 1 to 65535.")
    try:
        selected_port = int(selected_port)
    except ValueError:
        raise ValueError("Automation port must be an integer from 1 to 65535.") from None
    if not 1 <= selected_port <= 65535:
        raise ValueError("Automation port must be an integer from 1 to 65535.")
    if not isinstance(selected_token, str) or len(selected_token) < 16 or "\r" in selected_token or "\n" in selected_token:
        raise ValueError("Set a token of at least 16 characters without line breaks in connection config or TOMCAT_AUTOMATION_TOKEN.")
    return str(project_path.resolve()), selected_port, selected_token
