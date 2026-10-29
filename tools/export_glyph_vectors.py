#!/usr/bin/env python3
"""Reproduce filled/real-handle SVGs from a completed glyph-consistency run.

Never invokes image generation, changes an input, or replaces an output folder.
The current extraction is deliberately restricted to connected glyphs: the
experimental tracer selects the largest component. Disconnected symbols need
an explicit production extraction policy before this tool can accept them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image
from trace_glyph_trial import LIB, geometry, save_svg, svg_path, trace


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(run, destination):
    run = run.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise ValueError(f'Refusing to replace existing output: {destination}')
    contract = json.loads((run / 'contract.json').read_text())
    master_hash = digest(run / 'master.png')
    if master_hash != contract['master_sha256']:
        raise ValueError('Master SHA256 differs from the frozen run contract')
    requests = json.loads((run / 'requests.json').read_text())
    # Validate every input before creating output. Paths are resolved relative
    # to the run, so recorded absolute paths do not bind a checkout location.
    names = [r['name'] for r in requests]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate glyph names')
    for request in requests:
        name = request['name']
        if Path(name).name != name or name in ('.', '..'):
            raise ValueError('Unsafe glyph name')
        folder = run / 'glyphs' / name
        result = json.loads((folder / 'result.json').read_text())
        if result['status'] != 'complete' or digest(folder / 'enlarged.png') != result['sha256']:
            raise ValueError(f'Incomplete or changed original: {name}')
        crop = Image.open(run / 'master.png').crop(request['master_crop_box'])
        recorded = Image.open(folder / 'master-crop.png')
        if crop.mode != recorded.mode or crop.size != recorded.size or crop.tobytes() != recorded.tobytes():
            raise ValueError(f'Master crop is not an unaltered source crop: {name}')
        if (folder / 'prompt.txt').read_text() != request['prompt']:
            # Original prompt files may have one terminal newline.
            if (folder / 'prompt.txt').read_text().rstrip('\n') != request['prompt'].rstrip('\n'):
                raise ValueError(f'Prompt record mismatch: {name}')
    destination.mkdir(parents=True)
    rows = []
    # Original trial cells are 144x216; labels get separate space. Placement
    # follows recorded registration, not a new claim about common font metrics.
    cols = max(r['column'] for r in requests)
    nrows = max(r['row'] for r in requests)
    cell_w, cell_h, label_h = 144, 216, 36
    specimen = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols*cell_w}" height="{nrows*(cell_h+label_h)}" viewBox="0 0 {cols*cell_w} {nrows*(cell_h+label_h)}">',
                '<rect width="100%" height="100%" fill="white"/>']
    from glyph_consistency_report import component
    for request in requests:
        name = request['name']
        folder = run / 'glyphs' / name
        source = folder / 'enlarged.png'
        image = Image.open(source)
        _, _, _, extra = component(image)
        if extra:
            raise ValueError(f'{name}: disconnected ink requires manual extraction review ({extra} pixels)')
        paths, size, box = trace(image)
        svg = destination / (name + '.svg')
        handles = destination / (name + '-handles.svg')
        save_svg(paths, size, svg)
        save_svg(paths, size, handles, handles=True)
        metrics = json.loads((folder / 'metrics.json').read_text())
        reg = metrics['registration']
        s = reg['uniform_scale']
        tx = (request['column']-1)*cell_w + reg['translate_x'] - s*max(0, box[0]-8)
        ty = (request['row']-1)*(cell_h+label_h) + reg['translate_y'] - s*max(0, box[1]-8)
        specimen.append(f'<path d="{svg_path(paths)}" transform="translate({tx},{ty}) scale({s})" fill="black" fill-rule="nonzero"/>')
        text = ET.Element('text', {'x':str((request['column']-1)*cell_w+3),
                                  'y':str((request['row']-1)*(cell_h+label_h)+cell_h+20),
                                  'font-size':'10', 'fill':'black'})
        text.text = name
        specimen.append(ET.tostring(text, encoding='unicode'))
        rows.append({'name':name, 'char':request['char'], 'source_sha256':digest(source),
                     'prompt_sha256':digest(folder / 'prompt.txt'),
                     'svg':svg.name, 'svg_sha256':digest(svg),
                     'handles_svg':handles.name, 'handles_sha256':digest(handles),
                     **geometry(paths, box[3]-box[1])})
    specimen.append('</svg>')
    (destination / 'registered-specimen.svg').write_text('\n'.join(specimen)+'\n')
    manifest = {'schema_version':1, 'master_sha256':master_hash,
                'tool':LIB.potrace_version().decode(),
                'settings':{'threshold':128, 'alphamax':1, 'opticurve':1,
                            'opttolerance_glyph_height_fraction':.0015, 'turdsize':0},
                'extraction_policy':'Connected glyph only; fail on discarded disconnected dark ink.',
                'registration_note':'Per-glyph translation/uniform scale to original master. Not font metrics.',
                'glyphs':rows}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
    archive = destination / 'outlines.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(destination.iterdir()):
            if p != archive:
                z.write(p, p.name)
    print(json.dumps({'glyphs':len(rows), 'output':str(destination), 'zip':str(archive)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    export(args.run, args.output)


if __name__ == '__main__':
    main()
