import click
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("prod-artifacts")
@click.pass_context
def cli(ctx):
    """No-op command: Download your DBT artifacts from production.

    This command is a no-op as the implementation will differ depending on your
    production environment. You should override this command in your own
    project by running `palm override --name prod-artifacts` and then
    implementing the logic to download your DBT artifacts from production.
    """

    plugin_config = ctx.obj.plugin_config("dbt")
    artifact_path = plugin_config.dbt_artifacts_prod

    msg = "No-op command! Please override this command in your own project by running: palm override --name prod-artifacts'"

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    # success, msg = ctx.obj.run_in_docker(cmd, env_vars)

    click.secho(msg, fg="red")
