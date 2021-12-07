import click
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command('deps')
@click.pass_context
def cli(ctx):
    """Recompile dbt deps"""
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    ctx.obj.run_in_docker('dbt deps', env_vars)
