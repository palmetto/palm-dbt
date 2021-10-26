
/*{# Monkeypatched branch-specific schema generation.       
     Supports branch-specific dev, CI, and prod configurations.

    Requires the PALM_DBT_ENV environment variable be set to either DEVELOPMENT || CI || PROD

#}*/
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set env = env_var("PALM_DBT_ENV", var("PALM_DBT_ENV", "ENV_NOT_SET")) -%}
    {%- set branch_schema = env_var("PDP_DEV_SCHEMA", "SCHEMA_NOT_SET") -%}
    
    {%- if env == "DEVELOPMENT" -%}
       {{ _assemble_schema( branch_schema, custom_schema_name, true) }}

    {%- elif env == "CI" -%}
       {{ _assemble_schema( "ci_" ~ branch_schema, custom_schema_name, true) }}
    
    {%- elif env == "PROD" -%}
        {{ _assemble_schema( target.schema, custom_schema_name, false) }}

    {%- else -%}
         {{ exceptions.raise_compiler_error("Invalid environment!") }}
    {%- endif -%}

{%- endmacro %}


/*{# the dirty work of assembling the schema name #}*/
{% macro _assemble_schema(default_schema, 
                          custom_schema_name, 
                          should_concat=true) %}
    {%- if custom_schema_name is none -%}

        {{ default_schema }}

    {%- elif should_concat -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}

{% endmacro %}