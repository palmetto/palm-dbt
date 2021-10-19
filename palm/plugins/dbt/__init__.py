from pathlib import Path
from palm.plugins.base import BasePlugin

Plugin = BasePlugin(
    name = 'dbt', 
    path = Path(__file__),
)
