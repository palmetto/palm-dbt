import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars

@click.command("snapshot")
@click.option("--persist", is_flag=True, help="will not drop the test schema at the end")
@click.option("--select", multiple=True)
@click.pass_context
def cli(ctx, 
        persist: bool,
        select: Optional[tuple]=()):
    """ Executes the DBT snapshots."""
    
    command = "dbt snapshot"
    if select:
        command += f" --select {select}"
    if not persist:
        command += " && dbt run-operation drop_branch_schemas" 

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    ctx.obj.run_in_shell(command, env_vars)

