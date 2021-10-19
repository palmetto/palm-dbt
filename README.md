# Palm dbt

dbt plugin for Palm CLI

This plugin adds dbt-specific commands for use with Palm CLI

## Using this plugin

Install this plugin along with palm

`pip install palm-dbt`

Or from source

`python3 -m pip install .`

Configure your project to use the palm-dbt plugin, in `.palm/config.yaml`

```yaml
plugins:
  - dbt
```