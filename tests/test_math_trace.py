import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from math_trace import bitmap_words, export, fidelity, foreground, np, topology, trace_image, trace_mask


def blank(size=(197, 143)):
    return Image.new('L', size, 255)


def equals():
    image = blank()
    draw = ImageDraw.Draw(image)
    draw.rectangle((23, 36, 162, 49), fill=0)
    draw.rectangle((23, 88, 162, 101), fill=0)
    return image


def dotted_j():
    image = blank()
    draw = ImageDraw.Draw(image)
    draw.ellipse((122, 12, 140, 30), fill=0)
    draw.rectangle((125, 52, 136, 110), fill=0)
    draw.arc((83, 86, 136, 129), 0, 180, fill=0, width=12)
    return image


def ellipsis():
    image = blank()
    draw = ImageDraw.Draw(image)
    for x in (21, 91, 161):
        draw.ellipse((x, 90, x + 15, 105), fill=0)
    return image


def counters():
    image = blank()
    draw = ImageDraw.Draw(image)
    draw.rectangle((19, 24, 89, 122), fill=0)
    draw.ellipse((32, 34, 76, 67), fill=255)
    draw.ellipse((32, 80, 76, 111), fill=255)
    # Isolated ink with a one-pixel counter must not be filtered out.
    draw.rectangle((151, 30, 163, 42), fill=0)
    draw.point((157, 36), fill=255)
    return image


