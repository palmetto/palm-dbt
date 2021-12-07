import click
import subprocess
from pathlib import Path
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("cleanup")
@click.option("--deps", is_flag=True, help="Will clean and install dependencies")
@click.pass_context
def cli(ctx, deps: bool):
    """Removes any artifacts from Snowflake related to the current branch."""

    if deps:
        cmd = "dbt clean && dbt deps && dbt run-operation drop_branch_schemas"
    else:
        cmd = "dbt run-operation drop_branch_schemas"
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")

    click.echo("Remote cleanup complete! Cleaning your local docker env...")
    subprocess.run("docker-compose down", check=True, shell=True, cwd=Path.cwd())
    click.echo("Congratulations, you are squeaky clean!")
