import click
import shutil
from typing import List
from pathlib import Path


@click.command("install")
@click.pass_context
def cli(ctx):
    """Install required palm dbt macros in the dbt project

    Palm uses temporary schemas to ensure running and testing dbt is idempotent
    between changesets. The macros installed in this command enable that functionality
    within any dbt project.

    generate_branch_schemas - creates a schema name for the current git branch. This
    macro _requires_ the PALM_DBT_ENV environment variable be set to DEVELOPMENT | CI | PROD

    drop_branch_schemas - Used to clean up after each run, unless the --persist
    flag is provided. Only runs against a TEST database. Drops schemas matching
    the current git branch name.

    """

    macro_template_path = Path(Path(__file__).parent.parent, "macros")
    macros_path = Path.cwd() / "macros"
    macros = ['drop_branch_schemas.sql', 'generate_schema_name.sql']

    if macros_are_installed(macros_path, macros):
        click.secho("It looks like you already installed palm-dbt macros!", fg="green")
        return

    if not macros_path.exists():
        macros_path.mkdir()

    # Note: we are not using ctx.obj.generate for this because generating jinja marcros
    # is not easy nor fun. Simple file copying is preferable!
    for macro in macros:
        shutil.copy(Path(macro_template_path, macro), Path(macros_path, macro))

    click.secho("Palm dbt macros installed!", fg="green")


def macros_are_installed(macros_path: Path, macros: List[str]) -> bool:
    if not macros_path.exists():
        return False

    for macro in macros:
        if Path(macros_path / macro).exists():
            return True

    return False
