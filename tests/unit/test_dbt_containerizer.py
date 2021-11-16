import os
from pathlib import Path
from palm.containerizer import DbtContainerizer

class MockContext:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

DbtContainerizer.__abstractmethods__ = set()

def test_run(tmp_path, environment):
    templates_dir = (Path(__file__).parents[2] / 'palm/plugins/core/templates/containerize')

    os.chdir(tmp_path)
    Path('.env').touch()
    Path('requirements.txt').touch()
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, templates_dir)
    c.run()

    assert Path(tmp_path, 'Dockerfile').exists()
    assert Path(tmp_path, 'requirements.txt').exists()
    assert Path(tmp_path, 'scripts', 'entrypoint.sh').exists()

def test_validate_dbt_version(tmp_path, environment):
    ctx = MockContext(obj=environment)
    default_dbt_version = DbtContainerizer(ctx, tmp_path)
    assert default_dbt_version.validate_dbt_version()

    valid_dbt_version = DbtContainerizer(ctx, tmp_path, dbt_version='0.19.0')
    assert valid_dbt_version.validate_dbt_version()

