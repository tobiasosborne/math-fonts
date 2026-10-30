"""Geometry, semantic and actual CFF integration checks for the authored arrows."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

ROOT=Path(__file__).resolve().parents[1]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

arrows=module('math_arrows',ROOT/'tools/build_math_arrows.py')
ams=module('ams_arrow_test_builder',ROOT/'tools/build_math_ams.py')


class MathArrowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar=json.loads(arrows.GRAMMAR.read_text())
        cls.specs={s['name']:s for s in arrows.specs()}
        cls.paths={n:arrows.arrow(s,cls.grammar)[0] for n,s in cls.specs.items()}
        cls.temp=tempfile.TemporaryDirectory()
        cls.output=Path(cls.temp.name)/'arrows'
        cls.report=arrows.build(cls.output)
        cls.manifest=cls.output/'sources.json'

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def assertShapeEqual(self,a,b,tolerance=.1):
        difference=pathops.op(a,b,pathops.PathOp.XOR)
        self.assertLess(abs(difference.area),tolerance)

    def test_exact_finite_unicode_scope_and_no_semantic_placeholders(self):
        expected=set(range(0x2190,0x219A))|set(range(0x21A4,0x21A8))|set(range(0x21D0,0x21D6))|set(range(0x21BC,0x21C4))|set(range(0x27F5,0x27FB))
        self.assertEqual({s['codepoint'] for s in self.specs.values()},expected)
        self.assertEqual(len(self.specs),34)
        self.assertFalse(any('twohead' in n or 'hook' in n for n in self.specs))

    def test_exact_orientation_and_shared_head_for_long_forms(self):
        right=self.paths['arrow_right']
        for n,angle in [('arrow_left',180),('arrow_up',90),('arrow_down',270),('arrow_northeast',45),('arrow_northwest',135)]:
            self.assertShapeEqual(self.paths[n],arrows.rotate(right,angle))
        _,normalparts=arrows.arrow(self.specs['arrow_right'],self.grammar)
        _,longparts=arrows.arrow(self.specs['arrow_long_right'],self.grammar)
        # Long arrows translate the same head by half the extra shaft length.
        self.assertShapeEqual(normalparts[0].transform(1,0,0,1,300,0),longparts[0])
        self.assertEqual({m['shaft_thickness'] for m in self.report['metrics']},{40})
        self.assertEqual({m['head_length'] for m in self.report['metrics']},{190})

    def test_harpoon_halves_bar_and_double_shafts_have_distinct_semantics(self):
        upper=self.paths['harpoon_right_up'];lower=self.paths['harpoon_right_down']
        self.assertShapeEqual(upper.transform(1,0,0,-1,0,0),lower)
        self.assertGreater(abs(pathops.op(upper,lower,pathops.PathOp.XOR).area),1000)
        self.assertTrue(self.paths['arrow_right'].contains((0,0)))
        self.assertFalse(self.paths['arrow_double_right'].contains((0,0)))
        self.assertTrue(self.paths['arrow_double_right'].contains((0,60)))
        self.assertTrue(self.paths['arrow_frombar_right'].contains((-400,100)))
        self.assertFalse(self.paths['arrow_right'].contains((-400,100)))
        # Up-right harpoon's sole wing is to the right at its upper end.
        self.assertGreater(self.paths['harpoon_up_right'].bounds[2],100)
        self.assertLess(abs(self.paths['harpoon_up_right'].bounds[0]),30)

    def test_double_shaft_end_follows_curve_without_protruding_rectangle(self):
        spec=self.specs['arrow_double_right'];full,parts=arrows.arrow(spec,self.grammar)
        self.assertAlmostEqual(arrows.head_intersection_x(400,60,self.grammar),294.880261889006,places=5)
        clip=arrows.head_interior(400,-500,self.grammar)
        # Both shaft stripes lie entirely on the interior side of the actual
        # cubic at every y, not merely at their centerline join.
        for stripe in parts[1:]:
            self.assertLess(abs(pathops.op(stripe,clip,pathops.PathOp.DIFFERENCE).area),.01)
        self.assertGreater(abs(full.area),abs(parts[0].area))

    def test_union_topology_is_connected_and_keeps_double_arrow_counter(self):
        for row in self.report['metrics']:
            expected=2 if row.get('double') and row['ends']=='both' else 1
            self.assertEqual(row['contours'],expected,row['name'])
            self.assertGreater(row['area_design_units2'],0)
        self.assertFalse(self.paths['arrow_double_leftright'].contains((0,0)))
        self.assertTrue(self.paths['arrow_double_leftright'].contains((0,60)))

    def test_declared_frame_and_compiled_cff_are_valid_without_stock_outlines(self):
        entries,_=ams.load_sources(self.manifest)
        for name,e in entries.items():
            self.assertEqual(e['frame_kind'],'derived_design_units')
            self.assertFalse(e['provenance']['root_frame_registration_claimed'])
            self.assertFalse(e['provenance']['raster_fit_claimed'])
            self.assertFalse(e['provenance']['donor_outlines'])
            self.assertTrue(e['root_image_verified'])
        destination=Path(self.temp.name)/'font'
        ams.build(destination,sources=self.manifest)
        with TTFont(destination/ams.FONT_NAME) as font:
            self.assertIn('CFF ',font);self.assertIn('MATH',font)
            self.assertEqual(set(font.getBestCmap()),{32}|{s['codepoint'] for s in self.specs.values()})
            self.assertFalse(set(range(48,58))&set(font.getBestCmap()))
            for name in self.specs:
                pen=RecordingPen();font.getGlyphSet()[name].draw(pen)
                self.assertTrue(any(op=='curveTo' for op,_ in pen.value),name)
                self.assertEqual(sum(op=='closePath' for op,_ in pen.value),
                    next(r['contours'] for r in self.report['metrics'] if r['name']==name))

    def test_outputs_are_immutable(self):
        with self.assertRaises(FileExistsError):arrows.build(self.output)


if __name__=='__main__':unittest.main()
