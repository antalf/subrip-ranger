"""
Recalculate SubRip subtitle file to scale to the specified first and last
timing or scaling.
"""

import argparse
import logging

from . import timecodes, subtitles

DEFAULT_ENCODING = 'ISO8859-1'
DEFAULT_START_INDEX = 1
DEFAULT_SCALE = 1.0
DEFAULT_LOG_LEVEL = logging.WARNING

logger = logging.getLogger(__name__)


def main():
    argparser = get_argparser()
    args = argparser.parse_args()

    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)

    subtitle_sequence = subtitles.SubtitleSequence(args.start_index)
    with open(args.input_file, encoding=args.encoding, mode='r') as input:
        subtitle_sequence.parse(input)

    timecodes.Adjuster().set_params(
        args.first_appearance,
        last_disappearance=args.last_disappearance, scale=args.scale
    )
    subtitle_sequence.adjust()

    with open(args.output_file, encoding=args.encoding, mode='w') as output:
        subtitle_sequence.write(output)


def get_argparser():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        'first_appearance',
        help='Appearance timecode of first subtitle in HH:MM:SS,SSS format',
    )
    argparser.add_argument(
        'input_file',
        help='Source SubRip file',
    )
    argparser.add_argument(
        'output_file',
        help='Target SubRip file',
    )
    argparser.add_argument(
        '-l', '--last-disappearance',
        help='Disappearance timecode of last subtitle in HH:MM:SS,SSS format',
        metavar='TIMECODE',
    )
    argparser.add_argument(
        '-s', '--scale',
        type=float,
        default=DEFAULT_SCALE,
        help='Scale ratio (--last-disappearance overrides it) [%(default)s]',
        metavar='FLOAT',
    )
    argparser.add_argument(
        '-e', '--encoding',
        default=DEFAULT_ENCODING,
        help='Character encodings of input and output file [%(default)s]',
        metavar='ENCODING',
    )
    argparser.add_argument(
        '-i', '--start-index',
        type=int,
        default=DEFAULT_START_INDEX,
        help='Start index of the first subtitle [%(default)d]',
        metavar='INDEX',
    )
    argparser.add_argument(
        '-d', '--log-level',
        choices = logging._levelToName.values(),
        default=logging.getLevelName(DEFAULT_LOG_LEVEL),
        help='Verbosity level [%(default)s]',
        metavar='LOG_LEVEL',
    )
    return argparser
