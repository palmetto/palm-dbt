# Palm dbt Changelog

## 0.0.5

> 12/01/2021

The plugin officially supports dbt back TWO minor versions (this will march forward), currently supporting back through v0.19.

Features:
- **Containerize**: NEW command for containerizing dbt, `containerize`, has been implemented!
- **Shell**: NEW command to shell into the project container and execute arbitrary commands (run dbt directly!)
- **Version validation**: Added version detection and validation of supported dbt versions in a dbt project.

Improvements:
- **Bug fixes**: Fixed the enumeration of objects passed into the `--select` and `--models` flags when passed to dbt.
- **Issue templates**: Issue templates have been enabled for the repository!
- **General**: Removed hard-coded path names referring to Palmetto's own dbt project information and generalized pathing for code generation output.
- **PEP8**: Ran linting on the whole project.


## 0.0.4

> 11/22/2021

- The palmcli package is being renamed to palm, updated dependency naming for
compatibility

## 0.0.3

> 11/17/2021

- [BUG]: Palm snapshot is missing dbt deps
