"""Actual-engine integration and exact semantic/source contract for AMS reuse."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('test_ams_runtime_proof', REPO / 'tools/proof_ams_runtime.py')
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)


class SourceContract(unittest.TestCase):
    def test_authored_overlay_priority_and_exact_arrow_allowlist(self):
        class Name:
            def __init__(self, value):
                self.value = value
            def getDebugName(self, key):
                return self.value
        class Authored:
            def __init__(self, name):
                self.name = Name(name)
            def __getitem__(self, key):
                return self.name
            def getBestCmap(self):
                return {0x2b: 'plus', 0x2192: 'arrow_right', 0x21c0: 'harpoon_right_up'}
        name = 'BaskervilleCompanionMath-AMS'
        authored = Authored(name)
        rows = {r['command']: r for r in proof.mappings(authored)}
        self.assertEqual(rows['\\rightarrow']['expected_font'], name)
        self.assertEqual(rows['\\to']['expected_font'], name)
        self.assertEqual(rows['\\rightharpoonup']['codepoint'], 0x21c0)
        self.assertEqual(rows['\\rightharpoonup']['math_class'], 'mathrel')
        self.assertEqual(rows['\\leftarrow']['expected_font'], proof.pilot.UP)
        self.assertNotIn('\\twoheadleftarrow', rows)
        self.assertNotIn('\\hookrightarrow', rows)
        literal = {r['codepoint']: r for r in proof.literal_mappings(authored)}
        self.assertEqual(literal[0x2192]['expected_font'], name)
        self.assertEqual(literal[0x2b]['expected_font'], name)
        self.assertEqual(literal[0x2190]['expected_font'], proof.pilot.UP)
        old = {r['command']: r for r in proof.mappings(Authored(proof.pilot.MATH))}
        self.assertEqual(old['\\rightarrow']['expected_font'], proof.pilot.UP)
        aliases = {r['command']: r for r in proof.arrow_allowlist()}
        self.assertEqual(aliases['\\mapsto']['codepoint'], 0x21a6)
        self.assertEqual(aliases['\\twoheadrightarrow']['codepoint'], 0x21a0)
        self.assertNotEqual(aliases['\\twoheadrightarrow']['codepoint'], aliases['\\rightarrow']['codepoint'])

    def test_exact_bindings_and_opt_in_greek_shape_identities(self):
        rows = proof.mappings()
        stock = {r['command']: r for r in rows if r['declaration'] != 'native_Greek_opt_in'}
        native = {r['command']: r for r in rows if r['declaration'] == 'native_Greek_opt_in'}
        self.assertEqual(stock['\\centerdot']['codepoint'], 0x00b7)
        self.assertEqual(stock['\\eth']['math_class'], 'mathord')
        self.assertEqual(stock['\\lozenge']['codepoint'], 0x25ca)
        self.assertEqual(stock['\\lbrace']['math_class'], 'mathopen')
        self.assertEqual(stock['\\rbrace']['math_class'], 'mathclose')
        self.assertEqual(stock['\\}']['codepoint'], 0x7d)
        for name in ('\\sum', '\\int', '\\sqrt', '\\alpha', '\\beta', '\\|', '\\cdot'):
            self.assertNotIn(name, stock)
        self.assertEqual(native['\\varepsilon']['codepoint'], 0x3b5)
        self.assertEqual(native['\\varphi']['codepoint'], 0x3c6)
        for name in ('\\epsilon', '\\phi', '\\vartheta', '\\varkappa', '\\varrho', '\\varpi'):
            self.assertNotIn(name, native)
        self.assertEqual(len(native), 49)


@unittest.skipUnless(os.environ.get('RUN_AMS_RUNTIME_INTEGRATION') == '1',
                     'Set RUN_AMS_RUNTIME_INTEGRATION=1 for actual two-engine proofs')
class RenderedRuntime(unittest.TestCase):
    def test_explicit_overlay_reuses_authored_signs_before_stock(self):
        # A renamed copy of our own original pilot is a temporary loader
        # fixture, not a new design. It supplies real authored plus/minus/equals
        # so the priority branch is checked by actual PDF glyph fonts.
        from fontTools.ttLib import TTFont
        text_dir = Path(os.environ.get('BASKERVILLE_TEXT_FONT_DIR', '/home/tobias/.local/share/fonts/Baskerville 10 Pro'))
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            font = TTFont(proof.PILOT_FONT)
            name = 'BaskervilleCompanionMath-AMSOverlayTest'
            for record in font['name'].names:
                if record.nameID in (1, 4, 6):
                    record.string = name.encode(record.getEncoding())
            font['CFF '].cff.fontNames = [name]
            top = font['CFF '].cff.topDictIndex[0]
            top.FullName = top.FamilyName = name
            fixture = directory / (name + '.otf')
            font.save(fixture)
            result = proof.build(fixture, text_dir, directory / 'runtime', dpi=72, baseline=False)
            for engine in result['engines'].values():
                checks = {row['label']: row for row in engine['isolated_command_checks']}
                self.assertEqual(checks['literal:U+002B']['actual_fonts'], [name])
                self.assertEqual(checks['literal:U+2212']['actual_fonts'], [name])
                self.assertEqual(checks['literal:U+003D']['actual_fonts'], [name])
                self.assertEqual(checks['stock:\\rightarrow']['actual_fonts'], [proof.pilot.UP])
                self.assertEqual(checks['pilot-role:custom-symbols']['actual_fonts'], [name])

    def test_actual_exact_commands_and_native_alternate_scoping(self):
        font = Path(os.environ.get('AMS_RUNTIME_FONT', str(proof.PILOT_FONT)))
        text_dir = Path(os.environ.get('BASKERVILLE_TEXT_FONT_DIR', '/home/tobias/.local/share/fonts/Baskerville 10 Pro'))
        with tempfile.TemporaryDirectory() as temp:
            result = proof.build(font, text_dir, Path(temp) / 'runtime', dpi=72)
            self.assertEqual(result['status'], 'passed')
            self.assertTrue({'\\centerdot', '\\eth', '\\lozenge'} <= set(result['coverage']['direct_amssymb_implemented']))
            self.assertEqual(result['unchanged_pilot_regression'], {'lualatex': 20, 'xelatex': 20})
            for engine in result['engines'].values():
                checks = engine['isolated_command_checks']
                self.assertEqual(len([c for c in checks if c['label'].startswith('pilot-role:')]), 20)
                self.assertGreater(len(checks), 180)
                self.assertEqual(set(engine['actual_pdf_fonts']), {*proof.pilot.STORM, result['math_postscript_name']})
                self.assertGreaterEqual(len(engine['hard_missing_failures']), 9)
                for check in checks:
                    self.assertEqual(set(check['actual_fonts']), set(check['expected_fonts']))
                    self.assertGreater(check['glyph_count'], 0)


if __name__ == '__main__':
    unittest.main()
