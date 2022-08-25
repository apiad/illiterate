"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with three commands, that manage the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


from illiterate.config import IlliterateConfig
import typer
import yaml
from . import process

# The main typer application
app = typer.Typer()

# These are the types for our arguments, and `shutil` for copying files.

from pathlib import Path
from typing import List
import logging
from rich.logging import RichHandler
from rich.progress import track

# ## The build command

# Here is the implementation of the build command
# is called when `python -m illiterate build` is used.
# This command parse and creates the documentation based on its input parameters.


@app.command()
def build(
    sources: List[str] = None,
    debug: bool = False,
    inline: bool = False,
    *,
    config: Path = None
):
    level = logging.DEBUG if debug else logging.WARNING

    logging.basicConfig(level=level, handlers=[RichHandler(rich_tracebacks=True)])

    # This function does all the heavy-lifting...
    if config:
        with config.open() as fp:
            cfg = IlliterateConfig(**yaml.safe_load(fp))
    else:
        cfg = IlliterateConfig.make(inline=inline, sources=sources)

    # Finally, we just have to copy verbatim all necessary files.
    files = list(cfg.files())

    for input_path, output_path in track(files):
        process(input_path, output_path, cfg.inline)


@app.command()
def config(
    sources: List[str], inline: bool = False, *, expand:bool=False
):
    cfg = IlliterateConfig.make(inline=inline, sources=sources)

    if expand:
        cfg = cfg.expanded()

    print(yaml.safe_dump(cfg.dict()))
