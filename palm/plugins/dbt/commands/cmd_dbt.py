from email.policy import default
from unittest.result import failfast
import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("dbt")
@click.option("--select", '-s', multiple=True, help="Specify the nodes to include.")
@click.option("--exclude", '-e', multiple=True, help="Specify the nodes to exclude.")
@click.option(
    "--selector", help="Specify the selector to use, defined in selectors.yml."
)
@click.option(
    '--fail-fast',
    '-x',
    is_flag=True,
    default=False,
    help='Stop execution upon a first failure',
)
@click.option(
    "--full-refresh", is_flag=True, default=False, help="Specify the nodes to exclude."
)
@click.option(
    "--cleanup",
    is_flag=True,
    default=False,
    help="Drop the schema after running the command.",
)
@click.option(
    '--seed',
    is_flag=True,
    default=False,
    help='Create seeds before running the command.',
)
@click.option(
    "--options",
    '-o',
    help="passthrough for a string of dbt options - useful if an option you need is not available in palm",
)
@click.argument("args", nargs=-1)
@click.pass_context
def cli(
    ctx,
    select: Optional[str],
    exclude: Optional[str],
    selector: Optional[str],
    fail_fast: bool,
    full_refresh: bool,
    seed: bool,
    cleanup: bool,
    options,
    args: Tuple,
):
    """Pass through dbt commands to the container.

    This command allows you to run any dbt command in the Docker container.

    The most frequently used dbt options are available as options to this command.
    For any other options, you can use the --options flag to pass through any
    string of options to dbt.

    Example:
    palm dbt run --select my_model --full-refresh
    palm dbt run --options "--select my_model --full-refresh"
    """
    if len(args) == 0:
        click.secho("You must provide a dbt command", fg="red")
        return

    cmd = [f'dbt {" ".join(args)}']

    if seed:
        cmd.insert(0, f"dbt seed --full-refresh &&")
    if select:
        cmd.append(f" --select {' '.join(select)}")
    if exclude:
        cmd.append(f" --exclude {' '.join(exclude)}")
    if selector:
        cmd.append(f" --selector {selector}")
    if fail_fast:
        cmd.append(" --fail-fast")
    if full_refresh:
        cmd.append(f" --full-refresh")
    if options:
        cmd.append(f" {options}")
    if cleanup:
        cmd.append(" && dbt run-operation drop_branch_schemas")

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    success, msg = ctx.obj.run_in_docker(" ".join(cmd), env_vars)
    click.secho(msg, fg="green" if success else "red")
