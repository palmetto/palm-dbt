/*{# Cleans out all models generated for the current development schema 

    Only runs against the TEST database, will only work correctly when used in
    conjunction with the generate_schema_name macro

#}*/

{%- macro drop_branch_schemas() -%}
    {%- if target.database != "TEST" -%}
          {{ exceptions.raise_compiler_error("Branch cleanup can only execute in TEST database; currently pointed at " ~ target.database) }}
    {%- endif -%}

    {%- set branch_query -%}
        SHOW TERSE SCHEMAS IN DATABASE TEST;
        SELECT 'DROP SCHEMA TEST.' || "name" as drop_query FROM TABLE(RESULT_SCAN (LAST_QUERY_ID())) WHERE "name" LIKE UPPER('{{generate_schema_name()}}%')
    {%- endset -%}

    {% do log('getting schemas to drop with query ' ~ branch_query, info=True) %}
    {%- set drop_commands = run_query(branch_query).columns[0].values() -%}
    {% if drop_commands %}
        {% for drop_command in drop_commands %}
            {% do log('executing query ' ~ drop_command, True) %}
            {% do run_query(drop_command) %}
        {% endfor %}
    {% else %}
        {% do log('No schemas matching '~ generate_schema_name() ~' to clean.', True) %}
    {% endif %}

{%- endmacro -%}
