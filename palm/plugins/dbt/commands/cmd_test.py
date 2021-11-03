import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import shell_options, dbt_env_vars

@click.command('test')
@click.option("--fast", is_flag=True, help="will skip clean/deps/seed")
@click.option("--persist", is_flag=True, help="will not drop the test schema at the end")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--no-seed", is_flag=True, help="will skip seed full refresh")
@click.option("--no-fail-fast", is_flag=True, help="will run all tests if one fails")
@click.pass_context
def cli(ctx,
        fast: bool,
        persist: bool,
        no_seed: bool,
        no_fail_fast: bool,
        models: Optional[tuple] = tuple(),
        select: Optional[tuple] = tuple() ):
    """ Tests the DBT repo """

    
    cmd = shell_options("test", **locals())
    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
