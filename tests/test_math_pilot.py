"""End-to-end CFF/MATH and registration invariants for the bounded custom pilot."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('math_pilot', REPO / 'tools/build_math_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class MathPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / 'font'
        cls.manifest = pilot.build(cls.output)
        cls.font = TTFont(cls.output / pilot.FONT_NAME)

    @classmethod
    def tearDownClass(cls):
        cls.font.close()
        cls.temp.cleanup()

    def test_custom_only_cmap_and_real_cubic_font(self):
        font = self.font
        self.assertIn('CFF ', font)
        self.assertIn('MATH', font)
        self.assertNotIn('glyf', font)
        self.assertEqual(font['head'].unitsPerEm, 1000)
        cmap = font.getBestCmap()
        self.assertEqual(set(cmap), {32} | {cp for cps in pilot.ROLES.values() for cp in cps})
        for cp in [ord(c) for c in 'AHOfxd0123456789']:
            self.assertNotIn(cp, cmap)
        for name, cps in pilot.GREEK.items():
            for cp in cps:
                self.assertEqual(cmap[cp], name)
        for name in pilot.ROLES:
            source = json.loads(Path(self.manifest['glyphs'][name]['curves']).read_text())
            pen = RecordingPen()
            font.getGlyphSet()[name].draw(pen)
            self.assertEqual(sum(op == 'closePath' for op, _ in pen.value), len(source['paths']))
            if any(seg['tag'] == 1 for contour in source['paths'] for seg in contour['segments']):
                self.assertTrue(any(op == 'curveTo' for op, _ in pen.value), name)
            for actual, expected in zip(pilot.bounds(pen), self.manifest['glyphs'][name]['bounds_upm']):
                self.assertAlmostEqual(actual, expected, places=3)

    def test_math_constants_and_variant_references(self):
        math = self.font['MATH'].table
        for name, expected in pilot.CONSTANTS.items():
            actual = getattr(math.MathConstants, name)
            self.assertEqual(getattr(actual, 'Value', actual), expected, name)
        variants = math.MathVariants
        valid = set(self.font.getGlyphOrder())
        self.assertEqual(set(variants.VertGlyphCoverage.glyphs), {'left-paren', 'right-paren', 'radical', 'sum', 'integral'})
        for construction in variants.VertGlyphConstruction + variants.HorizGlyphConstruction:
            self.assertIsNone(construction.GlyphAssembly)
            measures = []
            for record in construction.MathGlyphVariantRecord:
                self.assertIn(record.VariantGlyph, valid)
                measures.append(record.AdvanceMeasurement)
            self.assertEqual(measures, sorted(set(measures)))
        for name, construction in zip(variants.VertGlyphCoverage.glyphs, variants.VertGlyphConstruction):
            if name in ['left-paren', 'right-paren']:
                self.assertGreater(construction.MathGlyphVariantRecord[-1].AdvanceMeasurement, 2800)
        info = math.MathGlyphInfo
        self.assertEqual(set(info.MathItalicsCorrectionInfo.Coverage.glyphs), set(pilot.GREEK))
        self.assertTrue(set(pilot.GREEK) <= set(info.MathTopAccentAttachment.TopAccentCoverage.glyphs))

    def test_math_script_is_discoverable_without_fabricated_optical_forms(self):
        table=self.font['GPOS'].table
        self.assertIn('math',[r.ScriptTag for r in table.ScriptList.ScriptRecord])
        gsub = self.font['GSUB'].table
        self.assertEqual([r.ScriptTag for r in gsub.ScriptList.ScriptRecord], ['math'])
        self.assertEqual(gsub.FeatureList.FeatureCount, 0)
        self.assertEqual(gsub.LookupList.LookupCount, 0)

    def test_radical_connector_overlaps_advance_and_preserves_roof(self):
        font = self.font
        glyphs = font.getGlyphSet()
        for name in ['radical', 'radical.size1', 'radical.size2']:
            pen = RecordingPen()
            glyphs[name].draw(pen)
            bb = pilot.bounds(pen)
            advance = font['hmtx'][name][0]
            self.assertGreaterEqual(bb[2]-advance, 20)
            self.assertLess(bb[2]-advance, 21)
            # All three finite roof strips retain the source 50-UPM thickness,
            # matching the engine rule rather than scaling to 75/100 UPM.
            roof_y = [p[1] for op, pts in pen.value for p in pts
                      if p[1] >= bb[3]-50.001]
            self.assertAlmostEqual(max(roof_y)-min(roof_y), 50, places=3)
        self.assertEqual(font['MATH'].table.MathConstants.RadicalRuleThickness.Value, 50)

    def test_hat_uses_positive_bearings_and_explicit_center_attachment(self):
        font = self.font
        attachments = font['MATH'].table.MathGlyphInfo.MathTopAccentAttachment
        anchors = dict(zip(attachments.TopAccentCoverage.glyphs,
                           [v.Value for v in attachments.TopAccentAttachment]))
        for name in ['hat-accent', 'hat-accent.wide1', 'hat-accent.wide2']:
            pen = RecordingPen()
            font.getGlyphSet()[name].draw(pen)
            bb = pilot.bounds(pen)
            advance, lsb = font['hmtx'][name]
            self.assertAlmostEqual(bb[1], pilot.CONSTANTS['AccentBaseHeight']+25, places=3)
            self.assertGreater(advance, 0)
            self.assertGreater(lsb, 0)
            self.assertLess(bb[2], advance)
            self.assertLess(abs(anchors[name]-(bb[0]+bb[2])/2), .501)

    def test_uniform_registration_recovers_identical_root_geometry(self):
        # A translated 4x enlargement of every control point must recover the
        # exact same root outline, baseline and metrics without width fitting.
        entry = pilot.defaults()['alpha']
        raw, count = pilot.outline(entry)
        data = json.loads(Path(entry['curves']).read_text())
        for contour in data['paths']:
            for segment in contour['segments']:
                segment['points'] = [[x*4+12, y*4+20] for x, y in segment['points']]
        path = Path(self.temp.name) / 'enlarged-curves.json'
        path.write_text(json.dumps(data))
        xoff, yoff = entry['registration']['offset_root']
        overridden = {**entry, 'curves': str(path),
                      'registration': {'scale': .25, 'offset_root': [xoff-3, yoff-5]}}
        other, other_count = pilot.outline(overridden)
        self.assertEqual(count, other_count)
        for (op, points), (other_op, other_points) in zip(raw.value, other.value):
            self.assertEqual(op, other_op)
            for p, q in zip(points, other_points):
                self.assertAlmostEqual(p[0], q[0], places=9)
                self.assertAlmostEqual(p[1], q[1], places=9)
        self.assertAlmostEqual(pilot.bounds(raw)[3], pilot.bounds(other)[3], places=9)

    def test_parent_override_interface_and_reject_unregistered_input(self):
        path = Path(self.temp.name) / 'sources.json'
        entry = pilot.defaults()['alpha']
        path.write_text(json.dumps({'sources': {'alpha': {'curves': entry['curves'],
            'registration_to_root': {'scale': 1, 'translate_x': 776, 'translate_y': 22}}}}))
        overridden = pilot.load_sources(path)['alpha']
        self.assertEqual(overridden['registration'], entry['registration'])
        path.write_text(json.dumps({'sources': {'alpha': {'curves': entry['curves']}}}))
        with self.assertRaises(ValueError):
            pilot.load_sources(path)

    def test_repeat_build_is_identical_and_prior_build_is_protected(self):
        other = Path(self.temp.name) / 'repeat'
        pilot.build(other)
        self.assertEqual((self.output / pilot.FONT_NAME).read_bytes(), (other / pilot.FONT_NAME).read_bytes())
        with self.assertRaises(FileExistsError):
            pilot.build(self.output)


if __name__ == '__main__':
    unittest.main()
