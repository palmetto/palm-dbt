# Palm dbt

dbt plugin for [Palm CLI](https://github.com/palmetto/palm-cli)

This plugin adds dbt-specific commands for use with Palm CLI

## Installing

Install this plugin along with palm

`pip install palm-dbt`

Or from source

`python3 -m pip install .`

### Configuring your project

To configure your project to use the palm-dbt plugin, you will need a `.palm/config.yaml`
this can be created by running `palm init`, once you have your config file,
add the dbt-palm plugin with the following configuration:

```yaml
plugins:
  - dbt
```

## Palm-ing an existing dbt project
palm-dbt ships with a command to containerize and convert your existing dbt project.

For example, if you wanted to containerize your existing dbt project running on 0.21.0, you would run:
```
  palm containerize --version 0.21.0
```

### Adding palm dbt macros

palm-dbt uses the git branch name to set the schema for all commands via env vars.
This allows palm to clean up test data after each run, ensuring that your data 
warehouse stays clean and free of development/test data.

To enable this functionality, palm-dbt ships with 2 macros that handle schema naming
and cleanup:

* generate_schema_name - **This macro overrides the dbt-core macro** to auto-generate 
a schema name based on your current git branch and PALM_DBT_ENV.

* drop_branch_schemas - This macro uses the branch named schema and the TEST database
to clean up any models generated by running dbt in development or test environments.
Calls to this macro are baked in to many of the palm dbt commands.

See the section [about the palm dbt naming macros](#about-the-palm-dbt-branch-naming-macros) 
below for more information.


To install these macros, run `palm install` from within a project that is configured
to use the palm-dbt plugin.

### Recommended (optional) protected branch configuration

In order to ensure your runs are idempotent, we recommend that you do not run 
palm-dbt commands against `main`, `master` or any other production-like branches
you may be using.

To prevent palm running against specific branches, add the following config to
your project's `.palm/config.yaml`

```yaml
protected_branches:
  - main
  - master
  # Any other branches you want to protect
```

## About the palm dbt branch naming macros

One of the most painful parts of data testing is unfortunate 
[shared mutable state](https://stackoverflow.com/questions/44219903/why-is-shared-mutability-bad). 
palm-dbt provides a mechanism to eliminate this undesirable situation by namespacing 
each run of dbt. for git branches other than main or master, palm will prefix the 
calculated schema name with a formatted version of your branch name. In CI, this 
will be additionally prefixed with "CI". For example: 

- you open a branch FEATURE/DATA-100/update-widget
- when you `palm run` in your local env, the schema `public` will be built as 
`feature_data_100_update_widget_public`. The schema `sales` will be built as 
`feature_data_100_update_widget_sales`. 
- in CI the schemas will be `ci_feature_data_100_update_widget_public`, 
`ci_feature_data_100_update_widget_sales` (respectively). 
- in prod the schemas will be 'public' and 'sales' (respectively). 

Refs will automatically update as well. This way, you can use a single test 
database and not worry about conflicts between developers, or between branches 
for the same developer (like during hotfixes). 

## Typical palm-dbt workflow

From a non-protected branch, running `palm run` will:
1. drop (if it exists) the namespaced schema in development
2. create the namespaced schema in development
3. clean, deps, seed and run
4. drop the namespaced schema in development

Why drop it? so your testing is atomic. 

Want to persist it? use the flag `--persist`
