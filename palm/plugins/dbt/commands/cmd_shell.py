import click
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command('shell')
@click.pass_context
def cli(ctx):
    """Bash into your docker image to run arbitrary commands"""
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    ctx.obj.run_in_docker('bash', env_vars)
