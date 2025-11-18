#!/usr/bin/env python3
"""
RGB Keyboard GUI Controller (PyQt6 versie)

Gebruikt het bestaande `keyboard_light` CLI-commando om de RGB-instellingen toe te passen.
"""

import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSlider, QPushButton, QScrollArea, QFrame, QColorDialog,
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from .arguments import Pattern, DEFAULT_PATTERN, DEFAULT_COLORS


class ColorBox(QFrame):
    """Custom widget for displaying a color with remove button."""
    remove_requested = pyqtSignal(int)
    move_left_requested = pyqtSignal(int)
    move_right_requested = pyqtSignal(int)
    selected = pyqtSignal(int)
    
    def __init__(self, color: str, index: int):
        super().__init__()
        self.index = index
        self.color = color
        self.is_selected = False
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px; border: 2px solid gray;")
        self.setFixedSize(60, 60)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        label = QLabel(color)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 8px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        remove_btn = QPushButton("X")
        remove_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        remove_btn.setFixedSize(40, 20)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        """Handle click to select color."""
        self.is_selected = not self.is_selected
        if self.is_selected:
            self.setStyleSheet(f"background-color: {self.color}; border-radius: 5px; border: 3px solid #0066FF;")
        else:
            self.setStyleSheet(f"background-color: {self.color}; border-radius: 5px; border: 2px solid gray;")
        self.selected.emit(self.index)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self.is_selected = selected
        if self.is_selected:
            self.setStyleSheet(f"background-color: {self.color}; border-radius: 5px; border: 3px solid #0066FF;")
        else:
            self.setStyleSheet(f"background-color: {self.color}; border-radius: 5px; border: 2px solid gray;")


class RGBKeyboardGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("RGB Keyboard Controller")
        self.setGeometry(100, 100, 900, 600)
        
        self.colors = DEFAULT_COLORS.copy()
        self.selected_color_index = None
        
        self._build_ui()
        
    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("RGB Keyboard Controller")
        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Controls frame
        controls_layout = QHBoxLayout()
        
        # Pattern
        pattern_layout = QVBoxLayout()
        pattern_label = QLabel("Pattern:")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(Pattern.choices())
        self.pattern_combo.setCurrentText(DEFAULT_PATTERN)
        pattern_layout.addWidget(pattern_label)
        pattern_layout.addWidget(self.pattern_combo)
        controls_layout.addLayout(pattern_layout)
        
        # Speed
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Speed (0–8):")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(8)
        self.speed_slider.setValue(5)
        self.speed_value_label = QLabel("5")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_value_label.setText(str(v)))
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)
        controls_layout.addLayout(speed_layout)
        
        # Intensity
        intensity_layout = QVBoxLayout()
        intensity_label = QLabel("Intensity (0–32):")
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(0)
        self.intensity_slider.setMaximum(32)
        self.intensity_slider.setValue(16)
        self.intensity_value_label = QLabel("16")
        self.intensity_slider.valueChanged.connect(lambda v: self.intensity_value_label.setText(str(v)))
        intensity_layout.addWidget(intensity_label)
        intensity_layout.addWidget(self.intensity_slider)
        intensity_layout.addWidget(self.intensity_value_label)
        controls_layout.addLayout(intensity_layout)
        
        main_layout.addLayout(controls_layout)
        
        # Colors section
        colors_label = QLabel("Colors")
        colors_font = colors_label.font()
        colors_font.setPointSize(12)
        colors_font.setBold(True)
        colors_label.setFont(colors_font)
        main_layout.addWidget(colors_label)
        
        # Colors display
        self.colors_scroll = QScrollArea()
        self.colors_scroll.setWidgetResizable(True)
        self.colors_scroll.setMaximumHeight(120)
        self.colors_frame = QFrame()
        self.colors_layout = QHBoxLayout()
        self.colors_layout.setContentsMargins(0, 0, 0, 0)
        self.colors_layout.setSpacing(5)
        self.colors_frame.setLayout(self.colors_layout)
        self.colors_scroll.setWidget(self.colors_frame)
        main_layout.addWidget(self.colors_scroll)
        
        # Buttons frame
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Color…")
        add_btn.clicked.connect(self.add_color)
        buttons_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_colors)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addSpacing(10)
        
        move_left_btn = QPushButton("← Move Left")
        move_left_btn.clicked.connect(self.move_color_left)
        buttons_layout.addWidget(move_left_btn)
        
        move_right_btn = QPushButton("Move Right →")
        move_right_btn.clicked.connect(self.move_color_right)
        buttons_layout.addWidget(move_right_btn)
        
        buttons_layout.addSpacing(10)
        rainbow_btn = QPushButton("Rainbow Preset")
        rainbow_btn.clicked.connect(self.set_rainbow_preset)
        buttons_layout.addWidget(rainbow_btn)
        
        fire_btn = QPushButton("Fire Preset")
        fire_btn.clicked.connect(self.set_fire_preset)
        buttons_layout.addWidget(fire_btn)
        
        ocean_btn = QPushButton("Ocean Preset")
        ocean_btn.clicked.connect(self.set_ocean_preset)
        buttons_layout.addWidget(ocean_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Apply button
        self.apply_btn = QPushButton("Apply to Keyboard")
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.apply_btn.clicked.connect(self.apply_settings)
        main_layout.addWidget(self.apply_btn)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        
        self.update_colors_display()

    def _update_label(self, label: QLabel, value: int) -> None:
        """Update label text with a value."""
        label.setText(str(value))

    def _show_success_dialog(self) -> None:
        """Show custom success dialog with Ok and Exit buttons."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Success")
        dialog.setGeometry(100, 100, 350, 150)
        
        layout = QVBoxLayout()
        
        label = QLabel("Settings applied to keyboard.")
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Ok")
        ok_btn.clicked.connect(lambda: (dialog.close(), self.status_label.setText("Ready")))
        button_layout.addWidget(ok_btn)
        
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def update_colors_display(self) -> None:
        """Update the colors display frame."""
        # Clear existing widgets
        while self.colors_layout.count():
            child = self.colors_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.colors:
            label = QLabel("No colors selected.")
            self.colors_layout.addWidget(label)
            return

        for idx, color in enumerate(self.colors):
            color_box = ColorBox(color, idx)
            color_box.remove_requested.connect(self.remove_color)
            color_box.selected.connect(self.on_color_selected)
            if self.selected_color_index == idx:
                color_box.set_selected(True)
            self.colors_layout.addWidget(color_box)
        
        self.colors_layout.addStretch()

    def add_color(self) -> None:
        """Add a color using the color chooser dialog."""
        color = QColorDialog.getColor(parent=self, title="Choose a color")
        if color.isValid():
            hex_color = color.name().upper()
            self.colors.append(hex_color)
            self.update_colors_display()

    def clear_colors(self) -> None:
        """Clear all colors after user confirmation."""
        reply = QMessageBox.question(
            self, "Clear colors",
            "Remove all colors?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
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
            self.selected_color_index = None
            self.update_colors_display()

    def on_color_selected(self, index: int) -> None:
        """Handle color selection."""
        if self.selected_color_index == index:
            self.selected_color_index = None
        else:
            self.selected_color_index = index
        self.update_colors_display()

    def move_color_left(self) -> None:
        """Move selected color one position to the left."""
        if self.selected_color_index is None or self.selected_color_index == 0:
            return
        
        # Swap with left neighbor
        idx = self.selected_color_index
        self.colors[idx], self.colors[idx - 1] = self.colors[idx - 1], self.colors[idx]
        self.selected_color_index = idx - 1
        self.update_colors_display()

    def move_color_right(self) -> None:
        """Move selected color one position to the right."""
        if self.selected_color_index is None or self.selected_color_index >= len(self.colors) - 1:
            return
        
        # Swap with right neighbor
        idx = self.selected_color_index
        self.colors[idx], self.colors[idx + 1] = self.colors[idx + 1], self.colors[idx]
        self.selected_color_index = idx + 1
        self.update_colors_display()

    def apply_settings(self) -> None:
        """Apply the current settings to the keyboard."""
        if not self.colors:
            QMessageBox.warning(self, "No colors", "Please add at least one color.")
            return

        colors_str = ",".join(self.colors)
        pattern = self.pattern_combo.currentText()
        speed = self.speed_slider.value()
        intensity = self.intensity_slider.value()

        cmd = [
            "keyboard_light",
            "-c", colors_str,
            "-p", pattern,
            "-s", str(speed),
            "-i", str(intensity),
        ]

        self.status_label.setText("Applying settings…")
        self.apply_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except FileNotFoundError:
            self.status_label.setText("Error: keyboard_light not found")
            QMessageBox.critical(
                self,
                "Command not found",
                "The 'keyboard_light' command was not found.\n"
                "Is the rgb-keyboard package installed in this environment?"
            )
        except subprocess.TimeoutExpired:
            self.status_label.setText("Error: command timeout")
            QMessageBox.critical(self, "Timeout", "Command took too long.")
        else:
            if result.returncode == 0:
                self.status_label.setText("Settings applied successfully.")
                self._show_success_dialog()
            else:
                err = result.stderr or result.stdout or "<no output>"
                self.status_label.setText("Error applying settings.")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to apply settings.\n\nCommand:\n{' '.join(cmd)}\n\nOutput:\n{err}",
                )
        finally:
            self.apply_btn.setEnabled(True)


def main() -> None:
    """Main entry point for the GUI."""
    app = QApplication(sys.argv)
    window = RGBKeyboardGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
