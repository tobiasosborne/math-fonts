"""Real bounded atlas extraction: untouched pixels, honest calibration, immutable outputs."""
import importlib.util
import json
import shutil
import statistics
import tempfile
import unittest
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ams_atlas', REPO / 'tools/prepare_ams_atlas.py')
atlas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(atlas)


class AMSAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name) / 'atlas'
        cls.directory.mkdir()
        shutil.copyfile(atlas.DEFAULT / 'master.png', cls.directory / 'master.png')
        cls.manifest, cls.cal = atlas.prepare(cls.directory)
        cls.cells = {cell['name']: cell for cell in cls.manifest['cells']}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_crops_are_unmodified_source_rectangles_without_labels_or_grid(self):
        self.assertEqual(len(self.cells), 64)
        self.assertEqual(self.manifest['root_sha256'], atlas.EXPECTED_SHA)
        with Image.open(self.directory / 'master.png') as original:
            for name, cell in self.cells.items():
                with self.subTest(name=name), Image.open(self.directory / cell['crop']) as crop:
                    expected = original.crop(cell['source_crop_box'])
                    self.assertEqual(crop.mode, expected.mode)
                    self.assertEqual(crop.size, expected.size)
                    self.assertEqual(crop.tobytes(), expected.tobytes())
                    self.assertEqual(atlas.sha_bytes((self.directory / cell['crop']).read_bytes()), cell['crop_sha256'])
                    self.assertEqual(list(atlas.ink_bbox(crop)), cell['ink_bbox_in_crop'])
                    self.assertEqual(atlas.components(crop), cell['component_areas'])
                    self.assertEqual(cell['removed_ink_pixels_inside_crop'], 0)
                    self.assertFalse(cell['coverage_credit'])
                    self.assertFalse(cell['font_source_ready'])
                    window = self.manifest['row_ink_label_windows'][cell['row']-1]
                    self.assertLess(cell['source_crop_box'][3], window['label_dark_y_inclusive'][0])
                    left, top, right, bottom = cell['grid_cell_box']
                    x0, y0, x1, y1 = cell['source_crop_box']
                    self.assertGreater(x0, left)
                    self.assertGreater(y0, top)
                    self.assertLess(x1, right)
                    self.assertLess(y1, bottom)

    def test_quarantines_anchor_retention_and_phi_independent_review(self):
        self.assertEqual({name for name, cell in self.cells.items() if cell['quarantined']}, set(atlas.QUARANTINE))
        for name in atlas.ANCHORS:
            self.assertFalse(self.cells[name]['usable_as_design_reference'])
            self.assertEqual(self.cells[name]['status'], 'retained_v1_anchor_redraw_evidence_only')
        for name in atlas.QUARANTINE:
            self.assertFalse(self.cells[name]['usable_as_design_reference'])
        self.assertTrue(self.cells['phi-straight']['usable_as_design_reference'])
        self.assertIn('Independently reviewed', self.cells['phi-straight']['review_note'])
        self.assertEqual(self.cells['epsilon-lobed']['codepoints'], [0x3B5, 0x1D700])
        self.assertEqual(self.cells['epsilon-lobed']['tex_command'], '\\varepsilon')
        self.assertEqual(self.cells['epsilon-lunate']['codepoints'], [0x3F5, 0x1D716])
        self.assertEqual(self.cells['epsilon-lunate']['tex_command'], '\\epsilon')
        self.assertEqual(self.cells['phi-looped']['codepoints'], [0x3C6, 0x1D711])
        self.assertEqual(self.cells['phi-looped']['tex_command'], '\\varphi')
        self.assertEqual(self.cells['phi-straight']['codepoints'], [0x3D5, 0x1D719])
        self.assertEqual(self.cells['phi-straight']['tex_command'], '\\phi')
        self.assertEqual(self.cells['left-bracket']['tex_command'], '\\lbrack')
        self.assertNotIn('digamma', self.cells)
        self.assertEqual(self.cells['partial']['codepoints'], [0x2202, 0x1D715])

    def test_one_robust_em_and_baseline_model_reports_real_disagreement(self):
        observations = self.cal['anchors']
        self.assertEqual({o['name'] for o in observations}, atlas.ANCHORS)
        ratios = [o[k] for o in observations for k in ['width_ratio_v2_over_v1', 'height_ratio_v2_over_v1']]
        scale = statistics.median(ratios)
        self.assertEqual(self.cal['scale_v2_over_v1'], scale)
        self.assertEqual(self.cal['source_em_pixels'], 200*scale)
        self.assertAlmostEqual(scale, .6404308202154101)
        self.assertGreater(self.cal['comparison_height_ratio_median']-self.cal['comparison_width_ratio_median'], .05)
        self.assertGreater(self.cal['rms_dimension_residual_pixels'], 5)
        self.assertEqual(self.cal['unanchored_greek_rows'], [3])
        self.assertIn('uncertain', self.cal['status'])
        for cell in self.cells.values():
            proposal = cell.get('builder_calibration_proposal')
            if cell['row'] > 4:
                self.assertIsNone(proposal)
                continue
            self.assertEqual(proposal['source_em_pixels'], self.cal['source_em_pixels'])
            self.assertEqual(proposal['baseline_root'],
                cell['grid_cell_box'][1]+self.cal['row_baseline_offset_pixels'])
            reg = proposal['registration_to_root_for_unresized_crop']
            self.assertEqual(reg['scale'], 1)
            self.assertEqual([reg['translate_x'], reg['translate_y']], cell['source_crop_box'][:2])
            self.assertNotIn('curves', proposal)
            self.assertNotIn('provenance', proposal)

    def test_deterministic_rerun_and_conflicts_do_not_replace_evidence(self):
        paths = list(self.directory.rglob('*'))
        before = {p.relative_to(self.directory): p.read_bytes() for p in paths if p.is_file()}
        atlas.prepare(self.directory)
        after = {p.relative_to(self.directory): p.read_bytes() for p in self.directory.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'copy'
            shutil.copytree(self.directory, target)
            (target / 'calibration.json').write_bytes(b'preserve conflicting evidence')
            with self.assertRaisesRegex(FileExistsError, 'Immutable evidence differs'):
                atlas.prepare(target)
            self.assertEqual((target / 'calibration.json').read_bytes(), b'preserve conflicting evidence')
            self.assertEqual((target / 'master.png').read_bytes(), before[Path('master.png')])

    def test_wrong_root_and_missing_grid_fail_before_artifact_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            Image.new('RGB', (1024, 1536), 'white').save(target / 'master.png')
            with self.assertRaisesRegex(ValueError, 'Wrong candidate image hash'):
                atlas.prepare(target)
            self.assertEqual(list(target.iterdir()), [target / 'master.png'])
        with self.assertRaisesRegex(ValueError, 'nine measured'):
            atlas.grid_and_windows(Image.new('RGB', (1024, 1536), 'white'))


if __name__ == '__main__':
    unittest.main()
