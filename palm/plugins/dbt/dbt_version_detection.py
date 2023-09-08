from email.mime import image
from pathlib import Path
import yaml

from palm.utils import run_in_docker

def get_dbt_version():
    image_name = _get_image_name()
    cmd = "pip list | grep dbt-core"
    success, msg = run_in_docker(cmd, image_name, capture_output=True)
    if not success:
        raise ValueError(f"Error getting dbt version: {msg}")
    return msg.strip().split(" ")[-1]


def _get_image_name():
    """Get the image name from the .palm/config.yaml file.

    This isn't great, but we don't want to instantiate a PalmConfig object here.
    """
    palm_config_path = Path(".palm/config.yaml")
    if not palm_config_path.exists():
        raise ValueError("No .palm/config.yaml file found")
    palm_config = yaml.safe_load(palm_config_path.read_text())
    return palm_config["image_name"]
