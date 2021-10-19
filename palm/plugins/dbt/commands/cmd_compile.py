import click
from typing import Optional

@click.command("compile")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--fast", is_flag=True, help="will skip clean/deps/seed")
@click.pass_context
def cli(ctx,
        fast: bool,
        models: Optional[tuple] = tuple()):

    """Cleans up target directory and dependencies, then compiles dbt"""

    def add_models(command:str)->str:
        if models:
            command += " --models " + " ".join(models)
        return command
    if fast:
      ctx.obj.run_in_shell(add_models("dbt compile"))
    else:
      ctx.obj.run_in_shell(add_models("dbt clean && dbt deps && dbt compile"))
