import re
import click
from typing import Tuple
from shutil import copy
from pathlib import Path
from functools import lru_cache


def create_dbt_sql_file(model_name: str, models_path: Path) -> None:
    """Writes dbt-style code to the model.sql based on SQL provided in the reference file

    Args:
        model_name (str): Name of the model
        model_type (str): Type of the model
    """

    replacements = get_replacements()

    output_file = models_path / model_name / f'{model_name}.sql'

    filedata = get_ref_file()

    filedata = re.sub('"', "", filedata, flags=re.IGNORECASE)

    for pat, repl in replacements:
        filedata = re.sub(pat, repl, filedata, flags=re.IGNORECASE)

    filedata = re.sub('join .*\.([a-z_\.]*)', lower_repl, filedata, flags=re.IGNORECASE)

    with open(output_file, 'w') as file:
        file.write(filedata)
        file.close()

    click.echo(f"Updated datasources in {output_file}'s sql file!")


def sql_to_yml() -> str:
    """Generates column documentation for the model based on ref file SQL notes

    Returns:
        str: Formatted description for each column in the provided SQL
    """
    filedata = get_ref_file()
    results = ''

    select_columns = re.sub(
        '(?s:.*)select\W*distinct\W|[ ]{0,}from[\W.\w]{1,}',
        '',
        filedata,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    select_columns = [
        "".join(tuples).lower()
        for tuples in re.findall(
            '([a-z\_]{1,} -- .*)|([a-z\_]{1,}[ ]{0,}$)',
            select_columns,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    ]

    columns = []

    for col in select_columns:
        columns.append(re.split('[ ]{0,}--[ ]{0,}', col))

    for value in columns:

        name = value[0]

        try:
            description = value[1]
        except IndexError:
            description = 'TBD'

        formatted = (
            "\n      - name: " + name + "\n        description: " + description + "\n"
        )

        results = results + formatted

    return results


def sql_to_md() -> str:
    """Pull the top comment from the ref file to inject into the model_notes md

    Returns:
        str: Content for model docs yml
    """
    filedata = get_ref_file()

    model_notes_present = (
        len(re.findall('\/\*\D([\D]*)\*\/([\D\d]*)', filedata, flags=re.MULTILINE)) > 0
    )

    if model_notes_present:
        results = re.sub(
            '\/\*\D([\D]*)\*\/([\D\d]*)', r'\1', filedata, flags=re.MULTILINE
        )
        results = re.sub('(?!\A)^', ' ' * 4, results, flags=re.MULTILINE)
        return results

    return "## Business Notes\n\n\t## Developer Notes"


@lru_cache(maxsize=1)
def get_ref_file() -> str:
    """Read the ref file, cached to reduce amount of times we need to read the file into memory

    Returns:
        str: ref file contents
    """
    ref_file_path = Path.cwd() / '.palm/model_template/ref_files/ref_file.sql'
    if not ref_file_path.exists():
        return ''
    contents = ref_file_path.read_text()
    return contents


def create_ref_files():
    ref_file_templates = Path(__file__).parent / 'model_template/ref_files'
    ref_file_dir = Path.cwd() / '.palm/model_template/ref_files'
    ref_file_dir.mkdir(parents=True, exist_ok=True)
    files = ['ref_file.sql', 'ref_file_readme.md']
    breakpoint
    for file in files:
        copy(ref_file_templates / file, ref_file_dir / file)
    click.secho(
        "Ref files created! Update the ref file and re-run the command to generate your model",
        fg="green",
    )


## helper functions


def get_replacements() -> list:
    """Get list of replacements

    Returns:
        list: list of replacements
    """

    replacements = []
    directory = Path.cwd() / 'source_systems'

    for file in directory.glob('*.yml'):
        replacement_for_file = get_replacements_for_file(file)
        if replacement_for_file:
            replacements.append(replacement_for_file)

    return replacements


def get_replacements_for_file(file: Path) -> Tuple:
    """Extracts the dbt naming conventions from a given file

    Args:
        file ([Path]): Path to a .yml file in sourcE_systems directory

    Returns:
        tuple: path, dbt_path
    """

    with open(file, 'r') as fd:
        sqlFile = fd.read()
        fd.close()

    try:
        src_and_tables = return_regex('src_and_tables', sqlFile)
        database = return_regex('database', sqlFile)[0]
        schema = return_regex('schema', sqlFile)[0]
    except AttributeError:
        print(AttributeError)

    src = src_and_tables[0]

    paths = [database + '.' + schema + '.' + path for path in src_and_tables[1:]]

    for path in paths:
        dbt_path = "{{ source('" + src + "', '" + path.split('.')[2] + "') }}"
        return (path, dbt_path)


def return_regex(typ, txt):

    regex_dict = {
        'src_and_tables': re.compile(
            "- name[: ]{0,3}(.*\_{0,}.*)\n", flags=re.IGNORECASE | re.MULTILINE
        ),
        'database': re.compile(
            "database[: ]{0,3}(.*\_{0,}.*)\n", flags=re.IGNORECASE | re.MULTILINE
        ),
        'schema': re.compile(
            "schema[: ]{0,3}(.*\_{0,}.*)\n", flags=re.IGNORECASE | re.MULTILINE
        ),
    }

    regexp = regex_dict[typ]

    results = regexp.findall(txt)

    results = [result.lower() for result in results]

    if len(results) == 0:
        results.append('ref_only')

    return results


def lower_repl(match):
    return "JOIN {{ ref('" + match.group(1).lower() + "') }}"
