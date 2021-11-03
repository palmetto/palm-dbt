import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("compile")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--fast", is_flag=True, help="will skip clean/deps/seed")
@click.pass_context
def cli(ctx,
        fast: bool,
        models: Optional[tuple] = tuple()):
    """Cleans up target directory and dependencies, then compiles dbt"""

    if fast:
      cmd = "dbt compile"
    else:
      cmd = "dbt clean && dbt deps && dbt compile"
    if models:
      cmd += f" --models {models}"

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")