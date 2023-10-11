import click
from pathlib import Path
import yaml

from palm.utils import run_in_docker


def get_dbt_version() -> str:
    """Get the dbt version from the dbt-core package in the docker image.

    Returns:
        str: The dbt version
    """
    image_name = _get_image_name()
    cmd = "pip list | grep dbt-core"
    success, msg = run_in_docker(cmd, image_name, capture_output=True, silent=True)
    if not success:
        raise ValueError(f"Error getting dbt version: {msg}")
    return msg.strip().split(" ")[-1]


def dbt_version_factory() -> str:
    """Get the dbt version from the dbt-core package in the docker image.
    Then update the dbt version in the .palm/config.yaml file.

    Returns:
        str: The dbt version
    """
    click.secho("Detecting dbt version...", fg="yellow")
    version = get_dbt_version()
    set_dbt_version_in_config(version)
    click.secho(
        f"Detected dbt version: {version}. .palm/config.yml updated", fg="green"
    )
    return version


def set_dbt_version_in_config(version: str) -> None:
    """Update the dbt version in the .palm/config.yaml file."""
    palm_config = _get_palm_config()
    palm_config['plugin_config']['dbt']['dbt_version'] = version
    _update_palm_config(palm_config)


def _get_image_name():
    """Get the image name from the .palm/config.yaml file."""
    palm_config = _get_palm_config()
    return palm_config["image_name"]


# Ideally, the 2 functions below would come from palm_config.py in palm-cli
# However, that class is more complicated than it should be and needs a refactor.
# So, for now, we have to do this here.


def _get_palm_config() -> dict:
    """Get the palm config from the .palm/config.yaml file."""
    palm_config_path = Path(".palm/config.yaml")
    if not palm_config_path.exists():
        raise ValueError("No .palm/config.yaml file found")
    return yaml.safe_load(palm_config_path.read_text())


def _update_palm_config(config: dict) -> None:
    """Update the palm config in the .palm/config.yaml file."""
    palm_config_path = Path(".palm/config.yaml")
    if not palm_config_path.exists():
        raise ValueError("No .palm/config.yaml file found")
    palm_config_path.write_text(yaml.dump(config))
