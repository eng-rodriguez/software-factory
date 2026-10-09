"""Exercise saved-plan binding without Terraform, credentials, or network access."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'plugins/factory/skills/devsecops-gha/templates/terraform-plan.sh'


class SavedPlanTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='factory plan ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.tf = self.root / 'infra'
        self.tf.mkdir()
        (self.tf / '.terraform.lock.hcl').write_text('# reviewed lockfile\n')
        self.plan = self.root / 'saved plan'
        self.log = self.root / 'calls.jsonl'
        tools = self.root / 'bin'
        tools.mkdir()
        mock = tools / 'terraform'
        mock.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['TF_CALLS'], 'a') as log:
    log.write(json.dumps(args) + '\\n')
command = args[1]
if command == 'plan':
    path = next(arg[5:] for arg in args if arg.startswith('-out='))
    pathlib.Path(path).write_text('saved plan fixture')
elif command == 'show':
    print(json.dumps({'resource_changes': [{'change': {'actions': ['create']}}]}))
elif command == 'apply' and os.environ.get('STALE_STATE') == 'true':
    sys.exit(1)
''')
        mock.chmod(0o755)
        self.env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'],
            TF_DIR=str(self.tf), PLAN_DIR=str(self.plan), TARGET_ENV='staging',
            IMAGE_DIGEST='sha256:fixture', GITHUB_SHA='a' * 40, GITHUB_RUN_ID='123',
            GITHUB_RUN_ATTEMPT='1', TF_CALLS=str(self.log),
            GITHUB_STEP_SUMMARY=str(self.root / 'summary.md'))

    def run_plan(self, mode, **env):
        return subprocess.run(['bash', str(SCRIPT), mode], env=dict(self.env, **env),
                              capture_output=True, text=True)

    def prepare(self):
        result = self.run_plan('prepare')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.log.write_text('')

    def manifest(self, **changes):
        path = self.plan / 'manifest.json'
        data = json.loads(path.read_text())
        path.write_text(json.dumps(dict(data, **changes)))

    def test_applies_saved_plan_without_replanning(self):
        self.prepare()
        result = self.run_plan('apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual([call[1] for call in calls], ['init', 'apply'])
        self.assertIn('-lockfile=readonly', calls[0])
        self.assertEqual(calls[1][-1], str(self.plan / 'tf.plan'))
        self.assertNotIn('-auto-approve', calls[1])

    def test_rejects_wrong_context_before_any_terraform_call(self):
        self.prepare()
        for key, value in [('GITHUB_SHA', 'b' * 40), ('GITHUB_RUN_ID', '124'),
                           ('GITHUB_RUN_ATTEMPT', '2'), ('TARGET_ENV', 'production'),
                           ('TF_DIR', '/other'), ('IMAGE_DIGEST', 'sha256:other')]:
            with self.subTest(key=key):
                result = self.run_plan('apply', **{key: value})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.log.read_text(), '')

    def test_rejects_expired_future_and_malformed_timestamp(self):
        self.prepare()
        for created in [int(time.time()) - 3601, int(time.time()) + 60, 'invalid']:
            with self.subTest(created=created):
                self.manifest(created=created)
                self.assertNotEqual(self.run_plan('apply').returncode, 0)
                self.assertEqual(self.log.read_text(), '')

    def test_rejects_changed_plan(self):
        self.prepare()
        (self.plan / 'tf.plan').write_text('different plan')
        self.assertNotEqual(self.run_plan('apply').returncode, 0)
        self.assertEqual(self.log.read_text(), '')

    def test_rejects_changed_provider_lockfile(self):
        self.prepare()
        (self.tf / '.terraform.lock.hcl').write_text('# changed')
        self.assertNotEqual(self.run_plan('apply').returncode, 0)
        self.assertEqual(self.log.read_text(), '')

    def test_stale_state_is_not_repaired_by_replanning(self):
        self.prepare()
        self.assertNotEqual(self.run_plan('apply', STALE_STATE='true').returncode, 0)
        calls = [json.loads(line)[1] for line in self.log.read_text().splitlines()]
        self.assertEqual(calls, ['init', 'apply'])

    def test_summary_has_action_counts(self):
        self.prepare()
        self.assertEqual(json.loads((self.plan / 'summary.json').read_text()),
                         [{'action': 'create', 'count': 1}])


if __name__ == '__main__':
    unittest.main()
