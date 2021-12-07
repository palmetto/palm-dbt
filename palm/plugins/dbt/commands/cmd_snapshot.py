import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("snapshot")
@click.option(
    "--persist", is_flag=True, help="will not drop the test schema at the end"
)
@click.option("--select", multiple=True)
@click.option("--fast", is_flag=True, help="will skip clean & deps")
@click.option("--deps", is_flag=True, help="will run clean & deps")
@click.pass_context
def cli(ctx, persist: bool, fast: bool, deps: bool, select: Optional[Tuple] = tuple()):
    """Executes the DBT snapshots."""

    if not fast or deps:
        cmd = "dbt clean && dbt deps && dbt snapshot"
    else:
        cmd = "dbt snapshot"
    if select:
        cmd += f" --select " + " ".join(select)
    if not persist:
        cmd += " && dbt run-operation drop_branch_schemas"

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
