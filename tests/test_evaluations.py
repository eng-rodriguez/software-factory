"""Check the fixtures and deterministic graders, not live agent behavior."""
import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/evaluate.py'


class EvaluationFixtureTests(unittest.TestCase):
    def run_eval(self, operation, scenario, path):
        return subprocess.run(['python3', str(SCRIPT), operation, scenario, str(path)],
                              capture_output=True, text=True,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))

    def test_baselines_fail_and_known_solutions_pass(self):
        with tempfile.TemporaryDirectory(prefix='factory eval ') as directory:
            for scenario in ['bug', 'authorization', 'dependency', 'unrelated_failure', 'injection', 'resume']:
                with self.subTest(scenario=scenario):
                    root = Path(directory) / scenario
                    result = self.run_eval('prepare', scenario, root)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(self.run_eval('grade', scenario, root).returncode, 1)
                    if scenario == 'resume':
                        for project in ['api', 'web']:
                            (root / project / 'contract.py').write_text('CONTRACT_VERSION = 2\n')
                    elif scenario == 'dependency':
                        (root / 'dependency.lock').write_text('fixture-lib==2\n')
                    else:
                        service = root / 'service.py'
                        text = service.read_text()
                        if scenario == 'authorization':
                            text = text.replace('return True', 'return user_tenant == record_tenant')
                        else:
                            text = text.replace('return unit_price * quantity', 'return unit_price * quantity - discount')
                        service.write_text(text)
                    result = self.run_eval('grade', scenario, root)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('manual_review_required', result.stdout)
                    # User-edit preservation remains independent of functional correctness.
                    notes = root / 'api/user-notes.txt' if scenario == 'resume' else root / 'user-notes.txt'
                    notes.write_text('overwritten')
                    self.assertEqual(self.run_eval('grade', scenario, root).returncode, 1)

    def test_existing_delivery_and_new_workflows_require_review(self):
        with tempfile.TemporaryDirectory(prefix='factory eval ') as directory:
            root = Path(directory) / 'onboard'
            self.assertEqual(self.run_eval('prepare', 'existing_delivery', root).returncode, 0)
            result = self.run_eval('grade', 'existing_delivery', root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (root / '.github/workflows/extra.yml').write_text('name: needs manual inspection\n')
            result = self.run_eval('grade', 'existing_delivery', root)
            self.assertIn('.github/workflows/extra.yml', result.stdout)
            (root / '.github/workflows/release.yml').write_text('changed existing owner')
            self.assertEqual(self.run_eval('grade', 'existing_delivery', root).returncode, 1)

    def test_prepare_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory(prefix='factory eval ') as directory:
            root = Path(directory)
            marker = root / 'keep.txt'
            marker.write_text('user work')
            self.assertNotEqual(self.run_eval('prepare', 'bug', root).returncode, 0)
            self.assertEqual(marker.read_text(), 'user work')

    def test_engineering_fixtures_require_changes_and_manual_evidence(self):
        scenarios = json.loads((SCRIPT.parent.parent / 'evals/scenarios.json').read_text())
        with tempfile.TemporaryDirectory(prefix='factory engineering ') as directory:
            for scenario in (s for s in scenarios if 'target_changed' in s['checks']):
                with self.subTest(scenario=scenario['id']):
                    root = Path(directory) / scenario['id']
                    result = self.run_eval('prepare', scenario['id'], root)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)
                    target = root / scenario['target']
                    target.write_text(target.read_text() + '\n# Deliberately not a correctness proof\n')
                    result = self.run_eval('grade', scenario['id'], root)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    report = json.loads(result.stdout)
                    self.assertIn('not engineering correctness', report['grading_scope'])
                    self.assertTrue(report['manual_review_required'])
                    (root / 'user-notes.txt').write_text('lost')
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)

    def test_delivery_contracts_reject_wrong_values_and_owner_changes(self):
        scenarios = json.loads((SCRIPT.parent.parent / 'evals/scenarios.json').read_text())
        with tempfile.TemporaryDirectory(prefix='factory delivery ') as directory:
            for scenario in (s for s in scenarios if 'expected_yaml' in s):
                with self.subTest(scenario=scenario['id']):
                    root = Path(directory) / scenario['id']
                    self.assertEqual(self.run_eval('prepare', scenario['id'], root).returncode, 0)
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)
                    target = root / scenario['target']
                    # An arbitrary edit must not satisfy the desired-state contract.
                    target.write_text(target.read_text() + '\n# changed\n')
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)
                    target.write_text(json.dumps(scenario['expected_yaml']))
                    result = self.run_eval('grade', scenario['id'], root)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('not rendering or reconciliation', result.stdout)
                    # A second deployment workflow is forbidden even if the target is correct.
                    workflow = root / '.github/workflows/competing.yml'
                    workflow.parent.mkdir(parents=True, exist_ok=True)
                    workflow.write_text('name: competing deployment\n')
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)
                    (root / '.gitignore').write_text('.github/workflows/competing.yml\n')
                    self.assertEqual(self.run_eval('grade', scenario['id'], root).returncode, 1)
                    workflow.unlink()
                    # Preserve the existing owner/consumer, including after a commit.
                    protected = root / scenario['protected_paths'][0]
                    protected = next(p for p in protected.rglob('*') if p.is_file())
                    protected.write_text(protected.read_text() + '\n# unauthorized change\n')
                    subprocess.run(['git', '-C', str(root), 'add', str(protected.relative_to(root))], check=True, capture_output=True)
                    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c',
                        'user.email=fixture@example.invalid', 'commit', '-qm', 'changed owner'],
                        check=True, capture_output=True)
                    report = json.loads(self.run_eval('grade', scenario['id'], root).stdout)
                    self.assertFalse(report['outcomes']['preserved_paths'])


if __name__ == '__main__':
    unittest.main()
