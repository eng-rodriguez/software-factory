"""Check the fixtures and deterministic graders, not live agent behavior."""
import os
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


if __name__ == '__main__':
    unittest.main()
