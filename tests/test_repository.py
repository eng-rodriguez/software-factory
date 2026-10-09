"""Validate distributable metadata, links and critical workflow wiring."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'plugins/factory/skills/devsecops-gha/templates'


def yaml(path):
    return json.loads(subprocess.check_output(['yq', '-o=json', '.', str(path)], text=True))


class DistributionTests(unittest.TestCase):
    def test_json_and_yaml_parse(self):
        for folder in ['plugins', 'settings', '.claude-plugin', '.github', 'evals']:
            for path in (ROOT / folder).rglob('*'):
                with self.subTest(path=path):
                    if path.suffix == '.json':
                        json.loads(path.read_text())
                    elif path.suffix in ['.yml', '.yaml']:
                        yaml(path)
        plugin = json.loads((ROOT / 'plugins/factory/.claude-plugin/plugin.json').read_text())
        self.assertRegex(plugin['version'], r'^\d+\.\d+\.\d+$')

    def test_internal_plugin_links_resolve(self):
        for path in (ROOT / 'plugins').rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#') or '<' in target:
                    continue
                target = target.split('#')[0]
                with self.subTest(path=path, target=target):
                    self.assertTrue((path.parent / target).exists())

    def test_actions_use_immutable_references(self):
        files = list(TEMPLATES.glob('*.yml')) + list((ROOT / '.github/workflows').glob('*.yml'))
        for path in files:
            for ref in re.findall(r'^\s*(?:- )?uses:\s*(\S+)', path.read_text(), re.M):
                with self.subTest(path=path, ref=ref):
                    self.assertRegex(ref, r'^[\w.-]+/[\w./-]+@[a-f0-9]{40}$')

    def test_deploy_verifies_before_mutation_and_consumes_matching_plan(self):
        jobs = yaml(TEMPLATES / 'deliver.yml')['jobs']
        for target in ['staging', 'production']:
            deploy = jobs[f'deploy-{target}']
            steps = deploy['steps']
            verify = next(i for i, step in enumerate(steps) if step.get('name') == 'Verify signature')
            login = next(i for i, step in enumerate(steps) if step.get('uses', '').startswith('azure/login@'))
            apply = next(i for i, step in enumerate(steps) if step.get('name') == 'Apply the approved saved plan')
            self.assertLess(verify, login)
            self.assertLess(login, apply)
            self.assertEqual(steps[apply]['env']['TARGET_ENV'], target)
            self.assertIn(f'plan-{target}', deploy['needs'])
            download = next(step for step in steps if step.get('uses', '').startswith('actions/download-artifact@'))
            self.assertEqual(download['with']['artifact-ids'], '${{ needs.plan-' + target + '.outputs.artifact }}')
            plan = jobs[f'plan-{target}']
            self.assertEqual(plan['environment'], target + '-plan')
            upload = next(step for step in plan['steps'] if step.get('uses', '').startswith('actions/upload-artifact@'))
            self.assertEqual(upload['with']['retention-days'], 1)
            self.assertNotIn('plan.log', upload['with']['path'])
            self.assertIn('tf.plan', upload['with']['path'])
        self.assertIn('dast', jobs['plan-production']['needs'])

    def test_container_scan_includes_dependency_inputs(self):
        workflow = yaml(TEMPLATES / 'ci.yml')
        filter_step = next(step for step in workflow['jobs']['changes']['steps'] if step.get('id') == 'filter')
        filters = subprocess.check_output(['yq', '-o=json', '.'],
            input=filter_step['with']['filters'], text=True)
        paths = json.loads(filters)['container']
        for path in ['uv.lock', 'pyproject.toml', 'requirements*.txt', 'web/**', '.dockerignore']:
            self.assertIn(path, paths)


if __name__ == '__main__':
    unittest.main()
