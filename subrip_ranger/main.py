"""
Recalculate SubRip subtitle file to scale to the specified first and last
timing.
"""

import argparse
import logging

from . import timecodes

DEFAULT_ENCODING = 'ISO8859-1'
DEFAULT_START_INDEX = 1
DEFAULT_LOG_LEVEL = logging.WARN

logger = logging.getLogger(__name__)


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--input-file',
        required=True,
        help='Source SubRip file',
        metavar='FILE',
    )
    argparser.add_argument(
        '-o', '--output-file',
        required=True,
        help='Target SubRip file',
        metavar='FILE',
    )
    argparser.add_argument(
        '-f', '--first-appearance',
        required=True,
        help='Appearing timecode of first subtitle in HH:MM:SS,SSS format',
        metavar='TIMECODE',
    )
    argparser.add_argument(
        '-l', '--last-disappearance',
        required=True,
        help='Disappearing timecode of last subtitle in HH:MM:SS,SSS format',
        metavar='TIMECODE',
    )
    argparser.add_argument(
        '-e', '--encoding',
        default=DEFAULT_ENCODING,
        help='Character encodings of input and output file [%(default)s]',
        metavar='ENCODING',
    )
    argparser.add_argument(
        '-s', '--start-index',
        default=DEFAULT_START_INDEX,
        type=int,
        help='Start index of the first subtitle [%(default)d]',
        metavar='INDEX',
    )
    argparser.add_argument(
        '-d', '--log-level',
        default=logging.getLevelName(DEFAULT_LOG_LEVEL),
        help='Verbosity level [%(default)s]',
        metavar='LOG_LEVEL',
    )
    args = argparser.parse_args()

    log_level = int(getattr(logging, args.log_level))
    logging.basicConfig(level=log_level)

    subtitles = []
    with open(file=args.input_file, encoding=args.encoding, mode='r') as input:
        state = 'index'
        subtitle = {}
        content = ''
        for line in input:
            content = line.rstrip()
            if content == '':
                state = 'index'
                subtitles.append(subtitle)
            elif state == 'index':
                subtitle = {'index': int(content), 'lines': []}
                state = 'timecodes'
            elif state == 'timecodes':
                subtitle['timecode_line'] = \
                    timecodes.TimecodeLine.from_timecode_line_string(content)
                state = 'subtitle'
            elif state == 'subtitle':
                subtitle['lines'].append(content)
        if content != '':
            subtitles.append(subtitle)

    dest = timecodes.Period(
        timecodes.Timecode.from_timecode_string(args.first_appearance).value,
        timecodes.Timecode.from_timecode_string(args.last_disappearance).value
    )
    adjuster = timecodes.Adjuster()
    adjuster.set_dest(dest)

    with open(file=args.output_file, encoding=args.encoding, mode='w') as output:
        index = args.start_index
        for subtitle in subtitles:
            if index != args.start_index:
                output.write('\n')
            output.write(f'{index}\n')
            subtitle['timecode_line'].adjust()
            output.write('%s\n' % str(subtitle['timecode_line']))
            output.write('%s\n' % '\n'.join(subtitle['lines']))
            index += 1
