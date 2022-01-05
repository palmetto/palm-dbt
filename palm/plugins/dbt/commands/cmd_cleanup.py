import click
import subprocess
from pathlib import Path
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("cleanup")
@click.pass_context
def cli(ctx):
    """Removes any artifacts from Snowflake related to the current branch."""

    cmd = "dbt run-operation drop_branch_schemas && dbt clean && dbt deps"
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")

    click.echo("Remote cleanup complete! Cleaning your local docker env...")
    subprocess.run("docker-compose down", check=True, shell=True, cwd=Path.cwd())
    click.echo("Congratulations, you are squeaky clean!")
