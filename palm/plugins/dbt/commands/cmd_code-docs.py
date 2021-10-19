import click
import subprocess
import webbrowser
from pathlib import Path

CODE_DOCS_URI = "http://localhost:8989"

@click.command("code-docs")
@click.pass_context
def cli(ctx):
    f"""generates internal readthedocs for pdp-dbt and serves them at {CODE_DOCS_URI}"""

    click.echo(f"Launching pdp-dbt readthedocs at {CODE_DOCS_URI}")
    subprocess.run('docker-compose run --detach --rm --service-ports pdp_code_documentation',
                   cwd=Path.cwd(),
                   shell=True,
                   check=True)
    webbrowser.open_new_tab(CODE_DOCS_URI)
