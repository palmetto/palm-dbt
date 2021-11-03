import click
from typing import Optional
from palm.plugins.dbt.dbt_palm_utils import dbt_env_vars

# TODO: Refactor this command to reduce branching logic and simply join a list of
# commands once, before running. Also use f-strings instead of concat

@click.command("cycle")
@click.argument("count", type=int, default=2)
@click.option("--fast", is_flag=True, help="will skip clean/deps/seed")
@click.option("--persist", is_flag=True, help="will not drop the test schema at the end")
@click.option("--models", multiple=True, help="see dbt docs on models flag")
@click.option("--select", multiple=True, help="see dbt docs on select flag")
@click.option("--no-seed", is_flag=True, help="will skip seed full refresh")
@click.pass_context
def cli(ctx,
        count:int,
        fast: bool,
        persist: bool,
        no_seed: bool,
        models: Optional[tuple] = tuple(),
        select: Optional[tuple] = tuple()):
    """ Consecutive run-test of the DBT repo. `count` is the number of run/test cycles to execute, defaults to 2
    """
    def add_models(command:str)->str:
        if models:
            command += " --models " + " ".join(models)
        return command

    def add_select(command:str)->str:
        if select:
            command += " --select " + " ".join(select)
        return command

    def add_persist()->str:
        if not persist:
            return " dbt run-operation drop_branch_schemas"
        return " true "

    def run_test():

        return (" && ".join(
                    (add_models("dbt run"), add_models("dbt test"),) * count
                    ) )

    def make_cmd():
        if fast:
            if no_seed:
                seed_cmd = ""
            else:
                seed_cmd = "dbt seed --full-refresh"
            commands = [add_select(seed_cmd),
                        run_test(),
                        add_persist()]
        else:
            if no_seed:
                seed_cmd = ""
            else:
                seed_cmd = " && dbt seed --full-refresh "
            commands = [add_select("dbt clean && dbt deps" + seed_cmd),
                        run_test(),
                        add_persist()]
        return " && ".join(list(filter(None, commands)))

    env_vars = dbt_env_vars(ctx.obj.palm.branch)
    cmd = make_cmd()
    success, msg = ctx.obj.run_in_docker(cmd, env_vars)
    click.secho(msg, fg="green" if success else "red")
