# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [0.5.0] - 2023-03-16

### Added

- Automated release to pypi via GH actions
- Support for containerizing dbt projects with dbt v1+

### Fixed

- Validation of plugin config where prod manifest is not used
- Default dbt run options do not include stateful selection unless --defer is used.
- Support for Pyyaml v6 (removed upper version pin)

## [0.4.0] - 2022-12-09

### Added

- Interactive column doc descriptions when generating a model-doc
- New dbt passthrough command. Running `palm dbt <command>` allows users to run
  bespoke or complex dbt commands without having to use `palm shell` for all those
  poweruser commands!
- PluginConfig - the plugin is now configurable, currently this is used to store
  the path for local and production assets, enabling another new feature.
  **note: this change requires palm v2.5.1 or higher**
- Added a no-op command for downloading artifacts.
  **note** to use `--defer` mode, you will need to override this function in your
  repo and implement the necessary logic to download production artifacts from
  your cloud provider.

### Changed

- run & test commands simplified and improved!

  - Persist by default, no need to specify `--persist` on every run!
  - New `run defer` modes allow you to move more quickly, no need to explicitly select
  the model you've been working on!
  - New `run iterative` mode allows you to iterate over failures in your models
  quickly, without exiting and re-running the same command over-and-over.
  - Re-wrote some legacy code that made these operations more complicated than necessary.

### Fixed

- Update model-doc command to populate existing columns when a docs_path config is present

## [0.3.1] - 2022-09-21

### Changed

- **model-doc command**: now supports advanced dbt project structures, parsese
the dbt_project and includes CLI prompts to ensure model doc is created in the
appropriate directory.
- **dbt test no longer runs seed**: palm test no longer runs seeds before
executing tests. This was a strange decision and didn't really make any sense,
caused slower dev/test cycles and added no value.

## [0.3.0] - 2022-10-05

### Added

- **model-doc**: New command to auto-generate docs for a new model!
Palm can now generate .yml and .md files based on the SQL in your model,
to use palm model-doc run `palm model-doc models/path/to/model.sql` in your
dbt project!

## [0.2.0] - 2022-01-05

### Added

- **dbt deps**: palm-dbt now assumes dbt deps are installed when the docker image is built.
Projects containerized by palm-dbt will be set up with this functionality, other projects
may need to adjust their Dockerfile to RUN dbt deps and implement the volume mount
in their docker-compose.yaml. See README for full details.

### Changed

- **pin version of black**: The version of black used to lint this project has been
pinned to ensure the local version matches the version used in CI

## [0.1.2] -2021-12-03

### Added

- **Containerize**: There is an explicit prompt to enter the dbt version number when containerizing a dbt project. Issue #34

### Changed

- **General**: Improved testing, documentation, CI, issue templates, and linting.

### Fixed

- **Bug Fixes**: Removed profiles.yml reference in Dockerfile template. Palm-dbt detects profiles.yml automatically.


## [0.1.1] - 2021-12-02

### Fixed

- Type hints were causing containerize to fail in python 3.8 and below. Issue #30

## [0.1.0] - 2021-12-01

The plugin officially supports dbt back TWO minor versions (this will march forward), currently supporting back through v0.19.

### Added

- **Containerize**: NEW command for containerizing dbt, `containerize`, has been implemented!
- **Shell**: NEW command to shell into the project container and execute arbitrary commands (run dbt directly!)
- **Version validation**: Added version detection and validation of supported dbt versions in a dbt project.
- **Issue templates**: Issue templates have been enabled for the repository!

### Changed

- **General**: Removed hard-coded path names referring to Palmetto's own dbt project information and generalized pathing for code generation output.
- **PEP8**: Ran linting on the whole project.

### Fixed

- Fixed the enumeration of objects passed into the `--select` and `--models` flags when passed to dbt.

## [0.0.4] - 2021-11-22

### Fixed

- The palmcli package is being renamed to palm, updated dependency naming for
compatibility

## [0.0.3] - 2021-11-17

### Fixed

- Palm snapshot is missing dbt deps
