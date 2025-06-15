from datetime import datetime, timedelta
from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

from nimby_timetable.timetable.location import Location
from nimby_timetable.timetable.timetable import Timetable

class RTTParser:
    def get_date_from_url(self, rtt_url: str) -> datetime:
        tokens = rtt_url.split("/")
        date_token = tokens[-2]
        return datetime.strptime(date_token, r"%Y-%m-%d")

    def parse_page(self, contents: str, date: datetime) -> Timetable:
        page = BeautifulSoup(contents, "html.parser")
        location_list = self.find_location_list(page)
        locations = self.split_locations(location_list)

        is_first_location = True
        last_time = date
        parsed_locations: list[Location] = []
        for location in locations:
            parsed_locations.append(self.parse_location(location, date, last_time, is_first_location))
            is_first_location = False
            last_time = parsed_locations[-1].departure_time
        
        timetable = Timetable(locations=parsed_locations, td=self.extract_td(page))

        return timetable
    
    def extract_td(self, page: BeautifulSoup) -> str:
        return page.find("title").text.split("|")[1][1:5]
    
    def find_location_list(self, page: BeautifulSoup) -> Tag:
        result = page.find("div", attrs={"class": "locationlist"})
        if not result:
            raise ValueError("Could not find locationlist div")

        return result


    def split_locations(self, location_list: Tag) -> list[Tag]:
        locations = []
        for child in location_list.find_all("div", recursive=False):
            if "titlerow" in child["class"]:
                continue

            locations.append(child)
        
        return locations
    
    def parse_location(self, location: Tag, date: datetime, last_time: datetime, is_first_location: bool) -> Location:
        name = location.find("a", attrs={"class": "name"}).get_text()

        wtt_times = location.find("div", attrs={"class": "wtt"})

        if arrival_tag := wtt_times.find("div", attrs={"class": "arr"}):
            arrival = self.parse_time(
                arrival_tag.get_text(),
                date,
                last_time,
            )
        else:
            arrival = None

        if departure_tag := wtt_times.find("div", attrs={"class": "dep"}):
            departure = self.parse_time(
                departure_tag.get_text(),
                date,
                last_time,
            )
        else:
            raise ValueError(f"Could not find departure time at {name}")
        
        path_allowance = None
        eng_allowance = None
        perf_allowance = None

        if allowance_tag := location.find("span", attrs={"class": "allowance"}):
            if path_tag := allowance_tag.find("span", attrs={"class": "pth"}):
                path_allowance = path_tag.get_text()
            if eng_tag := allowance_tag.find("span", attrs={"class": "eng"}):
                eng_allowance = eng_tag.get_text()
            if perf_tag := allowance_tag.find("span", attrs={"class": "prf"}):
                perf_allowance = perf_tag.get_text()


        platform = location.find("div", attrs={"class": "platform"}).get_text()
        path = location.find("div", attrs={"class": "path"}).get_text()
        line = location.find("div", attrs={"class": "line"}).get_text()

        if arrival:
            is_pass = False
        elif is_first_location:
            is_pass = False
        else:
            is_pass = True

        parsed_location = Location(
            name=name,
            arrival_time=arrival,
            departure_time=departure,
            platform=platform,
            is_pass=is_pass,
            path=path,
            line=line,
            path_allowance=path_allowance,
            eng_allowance=eng_allowance,
            perf_allowance=perf_allowance,

        )
        return parsed_location

    def parse_time(self, time_string: str, date: datetime, last_time: datetime) -> Optional[datetime]:
        if time_string == "":
            return None

        hours = int(time_string[0:2])
        minutes = int(time_string[2:4])
        seconds = 30 if "½" in time_string else 0

        parsed = date + timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if parsed < last_time:
            # Assume we've passed midnight
            parsed += timedelta(days=1)
        
        return parsed



