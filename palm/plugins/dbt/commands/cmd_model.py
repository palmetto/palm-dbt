import click
import re
from pathlib import Path

valid_model_types = ['tmp', 'staging', 'intermediate', 'dim', 'fact']

@click.group()
def cli():
  """ DBT model tools """
  pass

@cli.command('new')
@click.pass_context
@click.option("--name", multiple=False, required=True, help="Name of the model you are creating. Don't add 'dim_' or 'fact_' we do that for you!")
@click.option("--model-type", multiple=False, default='dim', help="staging, intermediate, fact, dim - default is dim")
@click.option("--use-ref-file", is_flag=True, help="Parses .palm/model_template/ref_files/ref_file.sql into .sql and .yml templates")
def new(ctx, name: str, model_type: str, use_ref_file: bool):
    """ Generate a new model """
    click.echo(f'Generating your new {name} {model_type}!')

    if model_type not in valid_model_types:
        click.secho(f'Invalid model type. Valid model types are: {", ".join(valid_model_types)}', fg='red')
        return

    model_name = get_model_name(name, model_type)

    sql_to_dbt = ctx.obj.import_module('sql_to_dbt', Path(Path.cwd(),'.palm','sql_to_dbt.py'))


    if use_ref_file:
        ref_file = sql_to_dbt.get_ref_file()
        # Check that ref file has been updated
        if re.match('^[<].*[>]$', ref_file):
            click.secho("Ref file not updated, please add your source SQL and re-run the command", fg="red")
            return

    create_model(model_name, model_type, ctx, use_ref_file)
    create_docs(model_name, model_type, ctx, use_ref_file)

    if use_ref_file:
        ctx.obj.run_in_shell(f"dbt run --models @{model_name} --fail-fast")


def create_model(model_name, model_type, ctx, use_ref_file):

    sql_to_dbt = ctx.obj.import_module('sql_to_dbt', Path(Path.cwd(),'.palm','sql_to_dbt.py'))

    model_template_path = Path('.palm', 'model_template', 'model')
    models_path = Path('models/arbor/', model_type)

    replacements = {
        'model_name': model_name
        , 'model_description': f"'{{{{ doc(\"{model_name}\") }}}}'"
        , 'ref': "{{ ref('staging_table') }}"
        , 'model_columns': f"""\n      - name: _sk\n        description: The unique id for {model_name}\n        tests:\n          - not_null"""
    }

    if use_ref_file:
        replacements['model_columns'] = sql_to_dbt.sql_to_yml()

    result = ctx.obj.generate(model_template_path, models_path, replacements)
    click.echo(result)

    if use_ref_file:
        sql_to_dbt.create_dbt_sql_file(model_name, model_type)


def create_docs(model_name, model_type, ctx, use_ref_file):

    sql_to_dbt = ctx.obj.import_module('sql_to_dbt', Path(Path.cwd(),'.palm','sql_to_dbt.py'))

    docs_template_path = Path('.palm', 'model_template', 'docs')
    docs_path = Path('models/arbor/documentation/models/', model_type)

    replacements = {
        'model_name': model_name
        , 'begin_docs': f"{{% docs {model_name} %}}"
        , 'end_docs': "{% enddocs %}"
        , 'model_notes': "## Business Notes\n\n\t## Developer Notes"
    }

    if use_ref_file:
        replacements['model_notes'] = sql_to_dbt.sql_to_md()

    result = ctx.obj.generate(docs_template_path, docs_path, replacements)

    click.echo(result)
    

def get_model_name(name, model_type):
    if model_type == 'dim':
        return f"dim_{name}"
    if model_type == 'fact':
        return f"fact_{name}"
    if model_type == 'tmp':
        return f"tmp_{name}"
    return name
