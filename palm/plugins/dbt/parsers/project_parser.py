class Project:
    """Project parser model"""

    def __init__(self, **data):
        self.name = data['name']
        self.version = data['version']
        self.profile = data['profile']
        self.config_version = data['config-version']
        self.model_paths = data.get('model-paths', 'models')
        self.macro_paths = data.get('macro-paths', 'macros')
        self.seed_paths = data.get('seed-paths', 'seeds')
        self.snapshot_paths = data.get('snapshot-paths', 'snapshots')
        self.analysis_paths = data.get('analysis-paths', 'analysis')
        self.test_paths = data.get('test-paths', 'tests')
        self.packages_install_path = data.get('packages-install-path', 'packages')
        # Supports dbt < 1.0.0 - this will be removed in an upcoming release
        self.modules_path = data.get('modules-path', 'dbt_modules')
        self.docs_paths = data.get('docs-paths', [])
        self.vars = data.get('vars', {})
        self.seeds = data.get('seeds', {})
        self.models = data.get('models', {})
        self.snapshots = data.get('snapshots', {})
