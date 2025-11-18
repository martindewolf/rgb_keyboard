#!/usr/bin/env python3
"""
RGB Keyboard GUI Controller (pure tkinter versie)

Gebruikt het bestaande `keyboard_light` CLI-commando om de RGB-instellingen toe te passen.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import subprocess
import sys
from .arguments import Pattern, DEFAULT_PATTERN, DEFAULT_COLORS


class RGBKeyboardGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RGB Keyboard Controller")
        self.geometry("800x500")
        self.minsize(700, 400)

        self.colors = DEFAULT_COLORS.copy()
        self.pattern_var = tk.StringVar(value=DEFAULT_PATTERN)
        self.speed_var = tk.IntVar(value=5)
        self.intensity_var = tk.IntVar(value=16)

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main, text="RGB Keyboard Controller", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 10))

        top_frame = ttk.Frame(main)
        top_frame.pack(fill=tk.X, pady=5)

        pattern_frame = ttk.Frame(top_frame)
        pattern_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(pattern_frame, text="Pattern:").pack(anchor="w")
        patterns = list(Pattern.choices())
        pattern_combo = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_var,
            values=patterns,
            state="readonly",
            width=15,
        )
        pattern_combo.pack()

        speed_frame = ttk.Frame(top_frame)
        speed_frame.pack(side=tk.LEFT, padx=30)
        ttk.Label(speed_frame, text="Speed (0–8):").pack(anchor="w")
        speed_scale = ttk.Scale(
            speed_frame,
            from_=0,
            to=8,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=lambda v: self._update_label(self.speed_value_label, int(float(v))),
        )
        speed_scale.pack(fill=tk.X)
        self.speed_value_label = ttk.Label(speed_frame, text=str(self.speed_var.get()))
        self.speed_value_label.pack(anchor="e")

        intensity_frame = ttk.Frame(top_frame)
        intensity_frame.pack(side=tk.LEFT, padx=30)
        ttk.Label(intensity_frame, text="Intensity (0–32):").pack(anchor="w")
        intensity_scale = ttk.Scale(
            intensity_frame,
            from_=0,
            to=32,
            orient=tk.HORIZONTAL,
            variable=self.intensity_var,
            command=lambda v: self._update_label(self.intensity_value_label, int(float(v))),
        )
        intensity_scale.pack(fill=tk.X)
        self.intensity_value_label = ttk.Label(intensity_frame, text=str(self.intensity_var.get()))
        self.intensity_value_label.pack(anchor="e")

        color_section = ttk.Labelframe(main, text="Colors", padding=10)
        color_section.pack(fill=tk.BOTH, expand=True, pady=10)

        self.colors_frame = ttk.Frame(color_section)
        self.colors_frame.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(color_section)
        btn_frame.pack(fill=tk.X)

        add_btn = ttk.Button(btn_frame, text="Add Color…", command=self.add_color)
        add_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_colors)
        clear_btn.pack(side=tk.LEFT, padx=5)

        preset_btn = ttk.Button(btn_frame, text="Rainbow Preset", command=self.set_rainbow_preset)
        preset_btn.pack(side=tk.LEFT, padx=5)

        fire_btn = ttk.Button(btn_frame, text="Fire Preset", command=self.set_fire_preset)
        fire_btn.pack(side=tk.LEFT, padx=5)

        ocean_btn = ttk.Button(btn_frame, text="Ocean Preset", command=self.set_ocean_preset)
        ocean_btn.pack(side=tk.LEFT, padx=5)

        apply_frame = ttk.Frame(main)
        apply_frame.pack(fill=tk.X, pady=10)

        self.apply_button = ttk.Button(apply_frame, text="Apply to Keyboard", command=self.apply_settings)
        self.apply_button.pack(ipady=5)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor="w", relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_colors_display()

    def _update_label(self, label: tk.Label, value: int) -> None:
        """Update label text with a value."""
        label.config(text=str(value))

    def _show_success_dialog(self) -> None:
        """Show custom success dialog with Ok and Exit buttons."""
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = ttk.Label(dialog, text="Settings applied to keyboard.", padding=20)
        label.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        ok_btn = ttk.Button(button_frame, text="Ok", command=lambda: (dialog.destroy(), self.status_var.set("Ready")))
        ok_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        exit_btn = ttk.Button(button_frame, text="Exit", command=self.quit)
        exit_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def update_colors_display(self) -> None:
        """Update the colors display frame."""
        for child in self.colors_frame.winfo_children():
            child.destroy()

        if not self.colors:
            ttk.Label(self.colors_frame, text="No colors selected.").pack(anchor="w")
            return

        for idx, color in enumerate(self.colors):
            item_frame = ttk.Frame(self.colors_frame)
            item_frame.pack(side=tk.LEFT, padx=3, pady=3)

            canvas = tk.Canvas(item_frame, width=40, height=40, bg=color, highlightthickness=1)
            canvas.pack()

            ttk.Label(item_frame, text=color).pack()

            remove_btn = ttk.Button(
                item_frame,
                text="X",
                width=2,
                command=lambda i=idx: self.remove_color(i),
            )
            remove_btn.pack(pady=2)

    def add_color(self) -> None:
        """Add a color using the color chooser dialog."""
        color = colorchooser.askcolor(title="Choose a color")
        if color and color[1]:
            self.colors.append(color[1].upper())
            self.update_colors_display()

    def clear_colors(self) -> None:
        """Clear all colors after user confirmation."""
        if messagebox.askyesno("Clear colors", "Remove all colors?"):
            self.colors.clear()
            self.update_colors_display()

    def set_rainbow_preset(self) -> None:
        """Set rainbow color preset."""
        self.colors = [
            "#FF0000", "#FF7F00", "#FFFF00",
            "#00FF00", "#0000FF", "#4B0082", "#9400D3"
        ]
        self.update_colors_display()

    def set_fire_preset(self) -> None:
        """Set fire color preset."""
        self.colors = ["#FF0000", "#FF4500", "#FFA500", "#FFD700"]
        self.update_colors_display()

    def set_ocean_preset(self) -> None:
        """Set ocean color preset."""
        self.colors = ["#000080", "#0000FF", "#00BFFF", "#87CEEB"]
        self.update_colors_display()

    def remove_color(self, index: int) -> None:
        """Remove a color at the given index."""
        if 0 <= index < len(self.colors):
            self.colors.pop(index)
            self.update_colors_display()

    def apply_settings(self) -> None:
        """Apply the current settings to the keyboard."""
        if not self.colors:
            messagebox.showwarning("No colors", "Please add at least one color.")
            return

        colors_str = ",".join(self.colors)
        pattern = self.pattern_var.get()
        speed = int(self.speed_var.get())
        intensity = int(self.intensity_var.get())

        cmd = [
            "keyboard_light",
            "-c", colors_str,
            "-p", pattern,
            "-s", str(speed),
            "-i", str(intensity),
        ]

        self.status_var.set("Applying settings…")
        self.apply_button.config(state=tk.DISABLED)
        self.update_idletasks()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except FileNotFoundError:
            self.status_var.set("Error: keyboard_light not found")
            messagebox.showerror(
                "Command not found",
                "The 'keyboard_light' command was not found.\n"
                "Is the rgb-keyboard package installed in this environment?"
            )
        except subprocess.TimeoutExpired:
            self.status_var.set("Error: command timeout")
            messagebox.showerror("Timeout", "Command took too long.")
        else:
            if result.returncode == 0:
                self.status_var.set("Settings applied successfully.")
                self._show_success_dialog()
            else:
                err = result.stderr or result.stdout or "<no output>"
                self.status_var.set("Error applying settings.")
                messagebox.showerror(
                    "Error",
                    f"Failed to apply settings.\n\nCommand:\n{' '.join(cmd)}\n\nOutput:\n{err}",
                )
        finally:
            self.apply_button.config(state=tk.NORMAL)


def main() -> None:
    """Main entry point for the GUI."""
    app = RGBKeyboardGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
