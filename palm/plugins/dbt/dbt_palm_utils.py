import re
from typing import Dict
from palm.plugins.dbt.local_user_lookup import local_user_lookup

""" Shared DBT utilities to build out common CLI options """


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
