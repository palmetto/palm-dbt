import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command('test')
@click.option(
    "--clean", is_flag=True, help="drop the test schema after the run is complete"
)
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--exclude", multiple=True, help="see dbt docs on exclude flag")
@click.option("--no-fail-fast", is_flag=True, help="will run all tests if one fails")
@click.pass_context
def cli(
    ctx,
    clean: bool,
    no_fail_fast: bool,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
):
    """Tests the DBT repo"""

    cmd = ['dbt', 'test']
    if select:
        cmd.append('--select')
        cmd.extend(select)
    if models:
        cmd.append('--models')
        cmd.extend(models)
    if exclude:
        cmd.append('--exclude')
        cmd.extend(exclude)
    if not no_fail_fast:
        cmd.append('--fail-fast')
    if clean:
        cmd.append('&& dbt run-operation drop_branch_schemas')

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(" ".join(cmd), env_vars)
    click.secho(msg, fg="green" if success else "red")
