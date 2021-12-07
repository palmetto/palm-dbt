import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("compile")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.pass_context
def cli(ctx, models: Optional[Tuple] = tuple()):
    """Cleans up target directory and dependencies, then compiles dbt"""

    cmd = "dbt compile"
    if models:
        cmd += f" --models {' '.join(models)}"

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