class MathTraceTests(unittest.TestCase):
    def assert_survives(self, image, components, holes, minimum_iou=.96):
        paths, rerender, report = trace_image(image, supersample=8)
        metrics = report['fidelity']
        self.assertEqual(rerender.size, image.size)
        self.assertEqual(metrics['source_topology']['component_count'], components)
        self.assertEqual(metrics['source_topology']['counter_count'], holes)
        self.assertTrue(report['topology_preserved'], report)
        self.assertEqual(report['positive_contours'], components)
        self.assertEqual(report['negative_contours'], holes)
        self.assertGreater(metrics['full_canvas_iou'], minimum_iou)
        return paths, rerender, report

    def test_equals_preserves_both_bands_and_empty_gap(self):
        _, rerender, _ = self.assert_survives(equals(), 2, 0)
        mask = np.asarray(rerender) < 128
        self.assertTrue(mask[42, 90])
        self.assertTrue(mask[94, 90])
        self.assertFalse(mask[68].any())

    def test_dotted_j_preserves_dot_and_disconnected_stem(self):
        _, rerender, _ = self.assert_survives(dotted_j(), 2, 0)
        mask = np.asarray(rerender) < 128
        self.assertTrue(mask[21, 131])
        self.assertTrue(mask[75, 131])
        self.assertFalse(mask[41].any())

    def test_ellipsis_preserves_all_three_marks(self):
        _, rerender, _ = self.assert_survives(ellipsis(), 3, 0, minimum_iou=.93)
        for x in (28, 98, 168):
            self.assertLess(rerender.getpixel((x, 97)), 128)

    def test_all_counters_including_one_pixel_hole_are_reported(self):
        _, _, report = self.assert_survives(counters(), 2, 3)
        self.assertIn(1, report['fidelity']['source_topology']['counter_areas'])
        self.assertIn(1, report['fidelity']['render_topology']['counter_areas'])

    def test_asymmetric_orientation_and_non_word_aligned_width(self):
        image = blank((197, 143))
        draw = ImageDraw.Draw(image)
        draw.polygon([(12, 17), (33, 17), (33, 96), (92, 96), (92, 113), (12, 113)], fill=0)
        draw.rectangle((169, 26, 184, 45), fill=0)
        _, rerender, report = self.assert_survives(image, 2, 0)
        self.assertEqual(report['fidelity']['source_topology']['ink_bbox'], [12, 17, 185, 114])
        for flipped in (image.transpose(Image.Transpose.FLIP_LEFT_RIGHT), image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)):
            self.assertLess(fidelity(np.asarray(flipped), rerender)['full_canvas_iou'], .4)
        self.assertLess(rerender.getpixel((20, 24)), 128)
        self.assertGreater(rerender.getpixel((176, 118)), 128)

    def test_bitmap_word_boundaries_are_msb_first_without_row_bleed(self):
        mask = np.zeros((3, 131), dtype=bool)
        mask[0, [0, 63, 64, 127, 130]] = True
        mask[1, [2, 70]] = True
        words = bitmap_words(mask)
        bits = words.dtype.itemsize * 8
        decoded = np.zeros_like(mask)
        for y in range(mask.shape[0]):
            for x in range(mask.shape[1]):
                decoded[y, x] = bool(int(words[y, x // bits]) & (1 << (bits - 1 - x % bits)))
        np.testing.assert_array_equal(decoded, mask)

    def test_single_pixel_components_are_never_despeckled(self):
        image = blank((71, 39))
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, 24, 25), fill=0)
        draw.point((65, 31), fill=0)
        paths, rerender, report = self.assert_survives(image, 2, 0)
        self.assertEqual(len(paths), 2)
        self.assertEqual(report['extraction']['removed_ink_pixels'], 0)
        self.assertLess(rerender.getpixel((65, 31)), 128)

    def test_transparent_hidden_black_composites_white_before_threshold(self):
        image = Image.new('RGBA', (71, 39), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, 24, 25), fill=(0, 0, 0, 255))
        draw.rectangle((40, 8, 49, 25), fill=(0, 0, 0, 127))
        gray, mask, metadata = foreground(image)
        self.assertEqual(gray[0, 0], 255)
        self.assertEqual(gray[12, 44], 128)
        self.assertFalse(mask[12, 44])
        self.assertEqual(mask.sum(), 17 * 18)
        self.assertEqual(metadata['alpha_background'], 'white')
        self.assert_survives(image, 1, 0)

    def test_palette_transparency_uses_same_white_composite(self):
        image = Image.new('P', (13, 13), 0)
        image.putpalette([0, 0, 0, 0, 0, 0] + [255] * (768 - 6))
        image.info['transparency'] = 0
        ImageDraw.Draw(image).rectangle((4, 4, 8, 8), fill=1)
        gray, mask, metadata = foreground(image)
        self.assertEqual(gray[0, 0], 255)
        self.assertEqual(mask.sum(), 25)
        self.assertTrue(metadata['alpha_present'])

    def test_color_conversion_requires_explicit_choice(self):
        image = Image.new('RGB', (31, 31), 'white')
        ImageDraw.Draw(image).rectangle((8, 8, 20, 20), fill=(150, 0, 0))
        with self.assertRaisesRegex(ValueError, 'Chromatic'):
            foreground(image)
        _, mask, metadata = foreground(image, allow_color=True)
        self.assertEqual(mask.sum(), 13 * 13)
        self.assertEqual(metadata['chromatic_pixels_after_compositing'], 13 * 13)

    def test_empty_unsupported_and_invalid_inputs_are_rejected(self):
        for image in (blank(), Image.new('RGBA', (10, 10), (0, 0, 0, 0))):
            with self.assertRaisesRegex(ValueError, 'No ink'):
                foreground(image)
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            foreground(Image.new('I', (10, 10)))
        with self.assertRaises(ValueError):
            trace_mask(np.zeros((4, 4), dtype=bool))
        with self.assertRaises(ValueError):
            trace_mask(np.ones((4, 4), dtype=np.uint8))
        with self.assertRaises(ValueError):
            trace_image(equals(), supersample=0)
        with self.assertRaises(ValueError):
            trace_image(equals(), tolerance_px=float('nan'))

    def test_missing_tiny_mark_fails_topology_check_and_fidelity(self):
        image = ellipsis()
        result = image.copy()
        ImageDraw.Draw(result).rectangle((150, 80, 190, 115), fill=255)
        metrics = fidelity(np.asarray(image), result)
        self.assertFalse(metrics['raster_topology_preserved'])
        self.assertEqual(metrics['source_topology']['component_count'], 3)
        self.assertEqual(metrics['render_topology']['component_count'], 2)
        self.assertLess(metrics['full_canvas_iou'], .7)

    def test_equal_component_counts_do_not_hide_a_relocated_mark(self):
        image = ellipsis()
        result = image.copy()
        draw = ImageDraw.Draw(result)
        draw.rectangle((150, 80, 190, 115), fill=255)
        draw.ellipse((161, 20, 176, 35), fill=0)
        metrics = fidelity(np.asarray(image), result)
        self.assertTrue(metrics['topology_checks']['component_count_equal'])
        self.assertFalse(metrics['raster_topology_preserved'])
        self.assertFalse(metrics['topology_checks']['each_source_component_has_one_spatial_match'])

    def test_canvas_edge_ink_and_nested_counter_topology(self):
        image = blank((41, 41))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 40, 40), fill=0)
        draw.rectangle((8, 8, 32, 32), fill=255)
        draw.rectangle((16, 16, 24, 24), fill=0)
        _, _, report = self.assert_survives(image, 2, 1)
        self.assertTrue(report['fidelity']['source_topology']['ink_touches_canvas_edge'])

    def test_fresh_export_and_cli_write_real_curve_handles_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'equals.png'
            output = Path(temp) / 'trace'
            equals().save(source)
            process = subprocess.run([sys.executable, str(ROOT / 'tools/math_trace.py'),
                                      '--input', str(source), '--output', str(output)],
                                     text=True, capture_output=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertTrue(json.loads(process.stdout)['topology_preserved'])
            self.assertEqual({p.name for p in output.iterdir()},
                             {'filled.svg', 'handles.svg', 'rerender.png', 'curves.json', 'metrics.json'})
            root = ET.parse(output / 'filled.svg').getroot()
            self.assertEqual(root.attrib['viewBox'], '0 0 197 143')
            handles = (output / 'handles.svg').read_text()
            self.assertIn('#2277dd', handles)
            self.assertIn('<circle', handles)
            report = json.loads((output / 'metrics.json').read_text())
            self.assertEqual(report['fidelity']['source_topology']['component_count'], 2)
            self.assertEqual(report['extraction']['removed_ink_pixels'], 0)
            before = (output / 'metrics.json').read_bytes()
            with self.assertRaises(FileExistsError):
                export(source, output)
            self.assertEqual(before, (output / 'metrics.json').read_bytes())

    def test_handle_control_points_are_actual_curve_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp) / 'dots.png', Path(temp) / 'out'
            ellipsis().save(source)
            export(source, output)
            paths = json.loads((output / 'curves.json').read_text())['paths']
            segments = [s for p in paths for s in p['segments'] if s['tag'] == 1]
            self.assertTrue(segments)
            root = ET.parse(output / 'handles.svg').getroot()
            ns = {'s': 'http://www.w3.org/2000/svg'}
            handle_paths = [e.attrib['d'] for e in root.findall('s:path', ns) if e.attrib.get('stroke') == '#2277dd']
            self.assertEqual(len(handle_paths), 2 * len(segments))
            a = segments[0]['points'][0]
            self.assertTrue(any(d.endswith(f'L{a[0]},{a[1]}') for d in handle_paths))


if __name__ == '__main__':
    unittest.main()
