import click
import subprocess
import webbrowser
from pathlib import Path

@click.command("cleanup")
@click.pass_context
def cli(ctx):
    """removes any artifacts from Snowflake
        related to the current branch.
    """
    ctx.obj.run_in_shell("dbt clean && dbt deps && dbt run-operation drop_branch_schemas")
    click.echo("Remote cleanup complete! Cleaning your local docker env...")
    subprocess.run("docker-compose down",
                   check=True,
                   shell=True,
                   cwd=Path.cwd())
    click.echo("Congratulations, you are squeaky clean!")
