"""
Driver for RGB LED keyboard backlight controller Integrated Technology Express ITE Device(8291) Rev 0.02.

This device uses a USB connector. Controlling it is just a matter of writing the right bytes to the device.
"""
from ctypes import create_string_buffer
from rgb_keyboard.arguments import Color, Pattern
import hid


class KeyboardController:
    """
    Controller to configure the RGB keyboard lights.
    """
    vendor_id = 0x048d
    product_id = 0xce00
    color_flag_prefix = [0x14, 0x00]
    color_flag_suffix = [0x00, 0x00]
    pattern_flag_prefix = [0x08, 0x02]


    def send_args(self, colors: list[Color], pattern: Pattern, intensity: int = 0x16, speed: int = 0x05) -> None:
        """Send configuration to the keyboard."""
        rgbs = [color.rgb for color in colors]
        cmds = [
            self.color_flag_prefix + [region] + rgb + self.color_flag_suffix
            for region, rgb in enumerate(rgbs, 1)
        ]
        # Define other properties
        properties = self.pattern_flag_prefix + [pattern.value, speed, intensity, 0x08, 0x00, 0x01]
        cmds.append(properties)
        self._send_command(*cmds)

    def _send_command(self, *cmds) -> None:
        """Send command bytes to the HID device."""
        with hid.Device(self.vendor_id, self.product_id) as h:
            h.nonblocking = 1
            for cmd in cmds:
                buf = self._c_str(cmd)
                h.send_feature_report(buf)

    def _c_str(self, cmd):
        """Convert command list to C string buffer."""
        data = bytearray(cmd)
        buf = create_string_buffer(len(data))
        for n, byte in enumerate(data):
            buf[n] = byte
        return buf
