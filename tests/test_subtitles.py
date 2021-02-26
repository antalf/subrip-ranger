from io import StringIO
from unittest import TestCase, mock

from subrip_ranger import subtitles, timecodes


class TestBase:
    SUBSECTIONS = [
        '1\n'
        '00:00:01,000 --> 00:00:02,000\n'
        'subtext 1/1\n'
        'subtext 1/2\n',
        '2\n'
        '00:00:04,000 --> 00:00:05,000\n'
        'subtext 2/1\n'
        'subtext 2/2\n',
    ]
    START_INDEX = 1


class SubtitleTest(TestBase, TestCase):

    def setUp(self):
        self.subsection = self.SUBSECTIONS[0]
        self.subtitle = subtitles.Subtitle(self.START_INDEX)
        self.subtitle.parse(self.subsection)

    def test_parsing(self):
        """parsing results expected values"""
        self.assertEqual(self.subtitle.index, self.START_INDEX)
        self.assertEqual(
            self.subtitle.timecode_line.appearance.value.total_seconds(), 1
        )
        self.assertEqual(
            self.subtitle.timecode_line.disappearance.value.total_seconds(), 2
        )
        self.assertEqual(len(self.subtitle.sublines), 2)

    @mock.patch.object(timecodes.TimecodeLine, 'adjust')
    def test_adjustment(self, mock_adjust):
        """adjustment called on timecode_line instance"""
        self.subtitle.adjust()
        mock_adjust.assert_called_once()

    def test_formatting(self):
        """formatting unadjusted subtitle matches with original"""
        self.assertEqual(str(self.subtitle), self.subsection)


class SubtitleSequenceTest(TestBase, TestCase):

    def setUp(self):
        self.subsections = '\n'.join(self.SUBSECTIONS)
        self.input = StringIO(self.subsections)
        self.subtitle_sequence = subtitles.SubtitleSequence(self.START_INDEX)
        self.subtitle_sequence.parse(self.input)

    def test_parsing(self):
        """subtitle entries fetched properly"""
        result = len(self.subtitle_sequence.subtitles)
        self.assertEqual(result, len(self.SUBSECTIONS))

    @mock.patch.object(subtitles.Subtitle, 'adjust')
    def test_adjustment(self, mock_adjust):
        """adjustment forwarded to each Subtitle instances"""
        self.subtitle_sequence.adjust()
        self.assertEqual(mock_adjust.call_count, len(self.SUBSECTIONS))

    def test_writing(self):
        """output of unadjusted subtitles matches with original content"""
        mock_file = mock.Mock()
        self.subtitle_sequence.write(mock_file)
        mock_file.write.assert_called_once_with(self.subsections)
