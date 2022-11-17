import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import shell_options, dbt_env_vars


@click.command("run")
@click.option(
    "--no-fail-fast",
    is_flag=True,
    help="Disables the setting which exits immediately if a single model fails to build",
)
@click.option(
    "--persist", is_flag=True, help="will not drop the test schema at the end"
)
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option(
    "--macros", multiple=True, help="see dbt docs on run operations and macros"
)
@click.option(
    "--full-refresh",
    is_flag=True,
    help="will perform a full refresh on incremental models",
)
@click.option("--no-seed", is_flag=True, help="will skip seed full refresh")
@click.pass_context
def cli(
    ctx,
    no_fail_fast: bool,
    persist: bool,
    full_refresh: bool,
    no_seed: bool,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
    macros: Optional[Tuple] = tuple(),
):
    """Runs the DBT repo."""

    cmd = shell_options("run", **locals())
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
