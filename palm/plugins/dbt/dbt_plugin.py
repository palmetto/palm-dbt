from pathlib import Path
from palm.plugins.base import BasePlugin

DbtPlugin = BasePlugin(
    name = 'dbt', 
    command_dir = Path(__file__) / 'commands',
)
