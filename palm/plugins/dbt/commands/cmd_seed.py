import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command('seed')
@click.option(
    "--clean", is_flag=True, help="drop the test schema after the run is complete"
)
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--exclude", multiple=True, help="see dbt docs on exclude flag")
@click.option(
    "--no-full-refresh",
    "-nf",
    is_flag=True,
    help="Insert seeds instead of recreating the table",
)
@click.pass_context
def cli(
    ctx,
    clean: bool,
    no_full_refresh: bool,
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
):
    """Run dbt seeds"""

    cmd = ['dbt', 'seed']
    if select:
        cmd.append('--select')
        cmd.extend(select)
    if exclude:
        cmd.append('--exclude')
        cmd.extend(exclude)
    if not no_full_refresh:
        cmd.append('--full-refresh')
    if clean:
        cmd.append('&& dbt run-operation drop_branch_schemas')

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(" ".join(cmd), env_vars)
    click.secho(msg, fg="green" if success else "red")
