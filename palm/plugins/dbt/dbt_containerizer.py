import os, sys
from pathlib import Path
from typing import Optional, Tuple, Dict
from palm.containerizer import PythonContainerizer
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

        self.package_manager = super().detect_package_manager()
        (
            self.profile_host_path,
            self.profile_volume_path,
        ) = self.determine_profile_strategy(Path.cwd())
        if self.profile_host_path:
            self.write_profile_envs()
        super().generate(self.target_dir, self.replacements)

    def validate_dbt_version(self) -> Tuple[bool, str]:
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
    def is_dbt_v1(self) -> bool:
        """Returns True if dbt version is 1.x.x"""
        return self.dbt_version.split(".")[0] == '1'

    @property
    def replacements(self) -> Dict:
        """
        Return a dictionary of replacements for the dbt template.
        """

        replacements = dict()
        if self.profile_host_path:
            replacements = {
                "dbt_profile_host": self.profile_host_path,
                "profile_volume_mount": ":".join(
                    (
                        "${DBT_PROFILE_HOST}",
                        self.profile_volume_path,
                    )
                ),
            }
        replacements.update(
            {
                "project_name": self.project_name,
                "package_manager": self.package_manager,
                "dbt_version": self.dbt_version,
                "packages_dir": self.get_packages_dir(),
            }
        )
        return replacements

    def validate_python_version(self) -> bool:
        """Pass through function - the PythonContainerizer handles this functionality.

        Returns:
            True
        """
        return True

    def write_profile_envs(self) -> None:
        """Writes dbt profile envars
        to a new .env, or appends to existing env.
        """
        with Path(".env").open("a") as env_file:
            env_file.write(
                (
                    f"DBT_PROFILE_HOST={self.profile_host_path}\n"
                    f"DBT_PROFILES_DIR={self.profile_volume_path}"
                )
            )

    def get_packages_dir(self) -> str:
        deps_dir = "dbt_packages" if self.is_dbt_v1 else "dbt_modules"
        dbt_confg = self.dbt_project_config()
        if dbt_confg.get('modules-path'):
            deps_dir = dbt_confg['modules-path']
        if dbt_confg.get('packages-install-path'):
            deps_dir = dbt_confg['packages-install-path']
        return deps_dir

    def dbt_project_config(self) -> dict:
        config_path = Path("dbt_project.yml")
        if config_path.exists():
            return yaml.safe_load(config_path.read_text())
        return {}

    @classmethod
    def determine_profile_strategy(cls, project_path: "Path") -> Tuple[str, str]:
        """determines where the on-the-host project
        has been storing the profiles.yml file

        Args:
         project_path: the project root to convert
        Returns:
           the host and container volume mount values
        """
        container_default = "/root/.dbt"
        profile_path = os.getenv("DBT_PROFILES_DIR", None)
        if profile_path:
            profiles_dir = Path(profile_path)
            if not profiles_dir.exists():
                raise AbortPalm("Your host has a non-existant DBT_PROFILES_DIR value!")
            if project_path in profiles_dir.parents:
                return cls._relative_paths(profiles_dir, project_path)
            return str(profiles_dir), container_default
        default_profile_path = Path.home() / ".dbt"
        if not default_profile_path.exists():
            click.secho("No DBT profile found. Skipping.", fg="yellow")
            return None, None
        return str(default_profile_path), container_default

    @classmethod
    def _relative_paths(cls, profiles_dir: str, project_path: str) -> Tuple[str, str]:
        """the relative child path of the given profiles dir
        Args:
         profiles_dir: where is the profile?
         project_path: the root of the project
        Returns:
         relative host and container paths <host_relative_path>, <container_absolute_path>,
        """
        return tuple(
            [
                str(profiles_dir).replace(str(project_path), prefix)
                for prefix in (
                    ".",
                    "/app",
                )
            ]
        )
