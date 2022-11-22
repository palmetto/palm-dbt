import pkg_resources
from pathlib import Path

from palm.plugins.dbt.plugin_config import DbtPluginConfig
from palm.plugins.base import BasePlugin


def get_version():
    try:
        version = pkg_resources.require("palm-dbt")[0].version
    except pkg_resources.DistributionNotFound:
        version = 'unknown'
    return version


DbtPlugin = BasePlugin(
    name='dbt',
    command_dir=Path(__file__).parent / 'commands',
    version=get_version(),
    package_location='https://github.com/palmetto/palm-dbt.git',
    config=DbtPluginConfig(),
)
