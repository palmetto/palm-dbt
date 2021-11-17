from pathlib import Path
from typing import Optional
from palm.containerizer import PythonContainerizer


class DbtContainerizer(PythonContainerizer):
    """
    Containerizer for dbt projects.
    """
    def __init__(self, ctx, template_dir: Path, dbt_version: Optional[str] = '0.21.0') -> None:
        self.ctx = ctx
        self.project_name = ctx.obj.palm.image_name
        self.template_dir = template_dir
        self.dbt_version = dbt_version
        self.package_manager = ''

    @property
    def replacements(self) -> dict:
        """
        Return a dictionary of replacements for the dbt template.
        """
        return {
            "project_name": self.project_name,
            "package_manager": self.package_manager,
            "dbt_version": self.dbt_version,
        }
    

    def validate_python_version(self) -> bool:
        return True