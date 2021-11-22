import os
import pytest
from pathlib import Path
from palm.plugins.dbt.dbt_containerizer import DbtContainerizer
from palm.environment import Environment
from palm.plugin_manager import PluginManager
from palm.palm_config import PalmConfig


class MockContext:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def environment(tmp_path, monkeypatch):
    monkeypatch.setattr(PalmConfig, '_get_current_branch', lambda x: 'master')
    pm = PluginManager()
    config = PalmConfig(Path(tmp_path))
    return Environment(pm, config)


DbtContainerizer.__abstractmethods__ = set()


def test_run(tmp_path, environment):
    templates_dir = (
        Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize'
    )
    os.chdir(tmp_path)
    Path('.env').touch()
    Path('requirements.txt').touch()
    Path('profiles.yml').touch()
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, templates_dir)
    c.run()

    assert Path(tmp_path, 'Dockerfile').exists()
    assert Path(tmp_path, 'requirements.txt').exists()
    assert Path(tmp_path, 'scripts', 'entrypoint.sh').exists()
    assert Path(tmp_path, 'profiles.yml').exists()
