import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from arena_council import choose


def rows(a=2, b=2, difference=None):
    return [dict(id=f'R{i}', score_a=(difference[1] if difference and difference[0] == f'R{i}' else a),
                 score_b=b) for i in range(1, 9)]


class ArenaTests(unittest.TestCase):
    def test_majority_allows_explicit_tradeoff(self):
        r = choose({'opus': 'A', 'sol': 'A', 'muse': 'B'},
                   {m: rows(difference=('R5', 1)) for m in ['opus', 'sol', 'muse']},
                   True, {'A': 'commercial', 'B': 'storm'})
        self.assertEqual(r['advancer'], 'commercial')
        self.assertTrue(r['competitive'])
        self.assertFalse(r['low_confidence'])

    def test_tie_prioritizes_identity_then_optical(self):
        r = choose({'opus': 'A', 'sol': 'B', 'muse': 'tie'},
                   {'opus': rows(difference=('R4', 1)), 'sol': rows(difference=('R4', 1)), 'muse': rows()},
                   True, {'A': 'storm', 'B': 'typotheque'})
        self.assertEqual(r['advancer'], 'typotheque')
        self.assertEqual(r['tiebreak_criterion'], 'R4')

    def test_draw_and_missing_panel_never_become_quality_win(self):
        key = {'A': 'typotheque', 'B': 'storm'}
        for prefs, complete in [({'opus': 'tie', 'sol': 'tie', 'muse': 'tie'}, True),
                                ({'opus': 'A', 'sol': 'A'}, False)]:
            r = choose(prefs, {m: rows() for m in prefs}, complete, key)
            self.assertEqual(r['advancer'], 'storm')
            self.assertFalse(r['competitive'])
            self.assertTrue(r['low_confidence'])
