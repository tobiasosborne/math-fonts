"""Actual-source grid fits preserve similarity, source identity and math geometry."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ams = module('build_math_ams')
grid = module('calibrate_greek_grid')
PROFILE = ROOT / 'runs/greek-grid-2026-10-30/calibration-v1/calibration.json'
SOURCES = ROOT / 'runs/ams-coverage-2026-10-30/arrows-v1/sources.json'
BASE = ROOT / 'runs/pipeline-2026-10-30/font-sources.json'


class GreekGridTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_actual_landmarks_aspect_topology_and_line_metadata(self):
        profile = json.loads(PROFILE.read_text())
        out = self.directory / 'font'
        ams.build(out, SOURCES, BASE, PROFILE)
        result = grid.audit(out / ams.FONT_NAME, PROFILE, self.directory / 'audit.json')
        before, after = TTFont(grid.BEFORE), TTFont(out / ams.FONT_NAME)
        for name, entry in profile['roles'].items():
            b, a = entry['before_bounds_upm'], result['glyphs'][name]['after_bounds_upm']
            self.assertAlmostEqual((a[2]-a[0])/(a[3]-a[1]), (b[2]-b[0])/(b[3]-b[1]), places=5)
            pens = []
            for font in [before,after]:
                pen = RecordingPen(); font.getGlyphSet()[name].draw(pen); pens.append(pen)
            self.assertEqual(sum(op=='closePath' for op,_ in pens[0].value), sum(op=='closePath' for op,_ in pens[1].value))
            self.assertEqual(sum(op=='curveTo' for op,_ in pens[0].value), sum(op=='curveTo' for op,_ in pens[1].value))
        for name in set(before.getGlyphOrder())-set(profile['roles']):
            pens=[]
            for font in [before,after]:
                pen=RecordingPen();font.getGlyphSet()[name].draw(pen);pens.append(pen.value)
            self.assertEqual(pens[0],pens[1],name)
        self.assertEqual(after['MATH'].table.MathConstants.AccentBaseHeight.Value,476)
        self.assertEqual(after['MATH'].table.MathConstants.AxisHeight.Value,250)
        self.assertGreater(after['OS/2'].usWinAscent,after['hhea'].ascent)
        self.assertEqual((after['OS/2'].sTypoAscender,after['OS/2'].sTypoDescender,after['OS/2'].sTypoLineGap),(744,-271,48))
        self.assertNotIn(ord('x'),after.getBestCmap())

    def test_stale_source_landmarks_and_excessive_transforms_fail_closed(self):
        original=json.loads(PROFILE.read_text())
        bad=[]
        p=copy.deepcopy(original);p['roles']['alpha']['source_curves_sha256']='0'*64;bad.append(p)
        p=copy.deepcopy(original);p['roles']['alpha']['before_bounds_upm'][1]+=1;bad.append(p)
        p=copy.deepcopy(original);p['roles']['alpha']['uniform_scale']=1.2;bad.append(p)
        p=copy.deepcopy(original);del p['roles']['beta'];bad.append(p)
        for i,profile in enumerate(bad):
            path=self.directory/f'bad-{i}.json';path.write_text(json.dumps(profile))
            output=self.directory/f'font-{i}'
            with self.assertRaises(ValueError):ams.build(output,SOURCES,BASE,path)
            self.assertFalse(output.exists())

    def test_calibrated_binary_reproduces_and_uncalibrated_font_stays_identical(self):
        hashes=[]
        for i in range(2):
            result=ams.build(self.directory/f'build-{i}',SOURCES,BASE,PROFILE)
            hashes.append(result['font_sha256'])
        self.assertEqual(hashes[0],hashes[1])
        legacy=ams.build(self.directory/'legacy',SOURCES,BASE)
        self.assertEqual(legacy['font_sha256'],grid.sha(grid.BEFORE))

    def test_reference_hash_and_anatomy_review_are_mandatory(self):
        bad=self.directory/'not-a-font.otf';bad.write_bytes(b'wrong reference')
        with self.assertRaises(ValueError):grid.measure_text(bad)
        with self.assertRaises(ValueError):grid.anatomy(TTFont(grid.BEFORE),'sum')

    def test_pipeline_refuses_silent_uncalibrated_new_work(self):
        output=self.directory/'must-not-exist'
        result=subprocess.run([sys.executable,str(ROOT/'tools/run_math_ams.py'),
            '--output',str(output),'--base-sources',str(BASE),'--sources',str(SOURCES),
            '--text-font-dir','/not-needed-for-argument-validation'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Greek grid calibration is required',result.stderr)
        self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
