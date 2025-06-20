from dataclasses import dataclass

from nimby_timetable.downloader.downloader import WebDownloader
from nimby_timetable.rtt_parser.rtt_parser import RTTParser


@dataclass
class CommandLineArguments:
    url: str


def main():
    downloader = WebDownloader()
    rtt_parser = RTTParser()

    try:
        while True:
            url = input("RTT URL: ")
            if not url:
                continue

            timetable = rtt_parser.parse_page(
                downloader.download(url),
                rtt_parser.get_date_from_url(url),
            )
            print()
            print(timetable.td, timetable.locations[0].format_time(timetable.locations[0].departure_time), timetable.locations[0].timetable_code, "-", timetable.locations[-1].timetable_code)
            print(timetable.to_nimby_timetable())
            print()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
