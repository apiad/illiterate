"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with three commands, that manage the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


import time
from illiterate.config import IlliterateConfig
import typer
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
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

    if config:
        with config.open() as fp:
            cfg = IlliterateConfig(**yaml.safe_load(fp))
    else:
        cfg = IlliterateConfig.make(inline=inline, sources=sources)

    process_all(cfg)


@app.command()
def config(
    sources: List[str], inline: bool = False, *, expand:bool=False
):
    cfg = IlliterateConfig.make(inline=inline, sources=sources)

    if expand:
        cfg = cfg.expanded()

    print(yaml.safe_dump(cfg.dict()))


class IlliterateHandler(FileSystemEventHandler):
    def __init__(self, input_path:Path, output_path:Path, cfg:IlliterateConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.input_path = input_path
        self.output_path = output_path

    def on_modified(self, event:FileModifiedEvent):
        typer.echo(f"Recreating: {self.input_path} -> {self.output_path}")
        process(self.input_path, self.output_path, self.cfg.inline)


@app.command()
def watch(sources: List[str]=None, inline: bool = False, *, config:Path=None):
    if config:
        with config.open() as fp:
            cfg = IlliterateConfig(**yaml.safe_load(fp))
    else:
        cfg = IlliterateConfig.make(inline=inline, sources=sources)

    process_all(cfg)
    observer = Observer()

    for input_path, output_path in cfg.files():
        observer.schedule(IlliterateHandler(input_path, output_path, cfg), input_path)

    observer.start()
    observer.join()


def process_all(cfg: IlliterateConfig):
    files = list(cfg.files())

    # This function does all the heavy-lifting...
    for input_path, output_path in track(files):
        process(input_path, output_path, cfg.inline)