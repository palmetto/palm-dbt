from pathlib import Path
from click import secho
from typing import Optional
import yaml


class PluginConfig:

    def __init__(self, project_path: Optional["Path"] = Path.cwd()):
        self.config_path = project_path / '.palm' / 'dbt-config.yaml'
        self.config = self._get_config()

    def _get_config(self) -> object:
        """Gets dbt config options from the local project.

        Returns:
            object: dict of project config options
        """
        if not self.config_path.exists():
          secho('No user config found, run `palm dbt-config`', fg='red')
          return {}

        return yaml.safe_load(self.config_path.read_text())

    @property
    def dbt_artifacts_local(self) -> str:
        key = self.config.get('dbt_artifacts_local')
        if not key:
            raise ValueError('Local artifacts path not found, run `palm dbt-config`')
        return key

    @property
    def dbt_artifacts_prod(self) -> str:
        secret = self.config.get('dbt_artifacts_prod')
        if not secret:
            raise ValueError(
                'Prod artifacts path not found, run `palm dbt-config`'
            )
        return secret

    @classmethod
    def write_config(cls, config):
        cls.config_path.parent.mkdir(parents=True, exist_ok=True)
        cls.config_path.write_text(yaml.dump(config))
