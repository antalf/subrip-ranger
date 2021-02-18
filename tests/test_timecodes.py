from unittest import TestCase
import datetime

from subrip_ranger import timecodes


class PeriodTest(TestCase):
    START = datetime.timedelta(hours=1, minutes=2, seconds=3)
    END = datetime.timedelta(hours=1, minutes=2, seconds=45)

    def setUp(self):
        self.period = timecodes.Period(self.START, self.END)

    def test_creation(self):
        """period has proper attributes"""
        self.assertEqual(self.period.start, self.START)
        self.assertEqual(self.period.end, self.END)

    def test_range(self):
        """calculate difference properly"""
        self.assertEqual(self.period.range, self.END - self.START)
    

class AdjusterTest(TestCase):
    DEST_FIRST_APPEARANCE = datetime.timedelta(minutes=1, seconds=3)
    DEST_LAST_DISAPPERANCE = datetime.timedelta(minutes=1, seconds=6)
    TIMECODE_FIRST = datetime.timedelta(minutes=1, seconds=2)
    TIMECODE_LAST = datetime.timedelta(minutes=1, seconds=5)

    def setUp(self):
        timecodes.Adjuster._borg_state = {}
        self.adjuster = timecodes.Adjuster()
        self.adjuster.update(self.TIMECODE_FIRST)
        self.adjuster.update(self.TIMECODE_LAST)
        self.dest = timecodes.Period(
            self.DEST_FIRST_APPEARANCE, self.DEST_LAST_DISAPPERANCE
        )

    def test_update(self):
        """updating range start and end properly"""
        self.assertEqual(self.adjuster.orig.start, self.TIMECODE_FIRST)
        self.assertEqual(self.adjuster.orig.end, self.TIMECODE_LAST)

    def test_dest_setting(self):
        """calculate scale and offset properly upon setting destination"""
        self.adjuster.set_dest(self.dest)
        self.assertEqual(self.adjuster.scale, 1.0)
        self.assertEqual(self.adjuster.offset,
                         self.TIMECODE_FIRST - self.DEST_FIRST_APPEARANCE)

    def test_adjusting(self):
        """calculate adjustment properly"""
        self.adjuster.set_dest(self.dest)
        adjusted = self.adjuster.adjust(self.TIMECODE_FIRST)
        self.assertEqual(self.DEST_FIRST_APPEARANCE, adjusted)


class TimecodeTest(TestCase):
    TIMECODE_STRING = '01:23:45,678'

    def setUp(self):
        self.timecode_value = datetime.timedelta(
            hours=1, minutes=23, seconds=45, milliseconds=678
        )

    def test_from_timecode_string(self):
        """alternative constructor from timecode_string"""
        timecode = timecodes.Timecode.from_timecode_string(self.TIMECODE_STRING)
        result = timecode.value
        expected = self.timecode_value
        self.assertEqual(result, expected, msg='different delta value')

    def test_to_timecode_string(self):
        """format timedelta as timecode string"""
        timecode = timecodes.Timecode(self.timecode_value)
        result = str(timecode)
        expected = self.TIMECODE_STRING
        self.assertEqual(result, expected, msg='unexpected timecode format')

    def test_to_timecode_string_no_fraction(self):
        """format timedelta as timecode string with no fraction seconds"""
        timecode = timecodes.Timecode(
            datetime.timedelta(hours=1, minutes=2, seconds=3)
        )
        result = str(timecode)
        expected = '01:02:03,000'
        self.assertEqual(result, expected, msg='unexpected timecode format')


class AdjustibleTimecodeTest(TestCase):
    TIMECODE_FIRST = '00:03:00,000'
    TIMECODE_LAST = '00:07:00,000'
    DEST_START = '00:02:00,000'
    DEST_END = '00:06:00,000'

    def setUp(self):
        timecodes.Adjuster._borg_state = {}
        self.timecode_value = datetime.timedelta(
            hours=1, minutes=23, seconds=45, milliseconds=678
        )

    def test_adjusting(self):
        """adjusting value with parameters"""
        timecode_first = timecodes.AdjustibleTimecode.from_timecode_string(
            self.TIMECODE_FIRST
        )
        timecode_last = timecodes.AdjustibleTimecode.from_timecode_string(
            self.TIMECODE_LAST
        )
        adjuster = timecodes.Adjuster()
        dest = timecodes.Period(
            timecodes.Timecode.from_timecode_string(self.DEST_START).value,
            timecodes.Timecode.from_timecode_string(self.DEST_END).value
        )
        adjuster.set_dest(dest)
        timecode_first.adjust()
        self.assertEqual(timecode_first.value, dest.start)


class TimecodeLineTest(TestCase):
    APPEARANCE = '00:42:55,990'
    DISAPPEARANCE = '00:43:00,910'
    TIMECODE_LINE_STRING = f'{APPEARANCE} --> {DISAPPEARANCE}'
    DEST_START = '00:42:56,990'
    DEST_END = '00:43:01,910'

    def setUp(self):
        timecodes.Adjuster._borg_state = {}
        self.timecode_line = timecodes.TimecodeLine.from_timecode_line_string(
            self.TIMECODE_LINE_STRING
        )

    def test_from_timecode_line_string(self):
        """attributes properly set"""
        result = str(self.timecode_line.appearance)
        expected = self.APPEARANCE
        self.assertEqual(result, expected)
        result = str(self.timecode_line.disappearance)
        expected = self.DISAPPEARANCE
        self.assertEqual(result, expected)

    def test_adjusting(self):
        """adjusting to a desired range"""
        dest = timecodes.Period(
            timecodes.Timecode.from_timecode_string(self.DEST_START).value,
            timecodes.Timecode.from_timecode_string(self.DEST_END).value
        )
        adjuster = timecodes.Adjuster()
        adjuster.set_dest(dest)
        self.timecode_line.adjust()
        result = str(self.timecode_line)
        expected = '00:42:56,990 --> 00:43:01,910'
        self.assertEqual(result, expected)

    def test_to_timecode_line_string(self):
        """format timecode_line as timecode line string"""
        result = str(self.timecode_line)
        expected = self.TIMECODE_LINE_STRING
        self.assertEqual(
            result, expected, msg='unexpected timecode line format'
        )
