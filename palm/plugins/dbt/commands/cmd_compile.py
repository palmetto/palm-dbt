import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars


@click.command("compile")
@click.option("--models", "-m", multiple=True, help="See dbt docs on models flag")
@click.option("--select", "-s", multiple=True, help="See dbt docs on select flag")
@click.option("--exclude", "-e", multiple=True, help="See dbt docs on exclude flag")
@click.pass_obj
def cli(
    environment,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
    exclude: Optional[Tuple] = tuple(),
):
    """Compiles the dbt repo"""
    env_vars = dbt_env_vars(environment.palm.branch)

    # --select and --models are interchangeable on dbt >= v1, combine the lists of selections
    targets = list(set(models + select))

    cmd = ["dbt compile"]
    if targets:
        cmd.append("--select")
        cmd.extend(targets)
    if exclude:
        cmd.append('--exclude')
        cmd.extend(exclude)
    
    success, msg = environment.run_in_docker(" ".join(cmd), env_vars)
    click.secho(msg, fg="green" if success else "red")
