"""Current checksums must match, while archived evidence remains byte-identical."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CurrentManifestTests(unittest.TestCase):
    def test_listed_file_digests_and_sizes_match_current_tree(self):
        manifest = json.loads((ROOT / 'hash_manifest.json').read_text())
        self.assertEqual(manifest['file_count'], len(manifest['files']))
        for name, expected in manifest['files'].items():
            with self.subTest(file=name):
                content = (ROOT / name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), expected['sha256'])
                self.assertEqual(len(content), expected['size_bytes'])

    def test_original_manifest_and_evidence_bytes_are_preserved(self):
        historical = ROOT / 'archive/hash_manifest.pre-2026-11-02.json'
        self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), '442d0198bbbfc7af0c00e724f679981c7ce6918f739acc11b520131371073e50')
        original = json.loads(historical.read_text())
        corrected = {'README.md', 'verify.py', 'CHANGELOG.md'}
        redirects = {}
        for name, entry in original['files'].items():
            if name in corrected:
                continue
            expected = entry['sha256'] if isinstance(entry, dict) else entry
            path = ROOT / redirects.get(name, name)
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

if __name__ == '__main__':
    unittest.main()
