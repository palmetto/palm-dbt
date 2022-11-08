import click
from typing import Optional, Tuple
<<<<<<< HEAD
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars
=======
from palm.plugins.dbt.dbt_palm_utils import shell_options, dbt_env_vars
from palm.plugins.dbt.plugin_config import PluginConfig
>>>>>>> 6e7652a (Move pluginconfig import to dbt run file)


@click.command("run")
@click.option(
    "--no-fail-fast",
    is_flag=True,
    help="Disables the setting which exits immediately if a single model fails to build",
)
@click.option(
    "--clean", is_flag=True, help="Drop the test schema after the run is complete"
)
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--exclude", multiple=True, help="see dbt docs on exclude flag")
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
    clean: bool,
    full_refresh: bool,
    no_seed: bool,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
):
    """Runs the DBT repo."""

    cmd = []
    if not no_seed:
        cmd.append("dbt seed --full-refresh && ")

    cmd.append("dbt run")
    if select:
        cmd.append("--select")
        cmd.extend(select)
    if models:
        cmd.append("--models")
        cmd.extend(models)
    if exclude:
        cmd.append("--exclude")
        cmd.extend(exclude)
    if not no_fail_fast:
        cmd.append("--fail-fast")
    if full_refresh:
        cmd.append("--full-refresh")
    if clean:
        cmd.append("&& dbt run-operation drop_branch_schemas")

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(" ".join(cmd), env_vars)
    click.secho(msg, fg="green" if success else "red")
