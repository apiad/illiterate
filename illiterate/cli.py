"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with a single command, that launches the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with a single command.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.

from os import name
from click.termui import style
import typer
import yaml

# This is the main function that does all the heavy lifting.

from . import process, process_yml

# We create a ` typer` application representing a sub-command
preset = typer.Typer()
# and the main typer application
app = typer.Typer()

# then we configure them
app.add_typer(preset, name="preset")

# These are the types for our arguments, and `shutil` for copying files.

from pathlib import Path
from typing import List
import shutil
import logging
from rich.logging import RichHandler

# Here is the implementation of the main command called build.


@app.command()
def build(
    src_folder: Path,
    output_folder: Path,
    copy: List[str] = None,
    debug: bool = False,
    inline: bool = False,
):
    level = logging.DEBUG if debug else logging.WARNING

    logging.basicConfig(level=level, handlers=[RichHandler(rich_tracebacks=True)])

    # This function does all the heavy-lifting...
    process(src_folder, output_folder, inline)

    # Finally, we just have to copy verbatim all necessary files.
    if copy:
        for fname in copy:
            if ":" in fname:
                fin, fout = fname.split(":")
            else:
                fin, fout = fname, Path(fname).name

            shutil.copy(fin, output_folder / fout)


# then we have the implementation of the commands associated with the `preset` subcommand

# This is the implementation of the `preset build` command
@preset.command(name="build")
def preset_build(file: Path = None, debug: bool = None):

    level = logging.DEBUG if debug else logging.WARNING

    logging.basicConfig(level=level, handlers=[RichHandler(rich_tracebacks=True)])

    yml_file = Path("illiterate.yml") if file is None else file

    if yml_file.exists():
        try:
            process_yml(yml_file)
        except:
            typer.echo(
                typer.style(
                    "The configuration file is corrupt or misconfigured.",
                    fg=typer.colors.RED,
                ),
                err=True,
            )
    else:
        typer.echo(
            typer.style("Configuration file does not exist.", fg=typer.colors.RED),
            err=True,
        )


# And this is the implementation of the 'preset init' command
@preset.command(name='init')
def preset_init(
    src_folder: Path,
    output_folder: Path,
    copy: List[str] = None,
    inline: bool = False,
):
    yml_data = {"output": str(output_folder), "inline": inline, "sources": {}}

    for path in src_folder.rglob("*.py"):
        yml_data["sources"][str(path.with_name(path.stem)).replace("/", ".")] = str(
            path
        )

    if copy:
        for fname in copy:
            if ":" in fname:
                fin, fout = fname.split(":")
                fout = Path(fout).stem
            else:
                fin, fout = fname, Path(fname).stem

            yml_data["sources"][fout] = fin

    with open("illiterate.yml", "w") as f:
        yaml.safe_dump(yml_data, f)

    typer.echo(
        style(f"'illiterate.yml' file created successfully.", fg=typer.colors.GREEN)
    )
