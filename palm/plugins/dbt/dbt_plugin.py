from pathlib import Path
from palm.plugins.base import BasePlugin
import pkg_resources


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
)
