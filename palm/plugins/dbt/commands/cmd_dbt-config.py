import click
from pathlib import Path
from palm.plugins.dbt.plugin_config import PluginConfig


@click.command("dbt-config")
@click.pass_obj
def cli(environment):
    """Set up your palm dbt configuration"""
    click.echo("Setting up your palm dbt configuration")
    config = {}

    has_prod_artifacts = click.confirm("Do you have production dbt artifacts saved locally?")
    if has_prod_artifacts:
        prod = click.prompt("Prod artifacts location:", type=click.Path(exists=True))
        config["dbt_artifacts_prod"] = str(prod)

    local = click.prompt("Local artifacts location:", type=click.Path(exists=True) ,default=Path("target/"))
    config['dbt_artifacts_local'] = str(local)

    PluginConfig.write_config(config)
