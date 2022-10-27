#!/usr/bin/env python3

from argparse import ArgumentParser
import dateutil
import dateutil.parser
from datetime import datetime
from dateutil.zoneinfo import getzoneinfofile_stream, ZoneInfoFile
from collections import defaultdict

# opinionated list of timezones
# and (for this list) unambiguous abbreviations
TIMEZONES = {
    "UTC": "UTC",
    "HST": "Pacific/Honolulu",
    "PST": "America/Tijuana",
    "CST": "America/Chicago",
    "EST": "America/Thunder_Bay",
    "WET": "Europe/Lisbon",
    "CET": "Europe/Berlin",
    "EET": "Europe/Kyiv",
    "+0330": "Asia/Tehran",
    "IST": "Asia/Kolkata",
    "+07": "Asia/Novosibirsk",
    "HKT": "Asia/Hong_Kong",
    "JST": "Asia/Tokyo",
    "AEST": "Australia/Sydney",
}


def format_utcoffset(tz, reftime):
    utcoffset = tz.utcoffset(reftime)
    midnight = dateutil.parser.parse("00:00")
    if utcoffset.total_seconds() >= 0:
        utcoffset = f"+{midnight + utcoffset:%H:%M}"
    else:
        utcoffset = f"-{midnight - utcoffset:%H:%M}"
    return utcoffset


def all_timezones():
    return ZoneInfoFile(getzoneinfofile_stream()).zones.keys()


def print_timezones(reftime):
    for timezone_str in all_timezones():
        tz = dateutil.tz.gettz(timezone_str)
        utcoffset = format_utcoffset(tz, reftime)
        print(f"{timezone_str:<30} UTC{utcoffset}")


def print_table(timezones, reftime, long=False):
    timezones_per_utcoffset = defaultdict(list)
    utcoffset_for_timezone = {}
    for timezone_str in all_timezones():
        tz = dateutil.tz.gettz(timezone_str)
        timezones_per_utcoffset[format_utcoffset(tz, reftime)].append(timezone_str)
        utcoffset_for_timezone[timezone_str] = format_utcoffset(tz, reftime)

    max_len_also = 120
    header = f"{'Name':<20} {'Abbr':<5} {'UTC offset':<10} {'Time':<18} {'Same time also in':<{max_len_also+4}}"
    print(header)
    print("=" * len(header))
    for abbr, timezone in timezones.items():
        tz = dateutil.tz.gettz(timezone)
        if tz is None:
            tz = dateutil.parser.parse("00:00 " + timezone).tzinfo
        utcoffset = format_utcoffset(tz, reftime)
        info = f"({abbr:<6} UTC{utcoffset})"
        also_in_str = " ".join(sorted(timezones_per_utcoffset[utcoffset]))
        if len(also_in_str) > max_len_also and not long:
            also_in_str = also_in_str[:max_len_also] + "..."
        print(
            f"{timezone:<20} {abbr:<5} UTC{utcoffset:<7} {reftime.astimezone(tz):%Y-%m-%d %H:%M}    {also_in_str}"
        )


def main(args=None):
    timezones = TIMEZONES.copy()

    parser = ArgumentParser()
    parser.add_argument("time", nargs="*")
    parser.add_argument("--long", action="store_true")
    parser.add_argument("--extra-list", nargs="+")
    parser.add_argument("--list-timezones", action="store_true")
    args = parser.parse_args(args)

    timezones_for_parser = {k: dateutil.tz.gettz(v) for k, v in timezones.items()}
    if len(args.time) > 0:
        time = " ".join(args.time)
        reftime = dateutil.parser.parse(time, tzinfos=timezones_for_parser)
    else:
        reftime = datetime.now()
    if reftime.tzinfo is None:
        reftime = reftime.replace(tzinfo=dateutil.tz.tzlocal())

    if args.list_timezones:
        print_timezones(reftime)
        return

    if args.extra_list is not None:
        for abbr in args.extra_list:
            timezones[abbr] = abbr

    print_table(timezones, reftime, long=args.long)


if __name__ == "__main__":
    main()
