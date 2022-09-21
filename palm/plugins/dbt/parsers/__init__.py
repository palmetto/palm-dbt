from typing import Optional
from pathlib import Path
import yaml
from .project_parser import Project


def parse_project(project_path: Optional[Path] = Path("dbt_project.yml")) -> Project:
    """Parse the dbt project file

    Args:
        project_path (Path): Path to the dbt project file

    Returns:
        Project: Parsed project file
    """

    if not project_path.exists():
        raise FileNotFoundError(f"Could not find {project_path}")

    config = yaml.safe_load(project_path.read_text())
    project = Project(**config)
    return project
