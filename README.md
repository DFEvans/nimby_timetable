# NIMBY Timetable

A set of tooling for converting real-world timetables to timings for [NIMBY Rails](https://store.steampowered.com/app/1134710/NIMBY_Rails/).

The output is designed for NIMBY's "Fixed Departure" mode, where all times
are relative to the departure time from the first stop. The departure time
from the first stop is set to 00:01:00. If you desire a different first
stop departure time (to have a train arrive in the platform earlier without
a separate order that gets it there), you can input the times from this
tool, then input the new time for the first stop and use Shift-Enter / 
Shift-click apply to modify all other timings to match.

## Realtime Trains (RTT) Parser

This will read a set of train timings from a page on realtimetrains.co.uk.
Note that the URL must be the train, not a station. 

```
RTT URL: https://www.realtimetrains.co.uk/service/gb-nr:Y03156/2025-06-16/detailed

2A90 14:36 MAN - CRE
Manchester Piccadilly [MAN]              9   00:01:00       SL
Mauldeth Road [MAU]                          00:08:00
Burnage [BNA]                                00:10:00
East Didsbury [EDY]                          00:12:00
Gatley [GTY]                                 00:14:30
Heald Green [HDG]                        2   00:17:30            <½>
Manchester Airport [MIA]                 2A  00:26:00
Styal [SYA]                                  00:30:30
Wilmslow [WML]                           2   00:41:30
Alderley Edge [ALD]                      2   00:45:00
Holmes Chapel [HCH]                          00:53:00
Sandbach [SDB]                           1   00:57:30       FL   [1]
 Crewe Signal Ce154                           01/02/00           (1)
Crewe [CRE]                              1
```

## London Underground (LUL) Parser

This will take a set of copy-pasted times for a train from the London
Underground working timetable PDFs. The parser will deal with the data
being presented with some unusual line breaks (particularly for fractional
minute timings).

When copying times, the stations aren't known (as they are on the far left
of the page), so stations are simply denoted S01, S02, ... in sequence.

```
Input timetable:
1 9 55
1 9 59
20 031
2
20 051
2
20 091
2
20 131
2
20b221
2
22

LUL 19:55
S01                                          00:01:00
S02                                          00:05:00
S03                                          00:09:30
S04                                          00:11:30
S05                                          00:15:30
S06                                          00:19:30
S07
```

## Internal details

There are four key internal data structures:
* `Timetable`
* `Location`
* `NimbyTimetable`
* `NimbyLocation`

The non-NIMBY structures contain real world clockface timings - so a train
departing its first stop at 16:00:00 is stored as that. The NIMBY
structures contain relative timings, setting the departure time from the
first stop as 00:01:00.

Terminology in the data structures derives from the data structures used
in the UK's national network timetable system.

### `Timetable`

A `Timetable` is a list of locations a train visits in sequence. It
contains:
* `locations: list[Location]`: containing an ordered sequence of locations the
  train visits.
* `td: str`: a free text field containing an identifier for the train.

A `Timetable` can be converted to `NimbyTimetable` by calling
`timetable.to_nimby_timetable()`.

### `Location`

A `Location` describes a station or passing point that a train visits.
It contains:
* `name: str`: The name of the location.
* `arrival_time: datetime | None`: The time the train arrives at the
  location. This field is not used.
* `departure_time: datetime | None`: The time a train ***departs or***
  ***passes*** a location.
* `platform: str | None`: The platform the train calls at. Cosmetic.
* `is_pass: bool`: Whether the train stops at (`False`) or passes
  (`True`) the location. Affects the formatting of the times in the
  timetable display.
* `path: str | None`: The track the train arrives on.
* `line: str | None`: The track the train departs on.
* `path_allowance: str | None`: The extra time allowed between this
  location and the next one due to timetabled conflicting moves.
* `eng_allowance: str | None`: The extra time allowed between this
  location and the next one to account for potential engineering
  work or temporary speed restrictions.
* `perf_allowance: str | None`: The extra time allowed between this
  location and the next one to account for day-to-day late running.

Note that the allowance fields are free text fields, so they can
display the raw allowance values from the data source, e.g.
`1` or `2½`.

### `NimbyTimetable`

A `NimbyTimetable` is a list of locations a train visits in sequence
like a `Timetable`, but in relative times. It contains:
* `locations: list[NimbyLocation]`: containing an ordered sequence of locations the
  train visits.

A `NimbyTimetable` can be created from a `Timetable` by calling
`timetable.to_nimby_timetable()`. When this is done, the locations are
transformed as follows:
* The first `Location` is transformed to a `NimbyLocation` with a 
  relative departure time of `initial_minutes_offset` minutes,
  defaulting to 1 minute
* For each subsequent `Location`, transform it to a `NimbyLocation`:
  * If the `Location` has `is_pass` set:
    * If none of `path`, `line`, or the three allowance fields are set:
      * Skip the `Location`
  * If the `Location` has a `departure_time`:
    * Compute the time difference between the first `Location`'s departure
      time and the current `Location`'s departure time, add 
      `initial_minutes_offset`, and set that as the `NimbyLocation`'s
      departure time

`Locations` that have `is_pass` set but one of the `path`, `line`, or
allowance fields set are included in the `NimbyTimetable` to help the
user see important routing or timing information.

### `NimbyLocation`
A `NimbyLocation` describes a station or passing point that a train visits
like a `Location`, using relative times. It contains:
* `name: str`: The name of the location.
* `departure: timedelta | None`: The relative time a train ***departs or***
  ***passes*** a location.
* `platform: str | None`: The platform the train calls at. Cosmetic.
* `is_pass: bool`: Whether the train stops at (`False`) or passes
  (`True`) the location. Affects the formatting of the times in the
  timetable display.
* `path: str | None`: The track the train arrives on.
* `line: str | None`: The track the train departs on.
* `path_allowance: str | None`: The extra time allowed between this
  location and the next one due to timetabled conflicting moves.
* `eng_allowance: str | None`: The extra time allowed between this
  location and the next one to account for potential engineering
  work or temporary speed restrictions.
* `perf_allowance: str | None`: The extra time allowed between this
  location and the next one to account for day-to-day late running.

When `str(nimby_location)` is called, a formatted output is generated
for display. The formatting is:
* `name`, padded to 40 characters
* `platform`, padded to 3 characters, if set
* `departure`, formatted as below
* `path`, padded to 3 characters, if set
* `line`, padded to 3 characters, if set
* `eng_allowance`, `path_allowance`, and `perf_allowance`, formatted as
  below

The time is formatted as follows:
* If `is_pass` is False, the separator is `:`
* Otherwise, the separator is `/` and the time is indented by a space
* The time is then formatted as `hh:mm:ss` or `hh/mm/ss`

The allowances are formatted as follows:
* If `eng_allowance` is set, it is formatted like `[1]`
* If `path_allowance` is set, it is formatted as `(1)`
* If `perf_allowance` is set, it is formatted as `<1>`
* The values are displayed in the order given above
