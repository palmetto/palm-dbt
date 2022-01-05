import re
from typing import Optional, Dict, Tuple
from palm.plugins.dbt.local_user_lookup import local_user_lookup

""" Shared DBT utilities to build out common CLI options """


def shell_options(command_name: str, **kwargs):
    # pop off unused kwargs caused by use of importlib in palm
    kwargs.pop("ctx")

    return _cycle(command_name, **kwargs)


def _cycle(
    cmd: str,
    persist: Optional[bool] = False,
    no_fail_fast: Optional[bool] = False,
    full_refresh: Optional[bool] = False,
    no_seed: Optional[bool] = False,
    select: Optional[Tuple] = (),
    models: Optional[Tuple] = (),
    macros: Optional[Tuple] = (),
) -> str:
    command = []
    if not no_seed:
        command.append("dbt seed --full-refresh")

    if macros:
        command.append(f'dbt run-operation + {"&& dbt run-operation".join(macros)}')
    else:
        subcommand = f"dbt {cmd}"
        if select and not no_seed:
            subcommand += " --select " + " ".join(select)
        if models:
            subcommand += " --models " + " ".join(models)
        if full_refresh:
            subcommand += " --full-refresh"
        if not no_fail_fast:
            subcommand += " --fail-fast"
        command.append(subcommand)

    if not persist:
        command.append("dbt run-operation drop_branch_schemas")

    return ' && '.join(command)


def dbt_env_vars(branch: str) -> Dict:
    return {
        'PDP_DEV_SCHEMA': _generate_schema_from_branch(branch),
        'PDP_ENV': 'DEVELOPMENT',  # Deprecated - this will be removed!
        'PALM_DBT_ENV': 'DEVELOPMENT',
    }


def _generate_schema_from_branch(branch: str) -> str:
    """Formats the branch name as a schema."""
    user = local_user_lookup()
    return re.sub(r"[^0-9a-zA-Z]+", "_", f"{user}_{branch}").strip("_").lower()
