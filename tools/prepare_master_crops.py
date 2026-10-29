#!/usr/bin/env python3
"""Reproduce unaltered glyph crops from a hash-pinned unified master/layout.

Crop dimensions are anatomy regions, not font em boxes. Registration must
recover the root coordinates; this tool never stretches or normalizes glyphs.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',required=True,type=Path)
    parser.add_argument('--layout',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing to replace an existing output directory')
    layout=json.loads(args.layout.read_text())
    if sha(args.image.read_bytes())!=layout['root_sha256']:
        raise ValueError('Root hash does not match approved layout')
    image=Image.open(args.image)
    names=set()
    crops=[]
    for record in layout['cells']:
        name=record['name']
        if name in names or Path(name).name!=name or name in ('.','..'):
            raise ValueError('Unsafe or repeated cell name')
        names.add(name)
        x0,y0,x1,y1=record['source_crop_box']
        if not (0<=x0<x1<=image.width and 0<=y0<y1<=image.height):
            raise ValueError('Crop lies outside root image')
        crops.append((record,image.crop((x0,y0,x1,y1))))
    args.output.mkdir(parents=True)
    rows=[]
    for record,crop in crops:
        path=args.output/(record['name']+'.png')
        crop.save(path)
        digest=sha(path.read_bytes())
        if record.get('crop_sha256') and digest!=record['crop_sha256']:
            raise ValueError('Reproduced crop differs: '+record['name'])
        rows.append({**record,'crop':path.name,'crop_sha256':digest})
    (args.output/'manifest.json').write_text(json.dumps({
        'root_sha256':layout['root_sha256'],'root_image':str(args.image),
        'layout_sha256':sha(args.layout.read_bytes()),
        'policy':'Unaltered crops, all components retained, no normalization; font geometry registers back to root.',
        'cells':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'crops':len(rows),'output':str(args.output)},indent=2))


if __name__=='__main__':
    main()
