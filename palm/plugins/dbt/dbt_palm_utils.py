import re
from typing import Optional
from palm.plugins.dbt.local_user_lookup import local_user_lookup

""" Shared DBT utilities to build out common CLI options """

def shell_options(command_name: str, **kwargs):
    # pop off unused kwargs caused by use of importlib in palm
    kwargs.pop("ctx")

    if kwargs["fast"]:
        for k in ("fast", "select"):
            kwargs.pop(k, None)
        return _short_cycle(command_name, **kwargs)
        return
    kwargs.pop("fast")
    return _long_cycle(command_name, **kwargs)


def _short_cycle(cmd: str,
                persist: Optional[bool] = False,
                no_fail_fast: Optional[bool] = False,
                full_refresh: Optional[bool] = False,
                no_seed: Optional[bool] = False,
                models: Optional[tuple] = (),
                macros: Optional[tuple] = ()) -> str:

    command = "" if no_seed else f" dbt seed --full-refresh && "

    if macros:
        command += f"dbt run-operation {macros}"
    else:
        command += f"dbt {cmd}"
        if models:
            command += " --models " + " ".join(models)
        if full_refresh:
            command += " --full-refresh"
        if not no_fail_fast:
            command += " --fail-fast"

    if not persist:
        command += " && dbt run-operation drop_branch_schemas"

    return command

def _long_cycle(cmd: str,
                persist: Optional[bool] = False,
                no_fail_fast: Optional[bool] = False,
                full_refresh: Optional[bool] = False,
                no_seed: Optional[bool] = False,
                select: Optional[tuple] = (),
                models: Optional[tuple] = (),
                macros: Optional[tuple] = ()) -> str:
    seed_cmd = "" if no_seed else "&& dbt seed --full-refresh"
    command = f"dbt clean && dbt deps {seed_cmd}" 

    if macros:
        run_operation = " && dbt run-operation "
        command += run_operation + run_operation.join(macros)
    else:
        command += f" && dbt {cmd}"
        if select and not no_seed:
            command += " --select " + " ".join(select)
        if models:
            command += " --models " + " ".join(models)
        if full_refresh:
            command += " --full-refresh"
        if not no_fail_fast:
            command += " --fail-fast"

    if not persist:
        command += " && dbt run-operation drop_branch_schemas"

    return command

def dbt_env_vars(branch: str) -> dict:
    return {
        'PDP_DEV_SCHEMA': _generate_schema_from_branch(branch),
        'PDP_ENV': 'DEVELOPMENT', # Deprecated - this will be removed!
        'PALM_DBT_ENV': 'DEVELOPMENT',
    }


def _generate_schema_from_branch(branch: str) -> str:
    """ Formats the branch name as a schema."""
    user = local_user_lookup()
    return re.sub(r"[^0-9a-zA-Z]+", "_", f"{user}_{branch}").strip("_").lower()
