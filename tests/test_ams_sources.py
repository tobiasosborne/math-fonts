"""Regression checks for source identity, coverage accounting and Greek policy."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ams_audit', ROOT / 'tools/audit_ams_sources.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AMSSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / 'runs/ams-coverage-2026-10-30/source-audit.json').read_text())
        cls.inv = json.loads(audit.INVENTORY.read_text())
        cls.targets = {r['target_id']: r for r in cls.report['targets']}

    def test_frozen_target_partition_and_exact_binding_identity(self):
        rows = self.report['targets']
        self.assertEqual(len(rows), len(self.targets))
        self.assertEqual(set(self.targets), {g['id'] for g in self.inv['glyphs']})
        self.assertEqual([sum(r['encoding_kind'] == k for r in rows) for k in ('scalar', 'sequence', 'unencoded')], [1196, 12, 717])
        identity = lambda b: (b['package'], b['command'], b['target_id'], b['kind'])
        self.assertEqual({identity(b) for b in self.report['bindings']}, {identity(b) for b in self.inv['command_bindings']})
        self.assertEqual(len(self.report['bindings']), 585)
        self.assertEqual(len({b['command'] for b in self.report['bindings']}), 577)
        self.assertEqual(sum(self.report['counts']['by_availability_class'].values()), 1925)

    def test_style_reuse_does_not_collapse_expressive_alphabets(self):
        italic = self.targets['u1D434']
        self.assertEqual(italic['selected_source']['source_codepoint'], 'U+0041')
        self.assertEqual(italic['selected_source']['style'], 'Italic')
        self.assertEqual(self.targets['u1D400']['selected_source']['style'], 'Bold')
        self.assertEqual(self.targets['u1D468']['selected_source']['style'], 'Bold italic')
        self.assertEqual(self.targets['u1D7CE']['selected_source']['source_codepoint'], 'U+0030')
        for row in self.report['targets']:
            if row['alphabet_style'] in ('double_struck', 'fraktur', 'script', 'sans_upright', 'monospace', 'bold_fraktur'):
                self.assertEqual(row['availability_class'], 'missing_expressive_alphabet', row['target_id'])
        self.assertEqual(self.targets['u210F']['availability_class'], 'missing_expressive_outline')
        self.assertEqual(self.targets['u1D6A4']['selected_source']['style'], 'Italic')

    def test_custom_greek_priority_and_native_alternates(self):
        self.assertEqual(self.targets['u1D6FC']['availability_class'], 'custom_pilot_greek')
        self.assertEqual(self.targets['u1D6FE']['availability_class'], 'missing_custom_greek')
        self.assertTrue(self.targets['u1D6FE']['stock_candidates'])
        for row in self.report['targets']:
            if row['native_greek_alternate_only']:
                self.assertFalse(row['availability_class'].startswith('external_'))
        for face in self.report['native_greek_alternates']:
            self.assertEqual(len(face['slots']), 61)
            self.assertFalse(face['default'])
            self.assertFalse(face['coverage_credit_for_missing_custom'])
        self.assertTrue(self.targets['u03B1']['style_caveat'])

    def test_no_sequence_or_engineering_credit_from_component_cmap(self):
        for row in self.report['targets']:
            self.assertFalse(row['accepted_design'])
            self.assertFalse(row['engineering_coverage_credit'])
            self.assertEqual(row['rendered_proof'], 'not_established_by_this_audit')
            if row['encoding_kind'] == 'sequence':
                self.assertEqual(row['availability_class'], 'sequence_binding_required')
                self.assertIsNone(row['pilot_cmap_glyph'])
        self.assertEqual(self.targets['u0028.size1']['availability_class'], 'size_engineering_required')
        self.assertTrue(self.targets['u0028.size1']['pilot_growth_construction']['variants'])
        self.assertFalse(self.targets['u0028.size1']['pilot_growth_construction']['has_assembly'])

    def test_all_direct_ams_probed_and_not_credited_as_rendered(self):
        direct = self.report['direct_amssymb']
        self.assertEqual(len(direct), 204)
        names = {b['command'] for b in direct}
        probe = self.report['macro_availability']
        self.assertEqual({r['command'] for r in probe['results']}, names)
        self.assertEqual(probe['counts'], {'defined': 170, 'undefined': 34})
        candidates = {b['command'] for b in direct if b['availability_class'].startswith('external_')}
        self.assertEqual(candidates, {'\\centerdot', '\\eth', '\\lozenge'})
        for b in direct:
            self.assertEqual(b['rendered_proof'], 'not_established_by_this_audit')
        self.assertFalse(next(b for b in direct if b['command'] == '\\centerdot')['macro_defined'])

    def test_hash_mismatch_fails_before_font_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'not-a-font.otf'
            p.write_bytes(b'changed font')
            with self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
                audit.font_info(p, '0' * 64)


if __name__ == '__main__':
    unittest.main()
