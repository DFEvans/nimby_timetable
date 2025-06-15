from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Location:
    name: str
    arrival_time: datetime | None
    departure_time: datetime | None
    platform: str | None
    is_pass: bool
    path: str | None
    line: str | None
    path_allowance: str | None
    eng_allowance: str | None
    perf_allowance: str | None

    def format_time(self, t: datetime, is_pass: bool = False) -> str:
        if not t:
            return ""
        
        separator = "/" if is_pass else ":"

        s = f"{t.hour:02d}{separator}{t.minute:02d}"
        if t.second == 30:
            s += "½"
        
        return s
    
    @property
    def timetable_code(self) -> str:
        try:
            code = self.name.split("[")[1].split("]")[0]
        except IndexError:
            code = self.name
        
        return code

    def __str__(self) -> str:
        s = f"{self.name:30s} {self.format_time(self.arrival_time):6s} {self.format_time(self.departure_time, is_pass=self.is_pass):6s}"

        allowance_string = ""
        if self.eng_allowance:
            allowance_string += f" [{self.eng_allowance}]"
        if self.path_allowance:
            allowance_string += f" ({self.path_allowance})"
        if self.perf_allowance:
            allowance_string += f" <{self.perf_allowance}>"

        return s + allowance_string


@dataclass
class NimbyLocation:
    name: str
    departure: timedelta | None
    platform: str | None
    is_pass: bool
    path: str | None
    line: str | None
    path_allowance: str | None
    eng_allowance: str | None
    perf_allowance: str | None

    @classmethod
    def from_location(cls, departure: timedelta | None, location: Location) -> NimbyLocation:
        return cls(
            name=location.name,
            departure=departure,
            platform=location.platform,
            is_pass=location.is_pass,
            path=location.path,
            line=location.line,
            path_allowance=location.path_allowance,
            eng_allowance=location.eng_allowance,
            perf_allowance=location.perf_allowance,
        )

    def __str__(self) -> str:
        if self.departure:
            hours = int(self.departure.total_seconds() // 3600)
            minutes = int((self.departure.total_seconds() // 60) % 60)
            seconds = int(self.departure.total_seconds() % 60)

            lead = " " if self.is_pass else ""
            separator = "/" if self.is_pass else ":"

            time_string = f"{lead}{hours:02d}{separator}{minutes:02d}{separator}{seconds:02d}"
        else:
            time_string = ""

        if self.is_pass:
            name = f" {self.name:39s}"
        else:
            name = f"{self.name:40s}"

        allowance_string = ""
        if self.eng_allowance:
            allowance_string += f" [{self.eng_allowance}]"
        if self.path_allowance:
            allowance_string += f" ({self.path_allowance})"
        if self.perf_allowance:
            allowance_string += f" <{self.perf_allowance}>"
        
        return f"{name:40s} {self.platform:3s} {time_string:10s} {self.path:3s} {self.line:3s} {allowance_string}"
