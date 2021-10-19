from pathlib import Path
from palm import Plugin

def load():
    Plugin.factory('dbt', Path(__file__))
