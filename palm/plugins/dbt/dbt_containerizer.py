from pathlib import Path
from typing import Optional
from palm.containerizer import PythonContainerizer
import sys
from palm.palm_exceptions import AbortPalm
import click

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
        self.profiles_file = ''
    
    def run(self) -> None:
        """Runs the containerizer.

        Returns:
            None
        """
        super().check_setup()
        self.package_manager = super().detect_package_manager()
        self.profiles_file = self.detect_profiles_file()
        super().generate(self.target_dir, self.replacements)
        

    def detect_profiles_file(self) -> str:
        """Determines whether or not there is a profiles.yml file in the project root.

        Returns:
            str: exists | unknown
        """
        if self.has_profiles_file():
            return "exists"

        # Unknown profiles.yml, prompt to setup profiles.yml
        try:
            self.optionally_add_profiles_file()
        except AbortPalm:
            click.secho("Aborting containerization", fg="red")
            sys.exit(1)
        return "exists"


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

    def optionally_add_profiles_file(self):
        """Optionally, add a profiles.yml file to the project root if it doesn't exist

        Raises:
            AbortPalm: Abort if user does not want to add profiles.yml
        """
        use_profiles_default = click.confirm(
            "Unable to detect a profiles.yml file, profiles.yml will be used by default. Continue?"
        )
        if use_profiles_default:
            Path("profiles.yml").touch()
        else:
            raise AbortPalm("Aborting")

    def has_profiles_file(self) -> bool:
        """Checks whether or not the project has a profiles.yml file.

        Returns:
            bool: true if profiles.yml or profiles.yaml exists
        """
        profiles_files = ['profiles.yml', 'profiles.yaml']

        for file in profiles_files:
            if Path(file).exists():
                breakpoint()
                return True

        return False