import click

@click.command("shell")
@click.pass_context
def cli(ctx):
    """ WARNING! currently not implemented."""
    click.echo(click.style("Sorry, this is not implemented yet :(", fg="red"))
    