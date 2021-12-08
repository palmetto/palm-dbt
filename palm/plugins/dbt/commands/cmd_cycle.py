import click
from typing import Optional, Tuple
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars

# TODO: Refactor this command to reduce branching logic and simply join a list of
# commands once, before running. Also use f-strings instead of concat


@click.command("cycle")
@click.argument("count", type=int, default=2)
@click.option(
    "--persist", is_flag=True, help="will not drop the test schema at the end"
)
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--no-seed", is_flag=True, help="will skip seed full refresh")
@click.pass_context
def cli(
    ctx,
    count: int,
    persist: bool,
    no_seed: bool,
    models: Optional[Tuple] = tuple(),
    select: Optional[Tuple] = tuple(),
):
    """Consecutive run-test of the DBT repo. `count` is the number of run/test cycles to execute, defaults to 2"""

    def add_models(command: str) -> str:
        if models:
            command += " --models " + " ".join(models)
        return command

    def add_select(command: str) -> str:
        if select:
            command += " --select " + " ".join(select)
        return command

    def run_test():
        return " && ".join(
            (
                add_models("dbt run"),
                add_models("dbt test"),
            )
            * count
        )

    def make_cmd():
        commands = []
        if not no_seed:
            seed_cmd = "dbt seed --full-refresh"
            commands.append(add_select(seed_cmd))

        commands.append(run_test())

        if not persist:
            commands.append("dbt run-operation drop_branch_schemas")

        return " && ".join(list(filter(None, commands)))

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    cmd = make_cmd()
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
