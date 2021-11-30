from pathlib import Path
from typing import Optional, \
    Tuple
from palm.containerizer import PythonContainerizer
import sys
from palm.palm_exceptions import AbortPalm
import click
import yaml


class DbtContainerizer(PythonContainerizer):
    """
    Containerizer for dbt projects.
    """

    def __init__(
        self, ctx, template_dir: Path, dbt_version: Optional[str] = '0.21.0'
    ) -> None:
        self.ctx = ctx
        self.project_name = ctx.obj.palm.image_name
        self.template_dir = template_dir
        self.dbt_version = dbt_version
        self.package_manager = ''

    def run(self) -> None:
        """Runs the containerizer.

        Returns:
            None
        """
        is_valid_version, message = self.validate_dbt_version()
        if not is_valid_version:
            click.secho(message, fg="red")
            sys.exit(1)

        super().check_setup()
        self.package_manager = super().detect_package_manager()
        self.detect_profiles_file()
        super().generate(self.target_dir, self.replacements)

    def detect_profiles_file(self) -> None:
        """Determines whether or not there is a profiles.yml file in the project root.

        Returns:
            str: exists | unknown
        """
        if self.has_profiles_file():
            return

        # Unknown profiles.yml, prompt to setup profiles.yml
        try:
            self.optionally_add_profiles_file()
        except AbortPalm:
            click.secho("Aborting containerization", fg="red")
            sys.exit(1)
        return

    def optionally_add_profiles_file(self):
        """Optionally, add a profiles.yml file to the project root if it doesn't exist

        Raises:
            AbortPalm: Abort if user does not want to add profiles.yml
        """
        use_profiles_default = click.confirm(
            "Unable to detect a profiles.yml file, would you like to create one?"
        )
        if use_profiles_default:
            profiles_template = {
                self.project_name: {
                    'target': 'DEVELOPMENT',
                    'outputs': {
                        'DEVELOPMENT': {
                            'type': 'postgres',
                            'account': '',
                            'user': '',
                            'password': '',
                            'role': '',
                            'database': '',
                            'warehouse': '',
                            'schema': '',
                            'threads': 8,
                            'client_session_keep_alive': False,
                        }
                    },
                }
            }

            Path("profiles.yml").write_text(yaml.dump(profiles_template))
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
                return True

        return False

    def validate_dbt_version(self) -> tuple[bool, str]:
        """Prompts the user for a DBT version.

        Returns:
            str: DBT version
        """
        semver = self.dbt_version.split(".")
        minimum_version = ['0', '19']
        maximum_version = ['0', '21']

        if semver[0] <= minimum_version[0] and semver[1] < minimum_version[1]:
            return (
                False,
                f'Invalid dbt version, must be > {".".join(minimum_version)}',
            )

        if semver[0] > maximum_version[0] or (
            semver[0] == maximum_version[0] and semver[1] > maximum_version[1]
        ):
            return (
                False,
                f'Invalid dbt version, must be < {".".join(maximum_version)}',
            )

        return (True, f'{self.dbt_version} is valid')

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
        """Pass through function - the PythonContainerizer handles this functionality.

        Returns:
            True
        """
        return True

    def determine_profile_strategy() -> Tuple[str,str]:
        """determines where the on-the-host project 
           has been storing the profiles.yml file
           Returns:
              the host and container volume mount values
        """
        return False
        ## is profile path envar set? 
            ## is it in the repo?
                # create the envar path relative to the /app in container
                # pass that as the compose envar for DBT_PROFILES_DIR
            ## else
                # explicitly set that path in .env via compose as /root/.dbt/profiles.yml
        ## else
            ## explicitly set expanded ~/.dbt/profiles.yml in env 