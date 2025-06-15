from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from nimby_timetable.timetable.location import Location, NimbyLocation


@dataclass
class Timetable:
    locations: list[Location]
    td: str

    def __str__(self) -> str:
        return "\n".join(str(location) for location in self.locations)
    
    def to_nimby_timetable(self, initial_minutes_offset: int = 1) -> NimbyTimetable:
        first_location = self.locations[0]
        offset = timedelta(minutes=initial_minutes_offset)
        first_nimby_location = NimbyLocation.from_location(
            offset,
            first_location,
        )

        nimby_locations = [first_nimby_location]

        for location in self.locations[1:]:
            if location.is_pass:
                if not any((location.path, location.line, location.path_allowance, location.eng_allowance, location.perf_allowance)):
                    continue

            if location.departure_time:
                time_offset = location.departure_time - first_location.departure_time + offset
            else:
                time_offset = None

            nimby_locations.append(
                NimbyLocation.from_location(
                    time_offset,
                    location
                )
            )
        
        return NimbyTimetable(nimby_locations)



@dataclass
class NimbyTimetable:
    locations: list[NimbyLocation]

    def __str__(self) -> str:
        return "\n".join(str(location) for location in self.locations)