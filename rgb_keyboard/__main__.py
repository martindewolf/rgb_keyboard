import argparse
import os
from itertools import cycle
from elevate import elevate

from rgb_keyboard.driver import KeyboardController
from rgb_keyboard.arguments import Color, Pattern, UltimateHelpFormatter, DEFAULT_PATTERN, DEFAULT_COLORS


parser = argparse.ArgumentParser(
    description="""Supply zero or more options [-c|s|i|p|r].
        Examples:
            keyboard_light
            keyboard_light -p solid
            keyboard_light -cred,#FF2200,#FF4400,blue -p wave -i 32 -s 8""",
    formatter_class=UltimateHelpFormatter
)


parser.add_argument("-c", "--colors",
                    help=f"Select colors to generate a light pattern. "
                         f"Use a comma separated list with #RRGGBB colors or {{{','.join(Color.choices())}}}.",
                    default=",".join(DEFAULT_COLORS))
parser.add_argument("-p", "--pattern",
                    help="Pattern of the effect.",
                    default=DEFAULT_PATTERN,
                    choices=Pattern.choices())
parser.add_argument("-s", "--speed",
                    help="Speed of the effect transitions. 1 (fast) to 8 (slow), 0  is no transition.",
                    default=5, type=int)
parser.add_argument("-i", "--intensity",
                    help="Intensity of the effect. 0 (low) to 32 (high).",
                    default=16, type=int)
parser.add_argument("-r", "--no_root_privileges", dest='root', action='store_true',
                    help="Set argument if no root privileges should be requested.",
                    default=False)


def main() -> None:
    """Main entry point for the CLI."""
    parsed = parser.parse_args()
    colors = [Color.get_by_name(color) for color in parsed.colors.split(",")]
    colors = _expand_colors_to(colors, 7)
    pattern = Pattern.get_by_name(parsed.pattern)

    if os.geteuid() != 0 and not parsed.root:
        elevate()

    KeyboardController().send_args(colors, pattern, parsed.intensity, parsed.speed)


def _expand_colors_to(colors: list[Color], count: int) -> list[Color]:
    """Repeat colors until reaching the desired count."""
    color_cycle = cycle(colors)
    return [next(color_cycle) for _ in range(count)]

if __name__ == "__main__":
    main()
