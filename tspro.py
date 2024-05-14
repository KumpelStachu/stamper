#!/usr/bin/env python3
from datetime import datetime
import argparse
import ffmpeg
import sys
import re

parser = argparse.ArgumentParser(prog='tspro', description='Add timestamp overlay to video')
parser.add_argument('input_files', help='Input video files', nargs='+')
parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
parser.add_argument('--suffix', help='Output file suffix', default='_ts')
parser.add_argument('--font', help='Font family', default='Arial')
parser.add_argument('--color', help='Text color', default='white')
parser.add_argument('--border', help='Border color', default='black')
parser.add_argument('--size', help='Text size', default=24, type=float)
parser.add_argument('--opacity', help='Overlay opacity', default=100, type=float)
parser.add_argument('--margin', help='Overlay margin', default=10, type=float)
parser.add_argument('--position-x', help='Horizontal position', default='left', choices=['left', 'center', 'right'])
parser.add_argument('--position-y', help='Vertical position', default='bottom', choices=['top', 'center', 'bottom'])

args = parser.parse_args()
input_files: list[str] = args.input_files

for filename in input_files:
    print(f'Processing {filename}')

    try:
        info = ffmpeg.probe(filename)
        stream = next(filter(lambda s: s['codec_type'] == 'video', info['streams']))
    except ffmpeg.Error:
        print(f'Error: invalid input file {filename}')
        continue

    try:
        creation_time = datetime.strptime(stream['tags']['creation_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
    except KeyError:
        print(f'Warning: no creation time for {filename}')
        creation_time = datetime.now()

    width = stream['width']
    height = stream['height']
    size = args.size * min(width, height) / 300

    x = args.margin * size / args.size
    if args.position_x == 'center':
        x = f'(W-text_w)/2'
    elif args.position_x == 'right':
        x = f'W-text_w-{x}'

    y = args.margin * size / args.size
    if args.position_y == 'center':
        y = f'(H-text_h)/2'
    elif args.position_y == 'bottom':
        y = f'H-text_h-{y}'

    input = ffmpeg.input(filename)
    output = re.sub(r'\.(\w+)$', fr'{args.suffix}.\1', filename)

    stream = ffmpeg.drawtext(input, escape_text=False, x=x, y=y, # type: ignore
                             fontfile='C:/Windows/Fonts/arial.ttf' if sys.platform == 'win32' else None,
                             font=args.font, fontcolor=args.color, fontsize=size,
                             bordercolor=args.border, borderw=size//12, alpha=args.opacity/100,
                             text=f'%{{pts:localtime:{int(creation_time.timestamp())}}}')
    stream.output(output).run(overwrite_output=True, quiet=not args.verbose)
