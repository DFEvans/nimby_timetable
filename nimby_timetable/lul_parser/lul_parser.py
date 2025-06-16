from datetime import datetime, timedelta

from nimby_timetable.timetable.location import Location
from nimby_timetable.timetable.timetable import Timetable


OFFSET_LOOKUP = {
    "+": timedelta(minutes=0, seconds=15),
    "a": timedelta(minutes=0, seconds=30),
    "A": timedelta(minutes=0, seconds=45),
    "b": timedelta(minutes=1, seconds=0),
    "B": timedelta(minutes=1, seconds=15),
    "c": timedelta(minutes=1, seconds=30),
    "C": timedelta(minutes=1, seconds=45),
    "d": timedelta(minutes=2, seconds=0),
    "D": timedelta(minutes=2, seconds=15),
    "e": timedelta(minutes=2, seconds=30),
    "E": timedelta(minutes=2, seconds=45),
    "f": timedelta(minutes=3, seconds=0),
    "F": timedelta(minutes=3, seconds=15),
    "g": timedelta(minutes=3, seconds=30),
    "G": timedelta(minutes=3, seconds=45),
    "h": timedelta(minutes=4, seconds=0),
    "H": timedelta(minutes=4, seconds=15),
    "j": timedelta(minutes=4, seconds=30),
    "J": timedelta(minutes=4, seconds=45),
    "k": timedelta(minutes=5, seconds=0),
}


def get_input() -> list[str]:
    print("Input timetable: ")
    lines = []
    while True:
        line = input()
        if not line.strip():
            return lines
        
        lines.append(line)


def parse_time(digits: list[str], date: datetime, last_time: datetime):
    hour = int("".join(digits[0:2]))
    minute = int("".join(digits[2:4]))
    if len(digits) > 4:
        numerator = int(digits[4])
        denominator = int(digits[5])
        second = int(60 * numerator / denominator)
    else:
        second = 0
    
    time = date + timedelta(hours=hour, minutes=minute, seconds=second)
    if time < last_time:
        time += timedelta(days=1)
    
    return time


def parse_offset(chars: list[str], departure_time: datetime) -> datetime | None:
    for char in chars:
        try:
            offset = OFFSET_LOOKUP[char]
        except KeyError:
            continue

        return departure_time - offset

    return None


def parse_lines(lines: list[str]) -> Timetable:
    date = datetime(2000, 1, 1)
    last_time = date
    locations: list[Location] = []
    while lines:
        digits = []
        chars = []
        line = lines.pop(0).strip()

        for char in line:
            if char.isnumeric():
                digits.append(char)
            elif not char.isspace():
                chars.append(char)

        if len(digits) < 2:
            # Either no digits, or a line with a single digit
            # which is usually a platform number
            continue

        if len(digits) != 4 and len(digits) != 6 and lines:
            line = lines.pop(0)
            for char in line:
                if char.isnumeric():
                    digits.append(char)
        
        if len(digits) != 4 and len(digits) != 6:
            continue

        departure_time = parse_time(digits, date, last_time)
        arrival_time = parse_offset(chars, departure_time)
        last_time = departure_time

        locations.append(Location(
            name = f"S{len(locations) + 1:02d}",
            arrival_time=arrival_time,
            departure_time=departure_time,
            platform="",
            is_pass=False,
            path="",
            line="",
            path_allowance="",
            eng_allowance="",
            perf_allowance="",
        ))

    locations[-1].arrival_time = locations[-1].departure_time
    locations[-1].departure_time = None

    return Timetable(
        locations=locations,
        td="LUL",
    )

        



