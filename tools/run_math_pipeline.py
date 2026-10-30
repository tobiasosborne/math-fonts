#!/usr/bin/env python3
"""Rebuild the bounded companion and prove external Storm reuse on both TeX engines."""
import argparse
import json
from pathlib import Path

from build_math_pilot import FONT_NAME, build as build_font
from proof_math_pilot import build as build_proofs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Fresh output directory')
    parser.add_argument('--sources', type=Path, help='Explicit measured glyph-source registration manifest')
    parser.add_argument('--text-font-dir', type=Path, required=True, help='External original Storm four-face directory')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--glyph-run', type=Path, help='Measured glyph-run directory; add an interactive proof viewer')
    args = parser.parse_args()
    if args.glyph_run and args.dpi != 300:
        parser.error('Interactive viewer currently expects 300dpi proof assets')
    if args.output.exists():
        parser.error('output must be fresh; previous runs remain immutable')
    # No image generation: default frozen root traces or explicitly registered sources.
    font = build_font(args.output / 'font', args.sources)
    proof = build_proofs(args.output / 'font' / FONT_NAME, args.text_font_dir,
                         args.output / 'runtime', args.dpi)
    summary = {'status': proof['status'], 'font': 'font/' + FONT_NAME,
               'font_sha256': font['font_sha256'], 'runtime_summary': 'runtime/summary.json',
               'glyph_count': len(font['glyph_order']),
               'engine_role_checks': {engine: len(record['role_checks'])
                                      for engine, record in proof['engines'].items()}}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    if args.glyph_run:
        from view_math_pipeline import build_view
        build_view(args.output,args.glyph_run)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
