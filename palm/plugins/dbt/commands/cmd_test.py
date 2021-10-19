import click
from typing import Optional
from pathlib import Path

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

    dbt_palm_utils = ctx.obj.import_module('dbt_palm_utils', Path(Path(__file__).parent, 'dbt_palm_utils.py'))
    
    cmd = dbt_palm_utils.shell_options("test", **locals())
    ctx.obj.run_in_shell(cmd)
