"""Regression coverage for file selection and strict JSON number loading."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_fail_closed import event_digest, synthetic_pack
import verify


class InputBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = Path(verify.__file__).resolve()
        self.write(synthetic_pack())

    def write(self, pack):
        for name, data in pack.items():
            (self.root / (name + '.json')).write_text(json.dumps(data), encoding='utf-8')

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(self.script), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True)

    def test_overflow_in_each_file_is_invalid_even_in_unused_metadata(self):
        for name in ('events', 'batches', 'anchors'):
            for literal in ('1e400', '-1e400'):
                with self.subTest(name=name, literal=literal):
                    self.write(synthetic_pack())
                    path = self.root / (name + '.json')
                    path.write_text(path.read_text().replace(
                        '{', '{"metadata":{"number":' + literal + '},', 1), encoding='utf-8')
                    result = verify.verify_evidence_pack_result(self.root)
                    self.assertEqual(result.status, verify.INVALID)
                    self.assertFalse(result.local_checks_passed)
                    self.assertFalse(result)

    def test_finite_exponent_metadata_is_supported(self):
        path = self.root / 'anchors.json'
        path.write_text(path.read_text().replace('{', '{"metadata":1e100,', 1), encoding='utf-8')
        result = verify.verify_evidence_pack_result(self.root)
        self.assertEqual(result.status, verify.INDETERMINATE)
        self.assertTrue(result.local_checks_passed)

    def test_control_event_count_requires_an_integer_when_present(self):
        for value in (3.0, True, '3', None):
            with self.subTest(value=value):
                pack = synthetic_pack()
                event = pack['events']['events'][-1]
                event['Governance']['EventCount'] = value
                event['Header']['EventHash'] = event_digest(event)
                self.write(pack)
                result = verify.verify_evidence_pack_result(self.root)
                self.assertEqual(result.status, verify.INVALID)
                self.assertFalse(result.local_checks_passed)
                self.assertIn('control event count must be an integer', '\n'.join(result.messages))

    def test_control_event_integer_count_can_match(self):
        pack = synthetic_pack()
        event = pack['events']['events'][-1]
        event['Governance']['EventCount'] = 3
        event['Header']['EventHash'] = event_digest(event)
        self.write(pack)
        result = verify.verify_evidence_pack_result(self.root)
        self.assertEqual(result.status, verify.INDETERMINATE)
        self.assertTrue(result.local_checks_passed)

    def test_cli_checks_explicit_directory(self):
        result = self.run_cli(self.root)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Event hashes matching the legacy encoding: 4/4', result.stdout)
        self.assertIn('Local consistency: PASS (not authenticated)', result.stdout)

    def test_cli_detects_mismatch_in_explicit_directory(self):
        pack = synthetic_pack()
        pack['events']['events'][0]['Payload']['value'] = 'changed'
        self.write(pack)
        result = self.run_cli(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Overall: INVALID', result.stdout)
        self.assertNotIn('Local consistency: PASS', result.stdout)

    def test_cli_missing_directory_does_not_inspect_bundled_pack(self):
        result = self.run_cli(self.root / 'missing')
        self.assertEqual(result.returncode, 2)
        self.assertIn('evidence unavailable', result.stdout)
        self.assertIn('Local consistency: NOT ESTABLISHED', result.stdout)
        self.assertNotIn('27/27', result.stdout)

    def test_cli_default_directory_is_independent_of_working_directory(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Event hashes matching the legacy encoding: 27/27', result.stdout)

    def test_cli_help_does_not_inspect_evidence(self):
        result = self.run_cli('--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('evidence_dir', result.stdout)
        self.assertNotIn('Local consistency:', result.stdout)

    def test_cli_rejects_unknown_options_and_extra_arguments(self):
        for args in (('--unknown',), (str(self.root), 'extra')):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('usage:', result.stderr)
                self.assertNotIn('Local consistency:', result.stdout)


if __name__ == '__main__':
    unittest.main()
