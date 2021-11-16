from pathlib import Path
import yaml
import re

class DbtVersionChecker():
  def __init__(self):
    self.dbt_project = self.read_dbt_project()

  def read_dbt_project(self):
    return yaml.safe_load(Path('dbt_project.yml').read_text())

  def configured_dbt_version(self):
    version_list = self.dbt_project.get("require-dbt-version")
    version_number = version_list[0]
    version_number = re.sub(r'[^0-9]', '', version_number)
    return ".".join(version_number.split(".")[:2])

  def is_supported_dbt_version(self):
    version = self.configured_dbt_version()
    return version in self.supported_dbt_versions()

  @property
  def supported_dbt_versions(self):
    return ["0.19", "0.20", "0.21"]