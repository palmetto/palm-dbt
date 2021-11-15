from palm.plugins.dbt.dbt_plugin import DbtPlugin
from .dbt_palm_utils import *
from .sql_to_dbt import *
from .local_user_lookup import *
from pathlib import Path
import yaml

Plugin = DbtPlugin

class DbtVersionChecker():
    def __init__(self):
        self.dbt_project = self.read_dbt_project()

    def read_dbt_project(self):
        return yaml.safe_load(Path("dbt_project.yml").read_text())

    def is_supported_dbt_version(self):
        version = self.dbt_project.get("version")
        major_minor = ".".join(version.split(".")[:2])
        return major_minor in self.supported_dbt_version

    @property
    def supported_dbt_version(self):
        return ["0.19", "0.20", "0.21"]
