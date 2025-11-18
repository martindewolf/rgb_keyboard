from setuptools import setup, find_packages
from codecs import open
from os import path
import os

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def find_all(folder):
    for (p, _, filenames) in os.walk(folder):
        for filename in filenames:
            yield os.path.join("..", p, filename)

setup(
    name="rgb-keyboard",
    version="1.1.0",
    description=(
        "Driver and interface to control keyboard RGB LED of "
        "ITE 8291 rev 0.02 (e.g. Avell laptops)"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martindewolf/rgb_keyboard",
    author="Eder Martins / Martin de Wolf",
    packages=find_packages(),
    package_data={"": list(find_all("rgb_keyboard"))},
    include_package_data=True,
    install_requires=[
        "hid",
        "elevate",
        "PyQt6",
    ],
    entry_points={
        "console_scripts": [
            "keyboard_light = rgb_keyboard.__main__:main",
            "keyboard_light_gui = rgb_keyboard.gui:main",
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/martindewolf/rgb_keyboard/issues",
        "Source": "https://github.com/martindewolf/rgb_keyboard",
    },
)
