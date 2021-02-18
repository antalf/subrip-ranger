# Brief description

Command line tool to adjust slip and speed imperfections in SubRip format
subtitle files.

It cannot adjust single subtitle entry timeings, there are GUI tools for that.

# Usage

First check the incorrect subtitle file content and remember first and last
subtitles.

Then check and seek the video and notice two time offsets:
1. the time when first subtitle should appear and
2. the time when last subtitle should disappear.

To make the conversion run the tool by specifying original file, target file,
desired appearance of the first subtitle, desired disappearance of the last
subtitle and file encoding if it differs from ISO8859-1.

For example to move each subtitle forward with one second in the included
example SubRip file:

```
  subrip_ranger \
    -i orig/happy-birthday-to-gnu-english.srt \
    -o /tmp/test.srt \
    -f '00:00:01,000' \
    -l '00:05:51,999'
```
