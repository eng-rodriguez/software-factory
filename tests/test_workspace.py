"""Behavioral hook tests; requires git, bash, jq and mikefarah/yq v4."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/factory/hooks/scripts'


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='factory workspace ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.api = self.repo('api')
        self.web = self.repo('web')

    def run_cmd(self, args, cwd=None, data=None, env=None):
        return subprocess.run(args, cwd=cwd or self.root, input=data, text=True,
                              capture_output=True, env=env)

    def repo(self, name):
        repo = self.root / name
        repo.mkdir()
        for args in [ ['init', '-q'], ['-c', 'user.name=Test', '-c',
                     'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'initial'] ]:
            result = self.run_cmd(['git', *args], repo)
            self.assertEqual(result.returncode, 0, result.stderr)
        return repo

    def workspace(self):
        config = self.root / '.factory/projects'
        config.mkdir(parents=True)
        (self.root / '.factory/workspace.yml').write_text(
            'version: 1\nmode: workspace\nprojects:\n  api: {path: api}\n  web: {path: web}\n')
        for name in ['api', 'web']:
            (config / f'{name}.yml').write_text('default_branch: develop\nareas: {}\n')

    def context(self, cwd):
        return self.run_cmd(['bash', '-c',
            'source "$1/lib.sh" || exit $?; printf "%s\\n" "$FACTORY_MODE" "$ROOT" "$CFG"; default_branch',
            'test', str(SCRIPTS)], cwd)

    def gate(self, cwd):
        # Deliberately launch elsewhere: runtime cwd must control resolution.
        return self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')], self.root,
                            json.dumps({'cwd': str(cwd)}))

    def configure_check(self, name, command):
        (self.root / f'.factory/projects/{name}.yml').write_text(
            'areas: {}\ncommands:\n  check: ' + json.dumps(command) + '\n')
        (self.root / name / 'changed.txt').write_text('new file')

    def test_legacy_local_configuration(self):
        (self.api / '.factory.yml').write_text('default_branch: legacy\nareas: {}\n')
        result = self.context(self.api)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['repository', str(self.api),
                         str(self.api / '.factory.yml'), 'legacy'])
        self.assertEqual(self.gate(self.api).returncode, 0)

    def test_no_config_defaults(self):
        result = self.context(self.api)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], 'main')
        self.assertEqual(result.stdout.splitlines()[0], 'repository')

    def test_external_config_from_nested_directory(self):
        self.workspace()
        nested = self.api / 'src'
        nested.mkdir()
        result = self.context(nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['workspace', str(self.api),
                         str(self.root / '.factory/projects/api.yml'), 'develop'])

    def test_unlisted_repository_remains_legacy_even_with_other_conflict(self):
        self.workspace()
        (self.api / '.factory.yml').write_text('areas: {}\n')
        other = self.repo('other')
        result = self.context(other)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], 'repository')

    def test_conflicting_config_is_not_overridden(self):
        self.workspace()
        (self.api / '.factory.yml').write_text('areas: {}\n')
        result = self.gate(self.root)
        self.assertEqual(result.returncode, 2)
        self.assertIn('already has .factory.yml', result.stderr)

    def test_missing_external_config_blocks(self):
        self.workspace()
        (self.root / '.factory/projects/api.yml').unlink()
        self.assertEqual(self.gate(self.root).returncode, 2)

    def test_parent_gate_runs_all_projects_in_correct_directories(self):
        self.workspace()
        log = self.root / '.factory/checks.log'
        for name in ['api', 'web']:
            self.configure_check(name, 'pwd >> ' + shlex.quote(str(log)))
        result = self.gate(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().splitlines(), [str(self.api), str(self.web)])
        self.assertFalse((self.api / '.factory.yml').exists())

    def test_failure_does_not_skip_sibling_checks(self):
        self.workspace()
        log = self.root / '.factory/checks.log'
        self.configure_check('api', 'exit 1')
        self.configure_check('web', 'pwd >> ' + shlex.quote(str(log)))
        result = self.gate(self.root)
        self.assertEqual(result.returncode, 2)
        self.assertIn('project checks', result.stderr)
        self.assertEqual(log.read_text().strip(), str(self.web))

    def test_child_session_checks_only_its_project(self):
        self.workspace()
        log = self.root / '.factory/checks.log'
        for name in ['api', 'web']:
            self.configure_check(name, 'pwd >> ' + shlex.quote(str(log)))
        result = self.gate(self.api)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().splitlines(), [str(self.api)])

    def test_invalid_or_duplicate_project_paths_block(self):
        self.workspace()
        for path in ['../api', 'api']:
            (self.root / '.factory/workspace.yml').write_text(
                f'version: 1\nmode: workspace\nprojects:\n  api: {{path: api}}\n  web: {{path: {path}}}\n')
            self.assertEqual(self.gate(self.root).returncode, 2)

    def test_symlink_project_blocks(self):
        self.workspace()
        (self.root / 'alias').symlink_to(self.api, target_is_directory=True)
        (self.root / '.factory/workspace.yml').write_text(
            'version: 1\nmode: workspace\nprojects:\n  api: {path: alias}\n')
        self.assertEqual(self.gate(self.root).returncode, 2)

    def test_custom_checks_preserve_workflow_linters(self):
        self.workspace()
        self.configure_check('api', 'true')
        workflows = self.api / '.github/workflows'
        workflows.mkdir(parents=True)
        (workflows / 'test.yml').write_text('name: example\n')
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        log = self.root / '.factory/linters.log'
        for tool in ['actionlint', 'zizmor']:
            script = bin_dir / tool
            script.write_text('#!/bin/sh\necho ' + tool + ' >> ' + shlex.quote(str(log)) + '\n')
            script.chmod(0o755)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
            data=json.dumps({'cwd': str(self.api)}), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().splitlines(), ['actionlint', 'zizmor'])

    def test_unchanged_project_does_not_run_custom_check(self):
        self.workspace()
        self.configure_check('api', 'exit 1')
        (self.api / 'changed.txt').unlink()
        result = self.gate(self.api)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_file_guard_resolves_child_migration_from_parent(self):
        migrations = self.api / 'migrations'
        migrations.mkdir()
        migration = migrations / '0001_initial.py'
        migration.write_text('# existing migration\n')
        for args in [['add', '.'], ['-c', 'user.name=Test', '-c',
                     'user.email=test@example.invalid', 'commit', '-qm', 'migration'],
                     ['update-ref', 'refs/remotes/origin/main', 'HEAD']]:
            result = self.run_cmd(['git', *args], self.api)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cmd(['bash', str(SCRIPTS / 'guard-files.sh')],
            data=json.dumps({'cwd': str(self.root), 'tool_input': {
                'file_path': 'api/migrations/0001_initial.py'}}))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('migration already merged', result.stderr)

    def test_bash_guard_uses_runtime_repository_for_staged_secrets(self):
        (self.api / '.env').write_text('FAKE=fixture\n')
        self.run_cmd(['git', 'add', '.env'], self.api)
        result = self.run_cmd(['bash', str(SCRIPTS / 'guard-bash.sh')],
            data=json.dumps({'cwd': str(self.api), 'tool_input': {'command': 'git commit -m test'}}))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('staged files look like secrets', result.stderr)

    def test_formatter_uses_runtime_directory_for_relative_path(self):
        (self.api / 'example.py').write_text('x = 1\n')
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        log = self.root / 'formatter.txt'
        script = bin_dir / 'ruff'
        script.write_text('#!/bin/sh\nprintf "%s\\n" "$PWD" "$3" > ' + shlex.quote(str(log)) + '\n')
        script.chmod(0o755)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        result = self.run_cmd(['bash', str(SCRIPTS / 'format.sh')],
            data=json.dumps({'cwd': str(self.api), 'tool_input': {'file_path': 'example.py'}}), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().splitlines(), [str(self.api), str(self.api / 'example.py')])

    def test_stop_recursion_guard_is_preserved(self):
        self.workspace()
        self.configure_check('api', 'exit 1')
        result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')], data=json.dumps(
            {'cwd': str(self.root), 'stop_hook_active': True}))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_shell_guard_common_mutations_and_read_only_controls(self):
        blocked = [
            'terraform apply', 'terraform -chdir=infra apply',
            'terraform -chdir infra destroy',
            'kubectl --namespace default delete pod example',
            'helm --namespace default upgrade example ./chart',
            'aws s3 rm s3://example/object', 'aws --region us-east-1 s3 sync . s3://example',
            'git push origin HEAD:main', 'git push origin HEAD:refs/heads/master',
            'git -C repo push --force-with-lease origin feature',
        ]
        allowed = ['terraform -chdir=infra plan', 'kubectl --namespace default get pods',
                   'aws s3 ls s3://example', 'git push origin feature', 'git diff']
        for command in blocked + allowed:
            with self.subTest(command=command):
                result = self.run_cmd(['bash', str(SCRIPTS / 'guard-bash.sh')],
                    data=json.dumps({'cwd': str(self.api), 'tool_input': {'command': command}}))
                self.assertEqual(result.returncode, 2 if command in blocked else 0, result.stderr)

    def test_migration_guard_uses_workspace_default_and_normalizes_path(self):
        self.workspace()
        migrations = self.api / 'app/migrations'
        migrations.mkdir(parents=True)
        (migrations / 'nested').mkdir()
        migration = migrations / '0001_initial.py'
        migration.write_text('# fixture\n')
        for args in [['add', '.'], ['-c', 'user.name=Test', '-c',
                     'user.email=test@example.invalid', 'commit', '-qm', 'migration'],
                     ['update-ref', 'refs/remotes/origin/develop', 'HEAD']]:
            self.assertEqual(self.run_cmd(['git', *args], self.api).returncode, 0)
        for path, expected in [('nested/../0001_initial.py', 2), ('0002_new.py', 0)]:
            result = self.run_cmd(['bash', str(SCRIPTS / 'guard-files.sh')], data=json.dumps({
                'cwd': str(self.root), 'tool_input': {'file_path': str(migrations / path)}}))
            self.assertEqual(result.returncode, expected, result.stderr)

    def test_migration_guard_reports_unavailable_base(self):
        migrations = self.api / 'migrations'
        migrations.mkdir()
        result = self.run_cmd(['bash', str(SCRIPTS / 'guard-files.sh')], data=json.dumps({
            'cwd': str(self.api), 'tool_input': {'file_path': str(migrations / '0001_new.py')}}))
        self.assertEqual(result.returncode, 2)
        self.assertIn('unavailable', result.stderr)

    def test_repository_check_command_runs_for_dependency_change(self):
        log = self.root / 'checks.log'
        (self.api / '.factory.yml').write_text('areas: {}\ncommands:\n  check: ' +
            json.dumps('pwd > ' + shlex.quote(str(log))) + '\n')
        (self.api / 'uv.lock').write_text('# fixture\n')
        result = self.gate(self.api)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().strip(), str(self.api))
        self.assertIn('PASSED project command', result.stderr)

    def mock_tools(self, scripts):
        bin_dir = self.root / 'bin'
        bin_dir.mkdir(exist_ok=True)
        for tool, body in scripts.items():
            path = bin_dir / tool
            path.write_text('#!/bin/sh\n' + body + '\n')
            path.chmod(0o755)
        return dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])

    def test_dependency_and_config_changes_trigger_frontend_checks(self):
        frontend = self.web / 'web'
        frontend.mkdir()
        env = self.mock_tools({'npm': 'exit 17', 'npx': 'exit 0'})
        for filename in ['package-lock.json', 'package.json', 'tsconfig.json', 'vite.config.ts']:
            with self.subTest(filename=filename):
                path = frontend / filename
                path.write_text('{}\n')
                result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
                    data=json.dumps({'cwd': str(self.web)}), env=env)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('frontend checks', result.stderr)
                path.unlink()

    def test_no_python_tests_fails_unless_explicitly_allowed(self):
        (self.api / 'backend').mkdir()
        (self.api / 'backend/example.py').write_text('# fixture\n')
        env = self.mock_tools({'ruff': 'exit 0', 'mypy': 'exit 0',
                              'pytest': 'echo "no tests ran"; exit 5', 'python': 'exit 0'})
        for allow, expected in [(False, 2), (True, 0)]:
            (self.api / '.factory.yml').write_text(
                'areas:\n  backend: {path: backend}\nchecks:\n  allow_no_tests: ' + str(allow).lower() + '\n')
            result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
                data=json.dumps({'cwd': str(self.api)}), env=env)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertIn('SKIPPED pytest' if allow else 'zero tests', result.stderr)

    def test_no_frontend_tests_not_silently_allowed(self):
        (self.web / 'web').mkdir()
        (self.web / 'web/example.ts').write_text('// fixture\n')
        env = self.mock_tools({'npm': 'exit 0', 'npx':
            'case "$*" in *vitest*) case "$*" in *--passWithNoTests*) exit 0;; *) exit 1;; esac;; esac'})
        result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
            data=json.dumps({'cwd': str(self.web)}), env=env)
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_frontend_success_is_supported_without_optional_flags(self):
        (self.web / 'web').mkdir()
        (self.web / 'web/example.ts').write_text('// fixture\n')
        env = self.mock_tools({'npm': 'exit 0', 'npx': 'echo "1 test passed"; exit 0'})
        result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
            data=json.dumps({'cwd': str(self.web)}), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASSED frontend', result.stderr)

    def test_root_python_lockfile_triggers_backend_checks(self):
        (self.api / 'backend').mkdir()
        (self.api / 'uv.lock').write_text('# fixture\n')
        env = self.mock_tools({'uv': 'exit 17'})
        result = self.run_cmd(['bash', str(SCRIPTS / 'quality-gate.sh')],
            data=json.dumps({'cwd': str(self.api)}), env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('ruff in backend', result.stderr)

    def test_no_applicable_checks_report_skipped(self):
        result = self.gate(self.api)
        self.assertEqual(result.returncode, 0)
        self.assertIn('SKIPPED', result.stderr)
        self.assertNotIn('PASSED', result.stderr)


if __name__ == '__main__':
    unittest.main()
