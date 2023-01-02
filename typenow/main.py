import os
import sys

from time import time
from rich import print
from getch import getch


def get_results(lesson_str: str, mistakes: int, start_time: float, char_nr: int):
    total_chars = len(lesson_str)

    time_taken = int(time() - start_time)
    time_taken_str = (
        (f"{time_taken} seconds")
        if time_taken < 60
        else (f"{time_taken // 60} minutes, {time_taken % 60} seconds")
    )

    try:
        gross_wpm = (char_nr / 5) / (time_taken / 60)
    except ZeroDivisionError:
        gross_wpm = 0
    try:
        accuracy = ((char_nr - mistakes) / char_nr) * 100
    except ZeroDivisionError:
        accuracy = 0

    res = []

    stats = {
        "Time taken": time_taken_str,
        "Gross WPM": int(gross_wpm),
        "Accuracy": f"{accuracy:.2f}% ({mistakes} mistakes [bold]/[/bold] {char_nr} chars)",
        "Progress": f"{(char_nr / len(lesson_str) * 100):.2f}% ({char_nr}/{len(lesson_str)} chars)",
    }

    for key, value in stats.items():
        res.append(f"[bold aqua]{key}[/bold aqua]: [dark_gray]{value}[/dark_gray]")

    return "\n".join(res)


def type_test(lesson_str: str):
    lines = lesson_str.splitlines(keepends=True)
    start_time = time()

    mistakes = 0
    char_nr = 0

    for line in lines:
        for pos, char in enumerate(line):
            is_mistake = False
            while True:
                term_width, term_heigth = os.get_terminal_size()
                center = term_width // 2

                padded_line = (" " * (center - 1)) + line.replace("\n", "↵")
                cropped_line = padded_line[pos : term_width - 1 + pos]

                progress_bar_length = int(char_nr / len(lesson_str) * term_width)

                print(
                    (progress_bar_length * "=")
                    + (">" if progress_bar_length < term_width else "")
                    + f"\n\n[bright_black]{cropped_line[:center - 1]}[/bright_black]"
                    + f"{'[white]' if not is_mistake else '[red]'}{cropped_line[center - 1]}{'[/white]' if not is_mistake else '[/red]'}"
                    + f"[white]{cropped_line[center:]}[/white]"
                    + "\n"
                    + (" " * (center - 1))
                    + "^"
                    + "\n\n"
                    + get_results(lesson_str, mistakes, start_time, char_nr)
                    + ((term_heigth - 10) * "\n")
                )

                typed_char = getch().replace("\r", "\n")

                match typed_char:
                    case "":
                        exit(0)
                    case "\x7f":
                        continue

                if typed_char == char:
                    break

                # print("Should be", ord(char))
                # print("Is", ord(typed_char))
                # input()
                is_mistake = True
                mistakes += 1

            char_nr += 1

    print("Test finished.\n")
    print(get_results(lesson_str, mistakes, start_time, char_nr))
    print((term_heigth - 8) * "\n")


def main():
    error = False

    if len(sys.argv) != 2:
        error = True
    elif not os.path.isfile(sys.argv[1]):
        error = True

    if error:
        print("[red][bold]Error[bold]: No file specified.[/red]")
        print("\n[bold]Usage:[/bold] typenow <file>\n<file> must be a valid text file.")
        exit(1)

    with open(sys.argv[1], "r", encoding="UTF-8") as f:
        type_test(f.read())
