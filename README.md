# Palm dbt

dbt plugin for Palm CLI

This plugin adds dbt-specific commands for use with Palm CLI

## Installing

Install this plugin along with palm

`pip install palm-dbt`

Or from source

`python3 -m pip install .`

## Configuring

Configure your project to use the palm-dbt plugin, in `.palm/config.yaml`

```yaml
plugins:
  - dbt
```

### Recommended (optional) protected branch configuration

palm-dbt uses the git branch name to set the schema for all commands via env vars.
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

## The (DBT) Flow

From a non-protected branch, running `palm run` will:
1. drop (if it exists) the namespaced schema in development
2. create the namespaced schema in development
3. clean, deps, seed and run
4. drop the namespaced schema in development

Why drop it? so your testing is atomic. 

Want to persist it? use the flag `--persist`
