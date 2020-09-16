"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with a single command, that launches the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with a single command.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.

import typer

# This is the main function that does all the heavy lifting.

from . import process

# We create a `typer` application.

app = typer.Typer()

# These are the types for our arguments, and `shutil` for copying files.

from pathlib import Path
from typing import List
import shutil

# And here is the command implementation.


@app.command()
def main(src_folder: Path, output_folder: Path, copy: List[str] = None):
    # Not much too see here ;)
    process(src_folder, output_folder)

    # Copy verbatim all necessary files
    if copy:
        for fname in copy:
            if ":" in fname:
                fin, fout = fname.split(":")
            else:
                fin, fout = fname, Path(fname).name

            shutil.copy(fin, output_folder / fout)
