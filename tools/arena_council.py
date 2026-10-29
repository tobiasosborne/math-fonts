#!/usr/bin/env python3
"""Prepare anonymous compiled-font matches and apply the frozen arena rule.

No model calls. Each match has exactly one external three-member panel.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

import jsonschema

from campaign_council import MEMBERS, freeze, validate

ROOT = Path(__file__).resolve().parents[1]
ARENA = ROOT / 'runs/arena-2026-10-29'
SEEDS = {'storm': 1, 'hoefler': 2, 'commercial': 3, 'typotheque': 4}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def choose(preferences, criteria, complete, key):
    """Preserve abstentions, tradeoffs and administrative advancements explicitly."""
    administrative = min(key, key=lambda side: SEEDS[key[side]])
    counts = {s: sum(p == s for p in preferences.values()) for s in ['A', 'B', 'tie']}
    result = {'votes': counts, 'competitive': False, 'tiebreak_criterion': None}
    if not complete:
        side, reason = administrative, 'Incomplete panel; seed advancement only, no demonstrated win.'
    elif counts['A'] != counts['B']:
        side = 'A' if counts['A'] > counts['B'] else 'B'
        reason = 'More non-tied panel preferences.'
        result['competitive'] = True
    else:
        side = None
        for cid in ['R5', 'R4', 'R2']:
            rows = [next(c for c in cs if c['id'] == cid) for cs in criteria.values()]
            av = sum(c['score_a'] > c['score_b'] for c in rows)
            bv = sum(c['score_b'] > c['score_a'] for c in rows)
            if av != bv:
                side = 'A' if av > bv else 'B'
                result.update(competitive=True, tiebreak_criterion=cid)
                reason = f'Equal preference votes; {cid} criterion votes {av}:{bv} break the tie.'
                break
        if side is None:
            side, reason = administrative, 'Draw after fixed criterion priorities; seed advancement only.'
    result.update(winner_side=side, advancer=key[side], reason=reason,
                  low_confidence=not result['competitive'] or max(counts['A'], counts['B']) < 2)
    return result


def prepare(match, entrants):
    from fontTools.ttLib import TTFont
    from design_greek_campaign import inventory
    from arena_proofs import build_proofs

    run = ARENA / 'matches' / match
    if run.exists():
        raise ValueError('Refusing to overwrite an existing match')
    assert len(set(entrants)) == 2 and set(entrants) <= set(SEEDS)
    ordered = list(entrants)
    random.Random('20261029-' + match).shuffle(ordered)
    key = dict(zip('AB', ordered))
    fonts = {}
    for side, slug in key.items():
        base = ARENA / 'entrants' / slug / 'private'
        assert read(base / 'engineering.json')['pass'], slug
        fonts[side] = base / 'final.otf'
        assert fonts[side].exists(), fonts[side]
    (run / 'private').mkdir(parents=True)
    (run / 'packet').mkdir()
    _, report = build_proofs(run, fonts['B'], fonts['A'], inventory(TTFont(fonts['B'])))
    assert report['pass']
    provenance = {'key': key, 'fonts': {side: {'path': str(path), 'sha256': sha(path)}
                                      for side, path in fonts.items()},
                  'proof_helper_sha256': sha(ROOT / 'tools/arena_proofs.py'),
                  'contract_sha256': sha(ARENA / 'contract.json')}
    (run / 'private/provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (run / 'private/engineering.json').write_text(json.dumps(report, indent=2) + '\n')
    freeze(run)
    return {'run': str(run), 'image_count': len(read(run / 'packet/manifest.json')['images']),
            'proof_pass': report['pass']}


def aggregate(run):
    packet = run / 'packet'
    for name, checksum in read(packet / 'council-lock.json')['documents'].items():
        assert sha(packet / name) == checksum, name
    manifest = read(packet / 'manifest.json')
    for image in manifest['images']:
        assert sha(packet / image['path']) == image['sha256'], image['id']
    ids = [i['id'] for i in manifest['images']]
    sources = {s['id'] for s in read(packet / 'sources.json')['sources']}
    prov = read(run / 'private/provenance.json')
    for font in prov['fonts'].values():
        assert sha(Path(font['path'])) == font['sha256']
    ballots, errors = {}, {}
    for member in MEMBERS:
        try:
            ballots[member] = validate(read(run / 'ballots' / f'{member}.json'), member, ids, sources)
        except (OSError, ValueError, jsonschema.ValidationError) as error:
            errors[member] = str(error)[:800]
    for member, ballot in ballots.items():
        if ballot['preference'] == 'not_assessable':
            errors[member] = 'Overall comparison not assessable; no competitive advancement.'
    complete = len(ballots) == 3 and not errors
    preferences = {m: b['preference'] for m, b in ballots.items()}
    result = choose(preferences, {m: b['criteria'] for m, b in ballots.items()}, complete, prov['key'])
    result.update(match=run.name, key=prov['key'], round_complete=complete,
                  preferences=preferences, errors=errors,
                  criterion_differences=[{'member': m, 'criterion': c['id'], 'A': c['score_a'], 'B': c['score_b']}
                                          for m, b in ballots.items() for c in b['criteria']
                                          if c['score_a'] != c['score_b']],
                  verdicts={m: {'A': b['verdict_a'], 'B': b['verdict_b']} for m, b in ballots.items()},
                  feature_ready_claim=False,
                  limitation='Relative arena advancement is not perfection or publication acceptance.')
    (run / 'council-result.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = [f'# {run.name}', '', f"A = {prov['key']['A']}; B = {prov['key']['B']}.", '',
             f"Preferences: {preferences}. Advancer: **{result['advancer']}**.", '',
             result['reason'], '', f"Competitive result: {result['competitive']}; low confidence: {result['low_confidence']}.", '',
             'Relative preference does not establish absolute feature readiness. All raw ballots are preserved.', '']
    for member, b in ballots.items():
        lines += [f'## {member}', '', f"A: {b['verdict_a']}; B: {b['verdict_b']}; preference {b['preference']}.", '',
                  b['observed_change'], '', b['better_vs_featureworthy'], '',
                  '| Criterion | A | B | Justification and remaining gap |', '|---|---|---|---|']
        for c in b['criteria']:
            lines.append(f"| {c['id']} | {c['score_a']} | {c['score_b']} | {c['anchor_reason']} {c['remaining_gap']} |")
        lines += ['']
        for blocker in b['publication_blockers']:
            lines += [f"**{blocker['problem']}** {blocker['evidence']}", '',
                      f"Change: {blocker['change']} Why: {blocker['why']}", '',
                      f"Verify: {blocker['verify']} Preserve: {blocker['preserve']}", '']
        lines += ['Next experiment: ' + b['next_experiment'], '']
    for member, error in errors.items():
        lines += [f'## {member}: invalid or missing', '', error, '']
    (run / 'council-report.md').write_text('\n'.join(lines))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'aggregate'])
    parser.add_argument('match', choices=['semifinal-1', 'semifinal-2', 'final'])
    parser.add_argument('--entrants', nargs=2, choices=list(SEEDS))
    args = parser.parse_args()
    result = prepare(args.match, args.entrants) if args.action == 'prepare' else aggregate(ARENA / 'matches' / args.match)
    print(json.dumps(result, indent=2))
