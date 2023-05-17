import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("snapshot")
@click.option("--clean", is_flag=True, help="Drop the test schema after the run")
@click.option("--select", "-s", multiple=True, help="See dbt docs on select flag")
@click.option("--exclude", "-e", multiple=True, help="See dbt docs on exclude flag")
@click.pass_obj
def cli(
    environment,
    clean: bool,
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
):
    """Executes the dbt snapshots."""
    env_vars = dbt_env_vars(environment.palm.branch)

    cmd = ["dbt snapshot"]
    if select:
        cmd.append("--select")
        cmd.extend(select)
    if exclude:
        cmd.append('--exclude')
        cmd.extend(exclude)

    success, msg = environment.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")

    if clean:
        success, msg = environment.run_in_docker(
            "dbt run-operation drop_branch_schemas", env_vars
        )
        click.secho(msg, fg="green" if success else "red")
