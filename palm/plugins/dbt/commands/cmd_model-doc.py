import click
import sqlparse
import re
import yaml
from pathlib import Path
from functools import lru_cache
from typing import List

from palm.plugins.dbt.parsers import parse_project


@click.command("model-doc")
@click.argument("model", required=True, type=click.Path(exists=True))
@click.pass_obj
def cli(environment, model):
    """Generates initial baseline model.yml for a given SQL model"""
    model_path = Path(model)
    model_name = model_path.stem
    generate_model_md_file(environment, model_path, model_name)
    generate_yml_file(model_path, model_name)


def generate_model_md_file(environment, model_path: Path, model_name: str) -> Path:
    """Generate the model markdown file

    Args:
        environment (palm.Environment.obj): The Palm environment object
        model_path (Path): The path to the model SQL file
        model_name (str): The name of the model

    Returns:
        Path: The path to the generated model markdown file
    """
    destination = get_md_destination_directory(model_path, model_name)
    click.echo(click.style(f"Generating {model_name}.md in {destination}", fg="green"))

    grain = click.prompt("What is the grain of the model?", type=str)
    description = click.prompt(
        "Please provide a user-facing description for this model", type=str
    )
    replacements = {
        "model_name": model_name,
        "model_name_humanized": model_name.replace("_", " ").title(),
        "grain": grain,
        "description": description,
        "begin_docs": f"{{% docs {model_name} %}}",
        "end_docs": "{% enddocs %}",
    }
    template_dir = Path(Path(__file__).parents[1], "templates") / "model_docs"
    environment.generate(template_dir, destination, replacements)
    return destination / f"{model_name}.md"


def _get_potential_model_doc_directories(model_path: Path) -> List[str]:
    """Infer potential model types from the path of the model

    Args:
        model_path (Path): The path to the model

    Returns:
        List[str]: A list of potential model types
    """
    # TODO: Implement dbt_project.yml parsing to get the docs directory (and other things)
    # This should be read from dbt_project configuration
    project_conf = parse_project()
    model_path_dirs = model_path.parent.parts
    if project_conf.docs_paths:
        model_types = []
        for doc_path in project_conf.docs_paths:
            model_docs_path = Path(doc_path, 'models')
            model_doc_types = {dir.stem for dir in model_docs_path.glob("*")}
            model_type_matches = model_doc_types.intersection(model_path_dirs)
            if model_type_matches:
                model_types.extend(
                    list(map(lambda p: model_docs_path / p, model_type_matches))
                )
        return model_types

    else:
        model_docs_path = Path("models/documentation")
        model_doc_types = {dir.stem for dir in model_docs_path.glob("*")}
        return [
            model_docs_path / model_dir
            for model_dir in model_path_dirs
            if model_dir in model_doc_types
        ]


def get_md_destination_directory(model_path: Path, model_name: str) -> Path:
    """Generate the destination for the models markdown file

    Note that the model must have a parent directory that matches the name of
    and existing group of model docs.
    """
    potential_model_dirs = _get_potential_model_doc_directories(model_path)
    if not potential_model_dirs:
        model_docs_dir = click.prompt(
            "Please enter the directory path for the model doc",
            type=Path,
            default="models/documentation",
        )
    elif len(potential_model_dirs) == 1:
        model_docs_dir = potential_model_dirs[0]
    else:
        model_docs_dir = click.prompt(
            "Multiple directories match the model path. Please enter the directory path for the model doc",
            type=click.Choice(potential_model_dirs),
            default=potential_model_dirs[0],
        )

    if not model_docs_dir:
        click.secho(f"Could not determine directory for {model_name} docs", fg="red")
        raise Exception("Could not determine model type")

    return model_docs_dir


def generate_yml_file(model_path: Path, model_name: str) -> Path:
    """Generate the model yml file"""
    click.echo(click.style(f"Generating {model_name}.yml for {model_name}", fg="green"))
    target_file = model_name + ".yml"
    destination = model_path.parent / target_file
    if destination.exists():
        click.echo(click.style(f"{model_name}.yml already exists", fg="yellow"))
        overwrite = click.confirm("Do you want to overwrite it?", default=False)
        if not overwrite:
            return

    model = {
        "version": 2,
        "models": [
            {
                "name": model_name,
                "description": f'{{{{ doc("{model_name}") }}}}',
                "columns": get_model_columns(model_path),
            }
        ],
    }
    destination.write_text(yaml.dump(model, sort_keys=False, default_flow_style=False))
    click.echo(click.style(f"{model_name}.yml generated at {destination}", fg="green"))
    return destination


