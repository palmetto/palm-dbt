import os
import pytest
import yaml
from unittest import mock
from pathlib import Path
import pygit2
import shutil
from palm.plugins.dbt.dbt_containerizer import DbtContainerizer
from palm.environment import Environment
from palm.plugin_manager import PluginManager
from palm.palm_config import PalmConfig


class MockContext:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def mock_repository(tmp_path):
    class TemporaryRepository:
        def __init__(self, name, tmp_path):
            self.name = name
            self.tmp_path = tmp_path

        def __enter__(self):
            path = Path(__file__).parent / 'data' / self.name
            temp_repo_path = Path(self.tmp_path) / path.stem
            if path.suffix == '.git':
                shutil.copytree(path, temp_repo_path)
            else:
                raise ValueError(f'Unexpected {path.suffix} extension')

            return temp_repo_path

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    with TemporaryRepository('testrepo.git', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def environment(tmp_path, monkeypatch):
    monkeypatch.setattr(PalmConfig, '_get_repo', mock_repository)
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


def test_validate_dbt_version(environment):
    templates_dir = (
        Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize'
    )
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, templates_dir)

    # Default version is valid
    is_valid, message = c.validate_dbt_version()
    assert is_valid

    # Minimum version is valid
    c = DbtContainerizer(ctx, templates_dir, '0.19.0')
    is_valid, message = c.validate_dbt_version()
    assert is_valid

    # Does not support below minimum version
    c = DbtContainerizer(ctx, templates_dir, '0.18.0')
    is_valid, message = c.validate_dbt_version()
    assert not is_valid

    # Patch versions are ignored
    c = DbtContainerizer(ctx, templates_dir, '0.19.100')
    is_valid, message = c.validate_dbt_version()
    assert is_valid

    # Supported version is valid
    c = DbtContainerizer(ctx, templates_dir, '0.21.1')
    is_valid, message = c.validate_dbt_version()
    assert is_valid

    # Next major is valid
    c = DbtContainerizer(ctx, templates_dir, '1.0.0')
    is_valid, message = c.validate_dbt_version()
    assert is_valid

    # Next minor is invalid
    c = DbtContainerizer(ctx, templates_dir, '1.4.0')
    is_valid, message = c.validate_dbt_version()
    assert not is_valid

    # Next major is invalid
    c = DbtContainerizer(ctx, templates_dir, '2.1.0')
    is_valid, message = c.validate_dbt_version()
    assert not is_valid

def test_profile_strategy_in_project(tmpdir, monkeypatch):
    """When the DBT_PROFILES_DIR is inside the project,
    set the path in compose and env relative to /app
    """
    config_dir = tmpdir / "config"
    config_dir.mkdir()
    with monkeypatch.context() as monkey:
        monkey.setenv("DBT_PROFILES_DIR", str(config_dir))
        assert DbtContainerizer.determine_profile_strategy(tmpdir) == (
            "./config",
            "/app/config",
        )


def test_profile_strategy_outside_project(tmpdir, monkeypatch):
    """When the DBT_PROFILES_DIR is outside the project,
    set the path in compose and env absolutely
    """
    project_dir = tmpdir / "awesome_dbt_project"
    config_dir = tmpdir / "config"
    config_dir.mkdir()
    with monkeypatch.context() as monkey:
        monkey.setenv("DBT_PROFILES_DIR", str(config_dir))
        assert DbtContainerizer.determine_profile_strategy(project_dir) == (
            str(config_dir),
            "/root/.dbt",
        )


def test_profile_strategy_default(tmpdir, monkeypatch):
    """Without a DBT_PROFILES_DIR the default behavior
    is the user's home .dbt adirectory.
    """
    home_dir = tmpdir / "userhome"
    dbt_dir = home_dir / ".dbt"
    [
        d.mkdir()
        for d in (
            home_dir,
            dbt_dir,
        )
    ]
    project_dir = tmpdir / "awesome_dbt_project"
    with mock.patch("pathlib.Path.home", (lambda: Path(str(home_dir)))):
        assert DbtContainerizer.determine_profile_strategy(project_dir) == (
            str(dbt_dir),
            "/root/.dbt",
        )


def test_profile_strategy_none(tmpdir, monkeypatch):
    """If we can't find a profile, return nada."""
    home_dir = tmpdir / "userhome"
    home_dir.mkdir()
    project_dir = tmpdir / "awesome_dbt_project"
    with mock.patch("pathlib.Path.home", (lambda: Path(str(home_dir)))):
        assert DbtContainerizer.determine_profile_strategy(project_dir) == (
            None,
            None,
        )


def test_dbt_project_config(tmpdir, environment):
    dbt_config = {"name": 'test_project'}
    with open(tmpdir / 'dbt_project.yml', 'w') as f:
        f.write(yaml.dump(dbt_config))
    os.chdir(tmpdir)

    templates_dir = (
        Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize'
    )
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, templates_dir)

    assert c.dbt_project_config() == dbt_config


def test_dbt_packages_dir(tmpdir, environment):
    dbt_config = {"name": 'test_project'}
    with open(tmpdir / 'dbt_project.yml', 'w') as f:
        f.write(yaml.dump(dbt_config))
    os.chdir(tmpdir)

    templates_dir = (
        Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize'
    )
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, templates_dir)

    # default value
    assert c.get_packages_dir() == 'dbt_modules'

    # modules-path config
    dbt_config['modules-path'] = 'custom_modules_path'
    with open(tmpdir / 'dbt_project.yml', 'w') as f:
        f.write(yaml.dump(dbt_config))
    assert c.get_packages_dir() == 'custom_modules_path'
    dbt_config.pop('modules-path')

    # package-install-path config (dbt v1.x)
    dbt_config['packages-install-path'] = 'custom_packages_path'
    with open(tmpdir / 'dbt_project.yml', 'w') as f:
        f.write(yaml.dump(dbt_config))
    assert c.get_packages_dir() == 'custom_packages_path'


def test_is_dbt_v1(environment):
    ctx = MockContext(obj=environment)
    c = DbtContainerizer(ctx, Path('.'))

    # True if dbt_version is passed as v1.0.x
    c = DbtContainerizer(ctx, Path('.'), '1.0.0')
    assert c.is_dbt_v1


def test_dbt_packages_dir_supports_v1(tmpdir, environment):
    dbt_config = {"name": 'test_project'}
    with open(tmpdir / 'dbt_project.yml', 'w') as f:
        f.write(yaml.dump(dbt_config))
    os.chdir(tmpdir)

    templates_dir = (
        Path(__file__).parents[2] / 'palm/plugins/dbt/templates/containerize'
    )
    ctx = MockContext(obj=environment)
    # dbt v1 default value
    c = DbtContainerizer(ctx, templates_dir, '1.0.0')
    assert c.get_packages_dir() == 'dbt_packages'
