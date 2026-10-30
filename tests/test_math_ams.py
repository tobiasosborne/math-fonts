"""AMS source contract tests. Synthetic outlines are test geometry, not designs."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('math_ams', REPO / 'tools/build_math_ams.py')
ams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ams)
BASE = REPO / 'runs/pipeline-2026-10-30/font-sources.json'


class MathAMSTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Deliberately non-letter geometry, with a tiny second contour: this must
        # never be promoted as a designed gamma, Greek face, or release fixture.
        self.curves = {'paths': [
            {'segments': [
                {'tag': 1, 'points': [[0, 0], [20, 0], [20, 20]]},
                {'tag': 2, 'points': [[20, 20], [5, 20], [0, 10]]},
                {'tag': 2, 'points': [[0, 10], [0, 5], [0, 0]]}]},
            {'segments': [
                {'tag': 2, 'points': [[3, 3], [3, 4], [4, 4]]},
                {'tag': 2, 'points': [[4, 4], [4, 3], [3, 3]]}]}]}
        (self.root / 'curves.json').write_text(json.dumps(self.curves))
        (self.root / 'root.bin').write_bytes(b'SYNTHETIC TEST ROOT; NOT DESIGN EVIDENCE')
        self.entry = {'name': 'test-gamma', 'codepoints': [0x3B3, 0x1D6FE],
            'kind': 'greek', 'curves': 'curves.json', 'source_crop_box': [100, 50, 130, 90],
            'baseline_root': 80, 'source_em_pixels': 100,
            'registration_to_root': {'scale': 1, 'translate_x': 100, 'translate_y': 50},
            'root_sha256': ams.sha(self.root / 'root.bin'), 'root_image': 'root.bin',
            'provenance': {'test_only': True, 'description': 'Non-letter cubic fixture; not a Greek design'}}

    def source(self, entry=None, name='test-gamma'):
        path = self.root / 'sources.json'
        path.write_text(json.dumps({'sources': {name: entry or self.entry}}))
        return path

    def test_arbitrary_explicit_role_has_exact_cubic_contours_and_provenance(self):
        output = self.root / 'font'
        manifest = ams.build(output, self.source())
        with TTFont(output / ams.FONT_NAME) as font:
            self.assertIn('CFF ', font)
            self.assertIn('MATH', font)
            self.assertNotIn('glyf', font)
            self.assertEqual(font.getBestCmap(), {32: 'space', 0x3B3: 'test-gamma', 0x1D6FE: 'test-gamma'})
            pen = RecordingPen()
            font.getGlyphSet()['test-gamma'].draw(pen)
            self.assertEqual(sum(op == 'closePath' for op, _ in pen.value), 2)
            self.assertTrue(any(op == 'curveTo' for op, _ in pen.value))
            self.assertEqual([r.ScriptTag for r in font['GSUB'].table.ScriptList.ScriptRecord], ['math'])
            self.assertEqual(font['GSUB'].table.LookupList.LookupCount, 0)
            self.assertIn('math', [r.ScriptTag for r in font['GPOS'].table.ScriptList.ScriptRecord])
        record = manifest['glyphs']['test-gamma']
        self.assertEqual(record['source_em_pixels'], 100)
        self.assertEqual(record['contour_count'], 2)
        self.assertEqual(record['curves_sha256'], ams.sha(self.root / 'curves.json'))
        self.assertEqual(record['provenance'], self.entry['provenance'])
        self.assertTrue(record['root_image_verified'])
        self.assertEqual(len(record['outline_signature_sha256']), 64)

    def test_root_em_and_uniform_registration_are_per_glyph(self):
        entry = ams.validate_entry('test-gamma', self.entry, self.root)
        pen, _ = ams.outline(entry)
        self.assertEqual(ams.pilot.bounds(pen), (0, 100, 200, 300))
        transformed = copy.deepcopy(self.curves)
        for contour in transformed['paths']:
            for segment in contour['segments']:
                segment['points'] = [[x*4+12, y*4+20] for x, y in segment['points']]
        (self.root / 'large.json').write_text(json.dumps(transformed))
        enlarged = {**entry, 'curves': str(self.root / 'large.json'),
            'registration_to_root': {'scale': .25, 'translate_x': 97, 'translate_y': 45}}
        self.assertEqual(pen.value, ams.outline(enlarged)[0].value)
        calibrated = {**entry, 'source_em_pixels': 200}
        self.assertEqual(ams.pilot.bounds(ams.outline(calibrated)[0]), (0, 50, 100, 150))

    def test_pilot_adoption_and_new_role_have_no_stock_or_inferred_coverage(self):
        output = self.root / 'hybrid'
        manifest = ams.build(output, self.source(), BASE)
        with TTFont(output / ams.FONT_NAME) as font:
            cmap = font.getBestCmap()
            expected = {32, 0x3B3, 0x1D6FE} | {cp for cps in ams.pilot.ROLES.values() for cp in cps}
            self.assertEqual(set(cmap), expected)
            self.assertTrue(all(ord(c) not in cmap for c in 'AZaz0123456789'))
            for cp in [0x3B4, 0x3B5, 0x3C0, 0x1D6FF]:
                self.assertNotIn(cp, cmap)
            math = font['MATH'].table
            for key, value in ams.CONSTANTS.items():
                actual = getattr(math.MathConstants, key)
                self.assertEqual(getattr(actual, 'Value', actual), value)
            info = math.MathGlyphInfo.MathItalicsCorrectionInfo
            self.assertEqual(set(info.Coverage.glyphs), set(ams.pilot.GREEK) | {'test-gamma'})
            variants = math.MathVariants
            self.assertEqual(set(variants.VertGlyphCoverage.glyphs),
                {'left-paren', 'right-paren', 'radical', 'sum', 'integral'})
            for construction in variants.VertGlyphConstruction + variants.HorizGlyphConstruction:
                self.assertIsNone(construction.GlyphAssembly)
                sizes = []
                for rec in construction.MathGlyphVariantRecord:
                    self.assertIn(rec.VariantGlyph, font.getGlyphOrder())
                    sizes.append(rec.AdvanceMeasurement)
                self.assertEqual(sizes, sorted(set(sizes)))
        self.assertFalse(manifest['glyphs']['test-gamma']['retained_pilot_engineering'])
        for name in ams.pilot.ROLES:
            self.assertTrue(manifest['glyphs'][name]['retained_pilot_engineering'])

    def test_invalid_or_incomplete_sources_are_rejected(self):
        changes = [
            {'source_em_pixels': 0}, {'source_em_pixels': float('nan')},
            {'baseline_root': float('inf')}, {'root_sha256': 'bad'},
            {'root_sha256': 'f'*64}, {'curves_sha256': '0'*64},
            {'provenance': {}}, {'codepoints': [ord('A')]}, {'codepoints': [ord('7')]},
            {'codepoints': [0x7F], 'kind': 'symbol'}, {'codepoints': [0x85], 'kind': 'symbol'},
            {'codepoints': [0xD800]}, {'codepoints': [0x110000]},
            {'codepoints': [0x3B3, 0x3B3]}, {'codepoints': [0x2211]},
            {'source_crop_box': [0, 0, 0, 10]}, {'source_crop_box': [0, 0]},
            {'registration_to_root': {'scale': -1, 'translate_x': 0, 'translate_y': 0}},
            {'registration_to_root': {'scale_x': 1, 'scale_y': 2}},
            {'name': 'wrong-name'}, {'kind': 'automatic-fallback'},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                ams.load_sources(self.source({**self.entry, **change}))
        for field in ams.REQUIRED:
            incomplete = dict(self.entry)
            del incomplete[field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                ams.load_sources(self.source(incomplete))
        with self.assertRaises(ValueError):
            ams.load_sources()

    def test_malformed_raw_curves_are_rejected_without_partial_build(self):
        bad_data = [[], {'paths': []}, {'paths': [None]}, {'paths': [{'segments': []}]},
            {'paths': [{'segments': [None]}]},
            {'paths': [{'segments': [{'tag': True, 'points': [[0, 0]]*3}]}]},
            {'paths': [{'segments': [{'tag': 9, 'points': [[0, 0]]*3}]}]},
            {'paths': [{'segments': [{'tag': 1, 'points': [[0, 0], [1, 1]]}]}]},
            {'paths': [{'segments': [{'tag': 1, 'points': [[0, 0], [1, float('nan')], [2, 2]]}]}]}]
        source = self.source()
        output = self.root / 'invalid-font'
        for data in bad_data:
            (self.root / 'curves.json').write_text(json.dumps(data))
            with self.subTest(data=data), self.assertRaises(ValueError):
                ams.build(output, source)
            self.assertFalse(output.exists())

    def test_duplicate_mappings_and_partial_overrides_are_rejected(self):
        entry = {**self.entry, 'name': 'alpha', 'codepoints': [0x3B1]}
        path = self.source(entry, 'alpha')
        loaded, legacy = ams.load_sources(path, BASE)
        self.assertEqual(loaded['alpha']['codepoints'], [0x3B1])
        self.assertNotIn('alpha', legacy)
        path = self.source({**self.entry, 'codepoints': [0x3B1]})
        with self.assertRaisesRegex(ValueError, 'conflicting roles'):
            ams.load_sources(path, BASE)
        path = self.source({'curves': 'curves.json'}, 'alpha')
        with self.assertRaisesRegex(ValueError, 'missing explicit fields'):
            ams.load_sources(path, BASE)

    def test_overridden_engineering_role_does_not_inherit_wrong_growth_recipe(self):
        entry = {**self.entry, 'name': 'radical', 'kind': 'symbol', 'codepoints': [0x221A]}
        output = self.root / 'new-radical'
        manifest = ams.build(output, self.source(entry, 'radical'), BASE)
        self.assertFalse(any(r['source'] == 'radical' for r in manifest['derived_recipes']))
        self.assertNotIn('radical.size1', manifest['glyph_order'])
        with TTFont(output / ams.FONT_NAME) as font:
            self.assertNotIn('radical', font['MATH'].table.MathVariants.VertGlyphCoverage.glyphs)

    def test_all_32_test_roles_accept_explicit_aliases_without_geometry_inference(self):
        # 25 lowercase scalars (including final sigma), six symbol variants,
        # and digamma. Identical fixtures here test serialization ONLY.
        pairs = [(cp, cp-0x3B1+0x1D6FC) for cp in range(0x3B1, 0x3CA)]
        pairs += [(0x3F5, 0x1D716), (0x3D1, 0x1D717), (0x3F0, 0x1D718),
                  (0x3D5, 0x1D719), (0x3F1, 0x1D71A), (0x3D6, 0x1D71B), (0x3DD, None)]
        roles = []
        for i, (native, alias) in enumerate(pairs):
            roles.append({**self.entry, 'name': f'test-role-{i}',
                'codepoints': [native] + ([alias] if alias else [])})
        path = self.root / 'all-test-only.json'
        path.write_text(json.dumps({'roles': roles}))
        output = self.root / 'all-test-only-font'
        manifest = ams.build(output, path)
        self.assertEqual(len(manifest['glyphs']), 32)
        self.assertEqual(len(manifest['cmap']), 64)

    def test_identical_build_bytes_and_previous_output_protected(self):
        path = self.source()
        first, second = self.root / 'one', self.root / 'two'
        ams.build(first, path, BASE)
        ams.build(second, path, BASE)
        self.assertEqual((first / ams.FONT_NAME).read_bytes(), (second / ams.FONT_NAME).read_bytes())
        self.assertEqual((first / 'build-manifest.json').read_bytes(), (second / 'build-manifest.json').read_bytes())
        with self.assertRaises(FileExistsError):
            ams.build(first, path, BASE)


if __name__ == '__main__':
    unittest.main()
