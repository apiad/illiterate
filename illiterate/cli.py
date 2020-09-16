"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with a single command, that launches the whole process.
"""

# We need `pathlib` to resolve paths automatically
from pathlib import Path
from typing import List
import shutil

# And `typer` to actually create the CLI app.
import typer

# Finally, this is the main function that does all the heavy lifting.
from . import process

# We create a `typer` application.
app = typer.Typer()


# And here is the only command.

@app.command()
def main(src_folder: Path, output_folder: Path, copy: List[Path] = None):
    # Not much too see here ;)
    process(src_folder, output_folder)

    # Copy verbatim all necessary files
    if copy:
        for fname in copy:
            shutil.copy(fname, output_folder / fname.name)
 