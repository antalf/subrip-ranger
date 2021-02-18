"""Classes to manage Subrip timecodes."""
import datetime
import logging
import re
from typing import NamedTuple

logger = logging.getLogger(__name__)

class Period:
    """
    Compose start and end to a single object
    and provide difference between them.
    """

    def __init__(self, start: datetime.timedelta, end: datetime.timedelta):
        self.start = start
        self.end = end

    @property
    def range(self):
        return self.end - self.start


class Adjuster:
    """Handle details for adjustment and calculate adjustment."""
    _borg_state = {}

    def __init__(self):
        """Implements Borg pattern and initalize on first instantiation only."""
        self.__dict__ = self._borg_state
        if not self._borg_state:
            self.orig = Period(None, None)
            self.dest = None
            self.offset = None
            self.scale = None

    def update(self, value: datetime.timedelta):
        """Stretch a range around into orig by finding min and max value."""
        try:
            self.orig.start, self.orig.end = \
                min(self.orig.start, value), max(self.orig.end, value)
        except TypeError:
            self.orig.start = self.orig.end = value

    def set_dest(self, dest: Period):
        """
        Calculate scale and offset for adjustment from original timecode
        range and the desired range.

        Call this after calling update on all original timecodes. 
        """
        self.dest = dest
        self.scale = self.dest.range / self.orig.range
        self.offset = self.orig.start - self.dest.start
        logger.info(
            'original timecodes from %s to %s', self.orig.start, self.orig.end
        )
        logger.info('scaling with %f', self.scale)
        logger.info('desired first timecode difference %s', self.offset)

    def adjust(self, value: datetime.timedelta):
        """Return desired value for a timecode."""
        return (value - self.orig.start) * self.scale + self.dest.start


class Timecode:
    """Convert a timecode as a timedelta back and forth."""
    TIMECODE_PATTERN = re.compile(
        r'(?P<hours>\d{2})'
        r':(?P<minutes>\d{2})'
        r':(?P<seconds>\d{2})'
        r',(?P<milliseconds>\d{3})'
    )
    TIMEDELTA_PATTERN = re.compile(
        r'(?P<hours>\d{,2})'
        r':(?P<minutes>\d{2})'
        r':(?P<seconds>\d{2})'
        r'(\.(?P<microseconds>\d{6}))*'
    )
    UNITS = ['hours', 'minutes', 'seconds', 'milliseconds']

    def __init__(self, value: datetime.timedelta):
        self.value = value

    @classmethod
    def from_timecode_string(cls, timecode_string):
        """Alternative constructor for timecode format handling."""
        match = cls.TIMECODE_PATTERN.match(timecode_string)
        if not match:
            raise ValueError(f'invalid timecode format "{timecode_string}"')
        kwargs = dict((unit, int(match.group(unit))) for unit in cls.UNITS)
        return cls(datetime.timedelta(**kwargs))

    def __str__(self):
        """Return internal timedelta value in timecode format."""
        timedelta_string = str(self.value)
        match = self.TIMEDELTA_PATTERN.match(timedelta_string)
        if not match:
            raise ValueError(f'invalid timedelta format "{timedelta_string}"')
        fields = match.groupdict()
        if fields['microseconds'] is None:
            fields['microseconds'] = '000'
        fields.update({
            'hours': int(fields['hours']),
            'minutes': int(fields['minutes']),
            'seconds': int(fields['seconds']),
            'milliseconds': int(fields['microseconds']) // 1000,
        })
        return '{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}' \
            .format(**fields)


class AdjustibleTimecode(Timecode):
    """Extend Timecode with adjustment handling."""

    def __init__(self, value: datetime.timedelta):
        """Call adjuster update for stretching original timecode range."""
        super().__init__(value)
        self.adjuster = Adjuster()
        self.adjuster.update(value)

    def adjust(self):
        """Do adjustment on stored timedelta value."""
        adjusted = self.adjuster.adjust(self.value)
        logger.debug('adjust %s to %s', self.value, adjusted)
        self.value = adjusted

class TimecodeLine(NamedTuple):
    """
    Manage whole timecode line with appearace and disappearance for a
    subtitle entry.
    """
    appearance: Timecode
    disappearance: Timecode
    TIMECODE_LINE_PATTERN = re.compile(
        r'(?P<appearance>\d{2}:\d{2}:\d{2},\d{3})'
        r'\s+-->\s+'
        r'(?P<disappearance>\d{2}:\d{2}:\d{2},\d{3})'
    )

    @classmethod
    def from_timecode_line_string(cls, timecode_line_string):
        """
        Alternate constructor to convert timecode line format to pair of
        Timecodes.
        """
        match = cls.TIMECODE_LINE_PATTERN.match(timecode_line_string)
        if not match:
            raise ValueError(
                f'invalid timecode line format "%s"', timecode_line_string
            )
        kwargs = dict(
            (field, AdjustibleTimecode.from_timecode_string(match.group(field)))
            for field in (cls._fields)
        )
        return cls(**kwargs)

    def __str__(self):
        """Convert timecode pair back to timecode line format."""
        return f'{self.appearance} --> {self.disappearance}'

    def adjust(self):
        """Make both timecodes adjusted."""
        [getattr(getattr(self, field), 'adjust')() for field in self._fields]