def get_model_columns(model_path: Path) -> List[str]:
    """Parse the model SQL file and return a list of columns names

    Args:
        model_path (Path): Path to the model SQL file

    Returns:
        List[str]: List of column names
    """
    raw = Path(model_path).read_text()
    raw = re.sub(
        r"{{[A-Za-z\\n\s()=_,]+}}", "", raw
    ).strip()  # Strip out jinja config blocks
    parsed = sqlparse.parse(raw)

    column_identifiers = []

    for statement in parsed:
        # Unknown is acceptable here because dbt models aren't always proper SQL
        if statement.get_type() in ["SELECT", "UNKNOWN"]:
            column_identifiers = get_column_identifiers(statement)

    column_names = get_column_names(column_identifiers)
    columns = create_column_list(column_names)
    return columns


def get_column_identifiers(
    statement: sqlparse.sql.Statement,
) -> List[sqlparse.sql.Identifier]:
    """Get the column identifiers from a SQL statement"""
    identifiers = []
    for token in statement.tokens:
        if token.ttype is None and type(token) is not sqlparse.sql.Function:
            if type(token) is sqlparse.sql.Identifier:
                # If the token is a CTE, skip it
                if not token_is_cte(token):
                    identifiers.append(token)
            elif type(token) is sqlparse.sql.IdentifierList:
                for child_token in token.get_identifiers():
                    if (
                        child_token.ttype is not sqlparse.tokens.Keyword
                        and not token_is_cte(child_token)
                    ):
                        identifiers.append(child_token)

    if len(identifiers) == 0:
        raise Exception("Could not find column identifiers")
    return identifiers


def token_is_cte(token: sqlparse.sql.Token) -> bool:
    """Check if a given token is a CTE name so we can skip documenting it.

    Args:
        token (sqlparse.sql.Token): The token to check

    Returns:
        bool: True if the token is a CTE name, False otherwise
    """
    _, next_token = token.token_next(1)
    return next_token and next_token.value == "AS"


def get_column_names(column_identifiers: List[sqlparse.sql.Identifier]) -> List[str]:
    """Get the column names from a list of identifiers

    Args:
        column_identifiers (List[sqlparse.sql.Identifier]): List of SQL identifiers

    Returns:
        List[str]: List of column names
    """
    columns = []
    for identifier in column_identifiers:
        columns.append(identifier.get_name())
    return columns


def column_has_existing_doc(column_name: str) -> bool:
    """Check if a column has an existing doc"""
    return column_name in existing_column_docs()


@lru_cache(maxsize=1)
def existing_column_docs() -> List[str]:
    """Get a list of existing column docs

    Cached to prevent globbing the filesystem multiple times

    Returns:
        List[str]: List of existing column doc names
    """
    project_conf = parse_project()
    if project_conf.docs_paths:
        column_docs = []
        for doc_path in project_conf.docs_paths:
            column_docs.extend(Path(doc_path, 'columns').glob('*.md'))
    else:
        column_docs = Path("models/documentation/columns").glob("*.md")

    return [column_doc.stem for column_doc in column_docs]


def create_column_list(column_names: List[str]) -> List[dict]:
    """Create a list of column dictionaries

    Args:
        column_names (List[str]): List of column names

    Returns:
        List[dict]: List of column dictionaries
    """
    columns = []
    columns_without_existing_docs = [
        c for c in column_names if not column_has_existing_doc(c)
    ]

    manual_descriptions = click.confirm(
        f'Do you want to manually enter descriptions for {len(columns_without_existing_docs)} columns?',
        default=False,
    )
    for col_name in column_names:
        description = 'TODO: Add description'
        if column_has_existing_doc(col_name):
            description = f'{{{{ doc("{col_name}") }}}}'
        elif manual_descriptions:
            description = click.prompt(
                f'Description for {col_name}', default=description
            )
            # TODO: Add ability to generate column doc file for manual descriptions

        col_dict = {"name": col_name, "description": description}
        columns.append(col_dict)
    return columns
