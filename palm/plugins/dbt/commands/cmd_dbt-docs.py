import click

@click.command("dbt-docs")
@click.pass_context
def cli(ctx):
    """generates dbt docs and serves them at http://localhost:8080"""
    ctx.obj.run_in_shell("dbt docs generate && dbt docs serve ")
