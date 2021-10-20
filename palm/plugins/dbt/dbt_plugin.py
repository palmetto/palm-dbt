from pathlib import Path
from palm.plugins.base import BasePlugin

DbtPlugin = BasePlugin(
    name = 'dbt', 
    path = Path(__file__),
)
