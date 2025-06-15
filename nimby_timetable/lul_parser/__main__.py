from .lul_parser import get_input, parse_lines

def main():
    while True:
        lines = get_input()
        timetable = parse_lines(lines)
        print()
        print("LUL", timetable.locations[0].format_time(timetable.locations[0].departure_time))
        print(timetable.to_nimby_timetable())
        print()


if __name__ == "__main__":
    main()
