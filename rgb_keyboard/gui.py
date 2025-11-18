#!/usr/bin/env python3
"""
RGB Keyboard GUI Controller (CustomTkinter versie)

Gebruikt het bestaande `keyboard_light` CLI-commando om de RGB-instellingen toe te passen.
"""

import customtkinter as ctk
from tkinter import colorchooser, messagebox
import subprocess
import sys
from .arguments import Pattern, DEFAULT_PATTERN, DEFAULT_COLORS


class RGBKeyboardGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RGB Keyboard Controller")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.colors = DEFAULT_COLORS.copy()
        self.pattern_var = ctk.StringVar(value=DEFAULT_PATTERN)
        self.speed_var = ctk.IntVar(value=5)
        self.intensity_var = ctk.IntVar(value=16)

        self._build_ui()

    def _build_ui(self):
        main = ctk.CTkFrame(self)
        main.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(main, text="RGB Keyboard Controller", font=("Arial", 24, "bold"))
        title.pack(pady=(0, 20))

        top_frame = ctk.CTkFrame(main)
        top_frame.pack(fill=ctk.X, pady=10)

        pattern_frame = ctk.CTkFrame(top_frame)
        pattern_frame.pack(side=ctk.LEFT, padx=10)
        pattern_label = ctk.CTkLabel(pattern_frame, text="Pattern:", font=("Arial", 12))
        pattern_label.pack(anchor="w")
        patterns = list(Pattern.choices())
        pattern_combo = ctk.CTkComboBox(
            pattern_frame,
            values=patterns,
            variable=self.pattern_var,
            state="readonly",
            width=150
        )
        pattern_combo.pack(pady=5)

        speed_frame = ctk.CTkFrame(top_frame)
        speed_frame.pack(side=ctk.LEFT, padx=30)
        speed_label = ctk.CTkLabel(speed_frame, text="Speed (0–8):", font=("Arial", 12))
        speed_label.pack(anchor="w")
        speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0,
            to=8,
            number_of_steps=8,
            variable=self.speed_var,
            command=lambda v: self._update_label(self.speed_value_label, int(float(v))),
        )
        speed_slider.pack(fill=ctk.X, pady=5)
        self.speed_value_label = ctk.CTkLabel(speed_frame, text=str(self.speed_var.get()), font=("Arial", 10))
        self.speed_value_label.pack(anchor="e")

        intensity_frame = ctk.CTkFrame(top_frame)
        intensity_frame.pack(side=ctk.LEFT, padx=30)
        intensity_label = ctk.CTkLabel(intensity_frame, text="Intensity (0–32):", font=("Arial", 12))
        intensity_label.pack(anchor="w")
        intensity_slider = ctk.CTkSlider(
            intensity_frame,
            from_=0,
            to=32,
            number_of_steps=32,
            variable=self.intensity_var,
            command=lambda v: self._update_label(self.intensity_value_label, int(float(v))),
        )
        intensity_slider.pack(fill=ctk.X, pady=5)
        self.intensity_value_label = ctk.CTkLabel(intensity_frame, text=str(self.intensity_var.get()), font=("Arial", 10))
        self.intensity_value_label.pack(anchor="e")

        color_section = ctk.CTkFrame(main)
        color_section.pack(fill=ctk.BOTH, expand=True, pady=20)
        
        color_label = ctk.CTkLabel(color_section, text="Colors", font=("Arial", 14, "bold"))
        color_label.pack(anchor="w", padx=10, pady=(0, 10))

        self.colors_frame = ctk.CTkFrame(color_section)
        self.colors_frame.pack(fill=ctk.X, padx=10, pady=(0, 10))

        btn_frame = ctk.CTkFrame(color_section)
        btn_frame.pack(fill=ctk.X, padx=10)

        add_btn = ctk.CTkButton(btn_frame, text="Add Color…", command=self.add_color, width=120)
        add_btn.pack(side=ctk.LEFT, padx=5)

        clear_btn = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_colors, width=120)
        clear_btn.pack(side=ctk.LEFT, padx=5)

        preset_btn = ctk.CTkButton(btn_frame, text="Rainbow Preset", command=self.set_rainbow_preset, width=120)
        preset_btn.pack(side=ctk.LEFT, padx=5)

        fire_btn = ctk.CTkButton(btn_frame, text="Fire Preset", command=self.set_fire_preset, width=120)
        fire_btn.pack(side=ctk.LEFT, padx=5)

        ocean_btn = ctk.CTkButton(btn_frame, text="Ocean Preset", command=self.set_ocean_preset, width=120)
        ocean_btn.pack(side=ctk.LEFT, padx=5)

        apply_frame = ctk.CTkFrame(main)
        apply_frame.pack(fill=ctk.X, pady=10)

        self.apply_button = ctk.CTkButton(apply_frame, text="Apply to Keyboard", command=self.apply_settings, height=40, font=("Arial", 14))
        self.apply_button.pack(fill=ctk.X)

        self.status_var = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, font=("Arial", 10))
        status_bar.pack(fill=ctk.X, side=ctk.BOTTOM, padx=10, pady=5)

        self.update_colors_display()

    def _update_label(self, label: ctk.CTkLabel, value: int) -> None:
        """Update label text with a value."""
        label.configure(text=str(value))

    def _show_success_dialog(self) -> None:
        """Show custom success dialog with Ok and Exit buttons."""
        dialog = ctk.CTkToplevel(self)
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
        
        label = ctk.CTkLabel(dialog, text="Settings applied to keyboard.", font=("Arial", 12), padx=20, pady=20)
        label.pack(fill=ctk.BOTH, expand=True)
        
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        ok_btn = ctk.CTkButton(button_frame, text="Ok", command=lambda: (dialog.destroy(), self.status_var.set("Ready")))
        ok_btn.pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        
        exit_btn = ctk.CTkButton(button_frame, text="Exit", command=self.quit)
        exit_btn.pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)

    def update_colors_display(self) -> None:
        """Update the colors display frame."""
        for child in self.colors_frame.winfo_children():
            child.destroy()

        if not self.colors:
            label = ctk.CTkLabel(self.colors_frame, text="No colors selected.", font=("Arial", 11))
            label.pack(anchor="w", padx=5)
            return

        for idx, color in enumerate(self.colors):
            item_frame = ctk.CTkFrame(self.colors_frame, fg_color=color, corner_radius=5)
            item_frame.pack(side=ctk.LEFT, padx=3, pady=3)

            label = ctk.CTkLabel(item_frame, text=color, text_color="white", font=("Arial", 9), padx=5, pady=5)
            label.pack()

            remove_btn = ctk.CTkButton(
                item_frame,
                text="X",
                width=30,
                height=25,
                font=("Arial", 10),
                fg_color="red",
                hover_color="darkred",
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
        self.apply_button.configure(state=ctk.DISABLED)
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
            self.apply_button.configure(state=ctk.NORMAL)


def main() -> None:
    """Main entry point for the GUI."""
    app = RGBKeyboardGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
