import click

from pathlib import Path
from pydantic import BaseModel
from palm.plugins.base_plugin_config import BasePluginConfig


class dbtPluginConfigModel(BaseModel):
    dbt_artifacts_prod: str
    dbt_artifacts_local: str


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
                "Prod artifacts location:", type=click.Path(exists=True)
            )
            config["dbt_artifacts_prod"] = str(prod)
            click.secho(f"Saved prod artifacts location:  {prod}", fg="green")

        local = click.prompt(
            "Local artifacts location:",
            type=click.Path(exists=True),
            default=Path("target/"),
        )
        config['dbt_artifacts_local'] = str(local)

        # I don't love that this has to be called by the implementing class
        # could be cleaned up with a decorator or something similar in palm-cli
        self.write(config)
        return config
