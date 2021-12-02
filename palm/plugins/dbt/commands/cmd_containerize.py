from typing import Optional
import click
from pathlib import Path
from palm.plugins.dbt.dbt_containerizer import DbtContainerizer


@click.command("containerize")
@click.option(
    "--version",
    multiple=False,
    help="dbt version to use (e.g. 0.21.0)",
)
@click.pass_context
def cli(ctx, version: Optional[str]):
    if not version:
        version = click.prompt("Enter dbt version to use", type=str, default="0.21.0")

    template_dir = Path(Path(__file__).parents[1], "templates") / "containerize"
    DbtContainerizer(ctx, template_dir, version).run()
    click.secho(f"Containerized {ctx.obj.palm.image_name}", fg="green")
