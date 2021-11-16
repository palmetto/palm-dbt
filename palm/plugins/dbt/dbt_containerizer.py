import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars
from palm.containerizer import PythonContainerizer
from palm.palm_exceptions import AbortPalm
from pathlib import Path
import yaml
from palm.plugins.base import BasePlugin
import pkg_resources


class DbtContainerizer(PythonContainerizer):
    """
    Containerizer for dbt projects.
    """

    def __init__(self, ctx, template_dir: Path, python_version: Optional[str] = 3.8) -> None:
        """
        dbtContainerizer constructor.
        """
        super().__init__(ctx, template_dir, python_version)


    def run(self) -> None:
        """
        Run the dbt containerizer.
        """
        if not super().validate_python_version():
            click.secho(f"Invalid python version: {self.python_version}", fg="red")
            return

        try:
            super().validate_python_version()
            super().check_setup()
            self.validate_dbt_version()
        except AbortPalm as e:
            click.secho(str(e), fg="red")
            return
        
        package_manager = super().package_manager()

        if package_manager == "unknown":
            try:
                self.optionally_add_requirements_txt()
            except AbortPalm:
                click.secho("Aborting containerization", fg="red")
                return
            package_manager = "pip3"


        target_dir = Path.cwd()
        replacements = {
            "project_name": self.project_name,
            "package_manager": package_manager,
            "python_version": self.python_version,
            "dbt_version": self.get_dbt_version()
        }

        super().generate(target_dir, replacements)