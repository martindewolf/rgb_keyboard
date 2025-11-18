import argparse
from enum import Enum

DEFAULT_PATTERN = "breathing"
DEFAULT_COLORS = ["#FF0000", "#FFFFFF", "#0000FF"]

class Color(Enum):
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    TEAL = "#00FFFF"
    PURPLE = "#FF00FF"
    PINK = "#FF0077"
    YELLOW = "#FF7700"
    WHITE = "#FFFFFF"
    ORANGE = "#FF1C00"
    OLIVE = "#808000"
    MAROON = "#800000"
    BROWN = "#A52A2A"
    GRAY = "#808080"
    SKYBLUE = "#87CEEB"
    NAVY = "#000080"
    CRIMSON = "#DC143C"
    DARKGREEN = "#006400"
    LIGHTGREEN = "#90EE90"
    GOLD = "#FFD700"
    VIOLET = "#EE82EE"

    def __init__(self, hex_value: str):
        self.hex_value = hex_value
        if hex_value[0] != "#":
            raise ValueError("Should pass a RGB code with pattern #RRGGBB")
        r, g, b = int(hex_value[1:3], 16), int(hex_value[3:5], 16), int(hex_value[5:], 16)
        self.rgb = [r, g, b]

    @staticmethod
    def choices():
        return [e.name.lower() for e in Color]
    
    @staticmethod
    def get_by_name(name: str):
        try:
            return Color[name.upper()]
        except KeyError:
            # Try direct hex value (case-insensitive)
            name_upper = name.upper()
            for color in Color:
                if color.hex_value.upper() == name_upper:
                    return color
            
            # If it's a hex color format, create a temporary Color-like object
            if name_upper.startswith("#") and len(name_upper) == 7:
                # Validate it's a valid hex color
                try:
                    int(name_upper[1:], 16)
                    # Create a simple object with the rgb attribute needed by the driver
                    class HexColor:
                        def __init__(self, hex_val):
                            self.hex_value = hex_val
                            r, g, b = int(hex_val[1:3], 16), int(hex_val[3:5], 16), int(hex_val[5:], 16)
                            self.rgb = [r, g, b]
                    return HexColor(name_upper)
                except ValueError:
                    raise ValueError(f"Invalid hex color: {name}")
            
            raise ValueError(f"Unknown color: {name}")

class Pattern(Enum):
    SOLID = 0x01
    BREATHING = 0x02
    WAVE = 0x03
    BLINKING = 0x12
    FLOW = 0x13
    # todo paterns have not been verified
    # copied from - https://github.com/rodgomesc/avell-unofficial-control-center working driver for revision 0.03.
    # RANDOM = 0x04
    # RAINBOW = 0x05
    # RIPPLE = 0x06
    # REACTIVERIPPLE = 0x07
    # MARQUEE = 0x09
    # FIREWORKS = 0x11
    # RAINDROP = 0x0A
    # AURORA = 0x0E

    @staticmethod
    def choices():
        return [e.name.lower() for e in Pattern]
    
    @staticmethod
    def get_by_name(name: str):
        try:
            return Pattern[name.upper()]
        except KeyError:
            raise ValueError(f"Unknown pattern: {name}")


class UltimateHelpFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass
