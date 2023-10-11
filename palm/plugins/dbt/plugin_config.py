import click

from typing import Optional
from pathlib import Path
import yaml
import semver
from pydantic import BaseModel, Field
from palm.plugins.base_plugin_config import BasePluginConfig
from palm.plugins.dbt.dbt_version_detection import dbt_version_factory, get_dbt_version


class dbtPluginConfigModel(BaseModel):
    dbt_artifacts_prod: Optional[str]
    dbt_artifacts_local: str
    dbt_version: str = Field(default_factory=dbt_version_factory)

    def dbt_version_semver(self) -> str:
        return semver.Version.parse(self.dbt_version)

    def is_dbt_version_greater_than(self, version: str, or_equal: bool = True) -> bool:
        target_version = semver.Version.parse(version)
        if or_equal:
            return self.dbt_version_semver() >= target_version
        return self.dbt_version_semver() > target_version

    def is_dbt_version_less_than(self, version: str, or_equal: bool = True) -> bool:
        target_version = semver.Version.parse(version)
        if or_equal:
            return self.dbt_version_semver() <= target_version
        return self.dbt_version_semver() < target_version


class DbtPluginConfig(BasePluginConfig):
    def __init__(self):
        super().__init__('dbt', dbtPluginConfigModel)

    def set(self) -> dict:
        config = {}

        has_prod_artifacts = click.confirm(
            "Do you have production dbt artifacts saved locally?"
        )
        if has_prod_artifacts:
            prod = click.prompt(
                "Prod artifacts location:",
                type=click.Path(exists=True),
                default=Path("target/prod_artifacts"),
            )
            config["dbt_artifacts_prod"] = str(prod)
            click.secho(f"Saved prod artifacts location:  {prod}", fg="green")

        local = click.prompt(
            "Local artifacts location:",
            type=click.Path(exists=True),
            default=Path("target/"),
        )
        config['dbt_artifacts_local'] = str(local)

        config['dbt_version'] = get_dbt_version()

        return config
