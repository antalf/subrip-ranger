from . import timecodes


class Subtitle:
    """implement SubRip subtitle section"""

    def __init__(self, index):
        self.index = index
        self.timecode_line = None
        self.sublines = []

    def parse(self, section: str):
        """parse SubRip formatted section and store its components"""
        lines = section.splitlines()
        lines.pop(0)
        self.timecode_line = \
            timecodes.TimecodeLine.from_timecode_line_string(lines.pop(0))
        self.sublines = lines[:]

    def adjust(self):
        """delegate adjustment to timecode_line instance"""
        self.timecode_line.adjust()

    def __str__(self):
        """format SubRip compliant subtitle section"""
        return '%d\n%s\n%s\n' % (
            self.index, str(self.timecode_line), '\n'.join(self.sublines)
        )


class SubtitleSequence:
    """implement sequence of subtitles representing SubRip file content"""

    def __init__(self, start_index):
        self.index = start_index
        self.subtitles = []

    def parse(self, input):
        """create list of subtitles by reading from a file handler"""
        subsections = input.read().strip('\n').split('\n\n')
        self.subtitles = \
            [self.get_subtitle(subsection) for subsection in subsections]

    def get_subtitle(self, subsection: str):
        """return a Subtitle class from a subtitle section string"""
        subtitle = Subtitle(self.index)
        subtitle.parse(subsection)
        self.index += 1
        return subtitle

    def adjust(self):
        """delegate adjustment to all subtitle instances"""
        [subtitle.adjust() for subtitle in self.subtitles]

    def write(self, output):
        """write SubRib formatted content to a file handler"""
        subsections = (str(subtitle) for subtitle in self.subtitles)
        output.write('\n'.join(subsections))
