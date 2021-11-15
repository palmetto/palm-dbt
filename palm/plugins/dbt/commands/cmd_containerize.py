import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars
from palm.containerizer import PythonContainerizer
from palm.palm_exceptions import AbortPalm
from pathlib import Path
import yaml

class DbtContainerizer(PythonContainerizer):
    """
    Containerizer for dbt.
    """

    def generate(self, target_dir, replacements) -> None:
        """
        Generate the container.
        """
        self.ctx.obj.generate(self.template_dir, target_dir, replacements)

    def run(self) -> None:
        try:
            super().check_setup()
        except AbortPalm as e:
            click.secho(str(e), fg="red")
            return
        
        package_manager = super().package_manager()

        if package_manager == "unknown":
            try:
                self.optionally_add_requirements_txt()
            except AbortPalm:
                click.secho("Aborting containerization", fg="red")
                return
            package_manager = "pip3"

        target_dir = Path.cwd()
        replacements = {
            "project_name": self.project_name,
            "package_manager": package_manager,
            "dbt_version": self.get_dbt_version()
        }

        self.generate(target_dir, replacements)

    def get_dbt_version(self):
        """
        Get the dbt version from the dbt_project.yml file.
        """
        with open("dbt_project.yml", "r") as f:
            dbt_yml = yaml.safe_load(f)
        return dbt_yml["require-dbt-version"]


@click.command("containerize")
@click.option("-i", "--image-name", multiple=False, help="Name of your docker image")
@click.pass_context
def cli(ctx, image_name):
    """Implement containerization for the current project
    
    Assumes standard dbt project structure
    Uses docker and docker-compose to implement basic containerization
    
    """
    image_name = image_name or ctx.obj.palm.image_name
    template_dir = Path(Path(__file__).parent.parent, 'templates', 'containerize')
    DbtContainerizer(ctx, image_name, template_dir).run()  
    click.secho(f"Containerized {image_name} successfully!", fg='green')  