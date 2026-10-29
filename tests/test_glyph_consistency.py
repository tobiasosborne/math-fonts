import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from glyph_consistency_report import registered
from trace_glyph_trial import trace, render, fidelity


def asymmetric_ring():
    im = Image.new('L', (144, 216), 255)
    d = ImageDraw.Draw(im)
    d.ellipse((28, 50, 110, 160), fill=0)
    d.ellipse((48, 70, 90, 140), fill=255)
    d.rectangle((27, 110, 39, 190), fill=0)
    return im


class GlyphConsistencyTests(unittest.TestCase):
    def test_identical_raster_has_no_measured_drift(self):
        im = asymmetric_ring()
        _, _, m = registered(im, im)
        self.assertGreater(m['silhouette_iou'], .99)
        self.assertLess(m['boundary_mean_master_px'], .1)
        self.assertEqual(m['master_counters'], m['enlarged_counters'])

    def test_registration_cannot_hide_independent_width_stretch(self):
        im = asymmetric_ring()
        _, _, m = registered(im, im.resize((200, 216)))
        self.assertGreater(abs(m['aspect_change_fraction']), .25)
        self.assertLess(m['silhouette_iou'], .8)

    def test_potrace_bitmap_orientation_and_holes_survive_cairo(self):
        im = asymmetric_ring()
        paths, size, _ = trace(im)
        result = fidelity(im, render(paths, size, 8))
        self.assertGreater(result['own_source_iou'], .95)
        self.assertEqual(result['source_counters'], 1)
        self.assertEqual(result['vector_counters'], 1)


if __name__ == '__main__':
    unittest.main()
