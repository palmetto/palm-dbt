import click
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars

@click.command("dbt-docs")
@click.pass_context
def cli(ctx):
    """generates dbt docs and serves them at http://localhost:8080"""
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    ctx.obj.run_in_docker("dbt docs generate && dbt docs serve ", env_vars)
