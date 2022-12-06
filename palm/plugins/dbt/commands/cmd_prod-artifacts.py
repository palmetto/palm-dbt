import click
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars
import sys


@click.command("prod-artifacts")
@click.pass_obj
def cli(environment):

    """No-op command: Download your dbt artifacts from production.

    This command is a no-op as the implementation will differ depending on your
    production environment. You should override this command in your own
    project by running `palm override --name prod-artifacts` and then
    implementing the logic to download your DBT artifacts from production.
    """

    plugin_config = environment.plugin_config("dbt")
    artifact_path = plugin_config.dbt_artifacts_prod

    msg = "No-op command! Please override this command in your own project by running: palm override --name prod-artifacts'"

    env_vars = dbt_env_vars(environment.palm.branch)
    # success, msg = environment.run_in_docker(cmd, env_vars)

    click.secho(msg, fg="red")
    sys.exit(2)
