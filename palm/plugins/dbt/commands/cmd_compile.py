import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("compile")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--deps", is_flag=True, help="Will clean and install dependencies")
@click.pass_context
def cli(ctx, deps: bool, models: Optional[Tuple] = tuple()):
    """Cleans up target directory and dependencies, then compiles dbt"""

    if deps:
        cmd = "dbt clean && dbt deps && dbt compile"
    else:
        cmd = "dbt compile"
    if models:
        cmd += f" --models {' '.join(models)}"

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
