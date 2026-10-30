"""Opt-in actual-engine integration: glyph sourcing, scripts and missing coverage.

RUN_MATH_RUNTIME_INTEGRATION=1 .venv/bin/python -m unittest discover -s tests -p test_math_runtime.py
External commercial files are never copied into the test tree.
"""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / 'tools' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('runtime_test_builder', 'build_math_pilot.py')
proof = module('runtime_test_proof', 'proof_math_pilot.py')


@unittest.skipUnless(os.environ.get('RUN_MATH_RUNTIME_INTEGRATION') == '1',
                     'Set RUN_MATH_RUNTIME_INTEGRATION=1 for actual two-engine rendering')
class MathRuntimeIntegration(unittest.TestCase):
    def test_actual_two_engine_sourcing_and_hard_missing_coverage(self):
        text_dir = Path(os.environ.get('BASKERVILLE_TEXT_FONT_DIR',
                           '/home/tobias/.local/share/fonts/Baskerville 10 Pro'))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            builder.build(output / 'font')
            result = proof.build(output / 'font' / builder.FONT_NAME, text_dir,
                                 output / 'runtime', dpi=72)
            self.assertEqual(result['status'], 'passed')
            self.assertEqual(set(result['engines']), {'lualatex', 'xelatex'})
            for engine in result['engines'].values():
                self.assertEqual(set(engine['actual_pdf_fonts']), {*proof.STORM, proof.MATH})
                self.assertEqual(len(engine['role_checks']), len(proof.ROLES))
                self.assertTrue(engine['unsupported_gamma_hard_failure'])
                for role in engine['role_checks']:
                    self.assertGreater(role['glyph_count'], 0)
                    self.assertEqual(len(role['actual_fonts']), 1)
                    if role['role'].endswith('-scripts'):
                        self.assertGreaterEqual(len(role['sizes_pt']), 3)


if __name__ == '__main__':
    unittest.main()
