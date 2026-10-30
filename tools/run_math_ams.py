#!/usr/bin/env python3
"""Build explicit AMS additions, audit both engines and retain a proof viewer.

No image/model call, donor-font import or implicit coverage substitution occurs.
"""
import argparse
import json
import os
from pathlib import Path

from build_math_ams import FONT_NAME, build as build_font
from proof_ams_runtime import build as build_proofs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base-sources', type=Path, required=True)
    parser.add_argument('--sources', type=Path, action='append', required=True,
                        help='Complete source manifests; may repeat, but roles must be unique')
    parser.add_argument('--text-font-dir', type=Path, required=True)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--calibration', type=Path, help='Explicit reviewed optical grid profile')
    parser.add_argument('--allow-uncalibrated', action='store_true',
                        help='Explicit historical reproduction only; new work needs a reviewed grid')
    args = parser.parse_args()
    if not args.calibration and not args.allow_uncalibrated:
        parser.error('Greek grid calibration is required. Use --allow-uncalibrated only for an explicit historical reproduction.')
    if args.output.exists():
        parser.error('Use a fresh output directory; earlier deliveries are immutable')
    records = {}
    for manifest in args.sources:
        data = json.loads(manifest.read_text())['sources']
        for name, original in data.items():
            if name in records:
                parser.error(f'Duplicate role across manifests: {name}')
            entry = dict(original)
            for field in ['curves', 'root_image']:
                if field in entry:
                    path = (manifest.resolve().parent / entry[field]).resolve()
                    entry[field] = os.path.relpath(path, args.output.resolve())
            records[name] = entry
    args.output.mkdir(parents=True)
    merged = args.output / 'font-sources.json'
    merged.write_text(json.dumps({'sources': records}, indent=2) + '\n')
    font = build_font(args.output / 'font', merged, args.base_sources, args.calibration)
    summary = {'status': 'building', 'font': 'font/' + FONT_NAME,
               'font_sha256': font['font_sha256'],
               'glyph_count': len(font['glyph_order']),
               'source_inputs': [str(p) for p in args.sources],
               'base_sources': str(args.base_sources),
               'runtime_summary': 'runtime/runtime-summary.json',
               'coverage_claim': 'Only explicitly audited rendered commands; full AMS unfinished.'}
    try:
        proof = build_proofs(args.output / 'font' / FONT_NAME, args.text_font_dir,
                             args.output / 'runtime', args.dpi)
    except Exception as error:
        summary.update(status='failed', error=str(error))
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        raise
    summary['status'] = proof['status']
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    from view_math_ams import build_view
    build_view(args.output)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
