import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars
import sys


@click.command("run")
@click.option(
    "--no-fail-fast",
    is_flag=True,
    help="Turns off --fail-fast. See dbt docs on fail-fast flag.",
)
@click.option("--clean", is_flag=True, help="Drop the test schema after the run")
@click.option("--models", "-m", multiple=True, help="See dbt docs on models flag")
@click.option("--select", "-s", multiple=True, help="See dbt docs on select flag")
@click.option("--exclude", "-e", multiple=True, help="See dbt docs on exclude flag")
@click.option("--defer", is_flag=True, help="See dbt docs on defer flag")
@click.option("--iterative", is_flag=True, help="Iterative stateful dbt run")
@click.option(
    "--full-refresh",
    is_flag=True,
    help="Will perform a full refresh on incremental models",
)
@click.option("--no-seed", is_flag=True, help="Will skip seed full refresh")
@click.pass_obj
def cli(
    environment,
    no_fail_fast: bool,
    clean: bool,
    full_refresh: bool,
    iterative: bool,
    defer: bool,
    no_seed: bool,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
    vars: Optional[str] = None,
):
    """Runs the DBT repo."""
    stateful = iterative or defer

    if defer:
        click.secho("Running 'palm prod-artifacts'...", fg='yellow')
        exit_code, _, _ = environment.run_on_host("palm prod-artifacts")
        if exit_code == 2:
            click.secho(
                "'palm prod-artifacts' not implemented. Can't use --defer without it!",
                fg='red',
            )
            sys.exit(1)
        elif exit_code != 0:
            click.secho(
                "Something went wrong while pulling the prod artifacts.", fg='red'
            )
            sys.exit(1)

    env_vars = set_env_vars(environment, stateful, defer)

    # --select and --models are interchangeable on dbt >= v1, combine the lists of selections
    targets = list(set(models + select))

    run_cmd = build_run_command(
        # Is there a better way to pass these args in?
        full_refresh=full_refresh,
        no_seed=(no_seed or defer),
        no_fail_fast=(no_fail_fast or iterative),
        targets=targets,
        exclude=exclude,
        defer=defer,
        vars=vars,
    )

    success, msg = environment.run_in_docker(run_cmd, env_vars)

    if iterative:
        while not success:
            click.secho("dbt run had some issues. Fix, then hit continue.", fg="yellow")
            cycle = click.confirm("Continue?", show_default=True)

            if not cycle:
                break

            env_vars = set_env_vars(environment, stateful)
            stateful_run_cmd = build_run_command(
                targets=["result:error", "result:skipped"],
                no_seed=iterative,
                no_fail_fast=iterative,
            )
            success, msg = environment.run_in_docker(stateful_run_cmd, env_vars)

    click.secho(msg, fg="green" if success else "red")

    if clean:
        success, msg = environment.run_in_docker(
            "dbt run-operation drop_branch_schemas && dbt clean", env_vars
        )
        click.secho(msg, fg="green" if success else "red")


def build_run_command(
    full_refresh: bool = False,
    no_seed: bool = True,
    no_fail_fast: bool = False,
    targets: Optional[list] = None,
    exclude: Optional[Tuple] = None,
    defer: bool = False,
    vars: Optional[str] = None,
) -> str:
    cmd = []
    full_refresh_option = " --full-refresh" if full_refresh else ""

    if not no_seed:
        cmd.append(f"dbt seed{full_refresh_option}")
        cmd.append("&&")

    cmd.append(f"dbt run{full_refresh_option}")
    if targets:
        cmd.append("--select")
        cmd.extend(targets)
    if exclude:
        cmd.append("--exclude")
        cmd.extend(exclude)
    if not no_fail_fast:
        cmd.append("--fail-fast")
    if defer:
        if not targets:
            cmd.extend(["--select", "state:new", "state:modified+"])
        cmd.append("--defer")
    if vars:
        cmd.append(f"--vars '{vars}'")

    return " ".join(cmd)


def set_env_vars(environment, stateful: bool, defer: bool = False) -> dict:
    plugin_config = environment.plugin_config('dbt')
    env_vars = dbt_env_vars(environment.palm.branch)
    if stateful:
        env_vars['DBT_DEFER_TO_STATE'] = 'true'
    if defer:
        env_vars['DBT_ARTIFACT_STATE_PATH'] = plugin_config.dbt_artifacts_prod
    else:
        env_vars['DBT_ARTIFACT_STATE_PATH'] = plugin_config.dbt_artifacts_local
    return env_vars
