"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with three commands, that manage the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


from click.termui import style
import typer
import yaml
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

# ## The build command

# Here is the implementation of the build command
# is called when `python -m illiterate build` is used.
# This command parse and creates the documentation based on its input parameters.


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

# ## The `preset build` subcommand

# The  `preset build` subcommand
# is called when `python -m illiterate preset build` is used.
# This command parse and creates the documentation based on a preconfigured file


# A good example of what a configuration file might look like
# is the one used for this project.
# The configuration files are called illiterate.yml
# imitating the mkdocs configuration files and have the following shape


# ```yml
# inline: true # true if we want to process the comments within code blocks
# output: docs # The address of the output folder
# sources: # List of files to be processed or copied
#   illiterate.__init__: illiterate/__init__.py # An input is made up of the address of the output file without suffix and using periods as a separator and the address of the input file.
#   illiterate.__main__: illiterate/__main__.py
#   illiterate.cli: illiterate/cli.py
#   illiterate.core: illiterate/core.py
#   index: Readme.md
# ```

# This is the implementation
@preset.command(name="build")
def preset_build(file: Path = None, debug: bool = None):

    level = logging.DEBUG if debug else logging.WARNING

    logging.basicConfig(level=level, handlers=[RichHandler(rich_tracebacks=True)])

    yml_file = Path("illiterate.yml") if file is None else file

    if yml_file.exists():
        try:
            # This function does all the heavy-lifting...
            process_yml(yml_file)
        except:
            # And if it fails we print the appropriate message
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


# ## The `preset build`

# The 'preset init' subcommand
# is called when `python -m illiterate preset build` is used.
# This command creates a preset based on its input parameters.
# Its input parameters and those of the `python -m illiterate build` command match.

# This is the implementation
@preset.command(name="init")
def preset_init(
    src_folder: Path,
    output_folder: Path,
    copy: List[str] = None,
    inline: bool = False,
):
    # We create a configuration prototype inside a dictionary
    yml_data = {"output": str(output_folder), "inline": inline, "sources": {}}

    # Then we add the files from the input folder to the configuration
    for path in src_folder.rglob("*.py"):
        yml_data["sources"][str(path.with_name(path.stem)).replace("/", ".")] = str(
            path
        )

    # And the files to be copied as well
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
