#!/usr/bin/env python3
"""Render a substantial local four-face Storm Baskerville text reference.

Uses supplied installed fonts without copying their binaries or outlines into
the project. The PNG is a design reference, not the proposed new math font.
"""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont


FACES = [('Regular', 'Baskerville10Pro.otf'),
         ('Italic', 'Baskerville10Pro-Italic.otf'),
         ('Bold', 'Baskerville10Pro-Bold.otf'),
         ('Bold italic', 'Baskerville10Pro-BoldItalic.otf')]
PARAGRAPH = (
    'A mathematical page should read with the calm rhythm of a well-set book. '
    'Letters, figures and punctuation share the same light, while their varied '
    'shapes give each line its movement. A narrow counter must stay open; a '
    'fine stroke must survive at reading size. The italic turns within the '
    'roman texture without breaking it. In a companion mathematics family, '
    'Greek letters and symbols should feel at home beside these words, with '
    'clear distinctions and a consistent balance of black and white.'
)
SAMPLES = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ',
           'abcdefghijklmnopqrstuvwxyz',
           '0123456789  (1,234.56)  + - = / : ; ! ? &',
           'α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω']


def wrapped(draw, text, font, width):
    lines, current = [], ''
    for word in text.split():
        candidate = (current + ' ' + word).strip()
        if current and draw.textlength(candidate, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing to replace an existing reference directory')
    records = []
    for label, filename in FACES:
        path = args.font_dir / filename
        ft = TTFont(path)
        cmap = ft.getBestCmap()
        missing = sorted({c for c in PARAGRAPH+''.join(SAMPLES) if not c.isspace() and ord(c) not in cmap})
        if missing:
            raise ValueError(f'{filename}: missing reference characters {missing}')
        records.append({'style':label, 'filename':filename,
                        'source':str(path.resolve()),
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'weight_class':ft['OS/2'].usWeightClass,
                        'units_per_em':ft['head'].unitsPerEm,
                        'sx_height':getattr(ft['OS/2'], 'sxHeight', None),
                        'cap_height':getattr(ft['OS/2'], 'sCapHeight', None)})
        ft.close()
    image = Image.new('RGB', (2560, 4800), 'white')
    draw = ImageDraw.Draw(image)
    guides = Image.new('RGBA', image.size, (0,0,0,0))
    guide_draw = ImageDraw.Draw(guides)
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 35)
    small_label = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 27)
    draw.text((100, 55), 'STORM BASKERVILLE 10 PRO — LOCAL TEXT REFERENCE', font=label_font, fill='black')
    draw.text((100, 115), 'Original text in four actual faces; no synthetic styles. Reference typography, not the new math font.', font=small_label, fill='black')
    for index, record in enumerate(records):
        top = 210 + index*1120
        path = args.font_dir / record['filename']
        draw.line((100, top, 2460, top), fill='#aaaaaa', width=2)
        draw.text((100, top+22), record['style']+' · '+record['filename'], font=label_font, fill='black')
        body = ImageFont.truetype(str(path), 56)
        scan = ImageFont.truetype(str(path), 72)
        y = top+125
        lines = wrapped(draw, PARAGRAPH, body, 2360)
        for line in lines:
            draw.text((100, y), line, font=body, fill='black', anchor='ls')
            y += 73
        y += 40
        record['sample_baselines'] = []
        record['guidelines'] = []
        for sample_index, text in enumerate(SAMPLES):
            if draw.textlength(text, font=scan) > 2350:
                raise ValueError('Sample exceeds reference width')
            draw.text((100, y), text, font=scan, fill='black', anchor='ls')
            record['sample_baselines'].append(y)
            # Only the lowercase Latin and Greek lines get construction
            # guides, all in a separate removable layer. No inferred math axis.
            if sample_index in (1,3):
                for label, position, color in [
                    ('baseline', float(y), (35,100,180,115)),
                    ('x-height', y-record['sx_height']/record['units_per_em']*72, (35,140,100,115)),
                    ('cap height', y-record['cap_height']/record['units_per_em']*72, (170,90,40,115))]:
                    guide_draw.line((95,position,2460,position), fill=color, width=1)
                    mask_draw.line((95,position,2460,position), fill=255, width=3)
                    record['guidelines'].append({'sample_index':sample_index,'kind':label,'y':position})
            y += 92
        if y > top+1110:
            raise ValueError('Reference content exceeds style panel')
        record['image_crop_box'] = [80, top+5, 2480, top+1110]
        record['body_font_pixels'] = 56
        record['scan_font_pixels'] = 72
    draw.text((100, 4730), 'Read the whole page for colour; use unaltered face crops for detailed prompting. Font binaries remain external.', font=small_label, fill='black')
    args.output.mkdir(parents=True)
    path = args.output/'storm-baskerville-reference.png'
    image.save(path, dpi=(300,300))
    guides.save(args.output/'guidelines-overlay.png')
    mask.save(args.output/'guidelines-mask.png')
    Image.alpha_composite(image.convert('RGBA'),guides).convert('RGB').save(args.output/'storm-baskerville-guided.png', dpi=(300,300))
    for index, record in enumerate(records):
        crop = args.output/('storm-'+record['style'].lower().replace(' ', '-')+'.png')
        image.crop(record['image_crop_box']).save(crop, dpi=(300,300))
        guide_crop = crop.with_name(crop.stem+'-guides.png')
        guides.crop(record['image_crop_box']).save(guide_crop)
        record['crop'] = crop.name
        record['crop_sha256'] = hashlib.sha256(crop.read_bytes()).hexdigest()
        record['guides_crop'] = guide_crop.name
    manifest = {'purpose':'Substantial Storm Baskerville 10 Pro visual reference for unified master and production prompts',
                'image':path.name, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'dimensions':list(image.size), 'dpi':300, 'faces':records,
                'guidelines':{'overlay':'guidelines-overlay.png','mask':'guidelines-mask.png',
                              'guided_view':'storm-baskerville-guided.png',
                              'coordinates':'Baseline, x-height and cap height from source font metrics at 72px em; overlay on lowercase Latin and Greek specimen lines.',
                              'math_axis':'Not a text font metric; set only after unified math-master calibration.',
                              'mask_semantics':'White excludes guide ink; clean original must be used for tracing, never erase this mask from a flattened annotated glyph.'},
                'paragraph':PARAGRAPH, 'sample_lines':SAMPLES,
                'note':'Same point scale, not normalized x-height; use separate matched-apparent-size proofs for weight calibration. No font binary is included. These reference shapes do not override the approved unified math master.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(path.resolve())


if __name__ == '__main__':
    main()
