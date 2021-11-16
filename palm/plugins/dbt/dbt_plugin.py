from pathlib import Path
from palm.plugins.base import BasePlugin
import pkg_resources
from dbt_version_checker import DbtVersionChecker

def get_version():
    try:
        version = pkg_resources.require("palm-dbt")[0].version
    except pkg_resources.DistributionNotFound:
        version = 'unknown'
    return version


if DbtVersionChecker().is_supported_dbt_version():
    DbtPlugin = BasePlugin(
        name = 'dbt', 
        command_dir = Path(__file__).parent / 'commands',
        version = get_version(),
        package_location='https://github.com/palmetto/palm-dbt.git'
    )
else:
    raise Exception('dbt plugin requires dbt version >= 0.19.0')
