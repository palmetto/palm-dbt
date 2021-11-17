import os
import pytest
from pathlib import Path
from palm.plugins.dbt.dbt_containerizer import DbtContainerizer
from palm.environment import Environment
from palm.palm_config import PalmConfig

class MockContext:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

DbtContainerizer.__abstractmethods__ = set()

def test_run(tmp_path):
    templates_dir = (Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize')
    ctx = None
    os.chdir(tmp_path)
    Path('.env').touch()
    Path('requirements.txt').touch()
    plugin_manager_instance = Environment().plugin_manager
    palm_config = PalmConfig(plugin_manager_instance)
    ctx.obj = Environment(plugin_manager_instance, palm_config)
    c = DbtContainerizer(ctx, templates_dir)
    c.run()
    
    assert ctx.obj == Environment()
    assert Path(tmp_path, 'Dockerfile').exists()
    assert Path(tmp_path, 'requirements.txt').exists()
    assert Path(tmp_path, 'scripts', 'entrypoint.sh').exists()
    assert Path(tmp_path, 'profiles.yml').exists()

