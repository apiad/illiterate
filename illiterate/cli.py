"""This module contains the illiterate CLI application.

The CLI application is basically a [Typer](https://typer.tiangolo.com) application
with three commands, that manage the whole process.
"""

# The illiterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


import typer
import yaml

# These two are for watching file changes.

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# And these are internal.

from illiterate import process
from illiterate.config import IlliterateConfig

# The main typer application.
app = typer.Typer()

# These are the types for our arguments, and `shutil` for copying files.

from pathlib import Path
from typing import List

from rich.progress import track

# ## A command helper

# Most of the commands will take either CLI args or a --config file.
# So we will define a decorator now to take care of that bookkeeping and
# obtain an instance of `IlliterateConfig`.


def illiterate_command(fn):
    def command(
        src: List[str] = typer.Option([]),
        inline: bool = False,
        linenums: bool = False,
        highlights: bool = False,
        title: bool = False,
        expanded: bool = False,
        config: Path = None,
    ):
        if config:
            with config.open() as fp:
                cfg = IlliterateConfig(**yaml.safe_load(fp))
        elif not src and Path("illiterate.yml").exists():
            with open("illiterate.yml") as fp:
                cfg = IlliterateConfig(**yaml.safe_load(fp))
        else:
            if not src:
                typer.echo("At least one source or a config file must be provided.")
                raise typer.Exit(1)

            cfg = IlliterateConfig.make(
                sources=src, inline=inline, linenums=linenums, highlights=highlights, title=title
            )

        if expanded:
            cfg = cfg.expanded()

        return fn(cfg)

    return command


# ## The build command

# Here is the implementation of the build command
# is called when `python -m illiterate build` is used.
# This command parse and creates the documentation based on its input parameters.


@app.command("build")
@illiterate_command
def build(config: IlliterateConfig):
    process_all(config)


# ## The config command


@app.command("config")
@illiterate_command
def config(config: IlliterateConfig):
    print(yaml.safe_dump(config.dict()))


class IlliterateHandler(FileSystemEventHandler):
    def __init__(
        self, input_path: Path, output_path: Path, cfg: IlliterateConfig
    ) -> None:
        super().__init__()
        self.cfg = cfg
        self.input_path = input_path
        self.output_path = output_path

    def on_modified(self, event: FileModifiedEvent):
        typer.echo(f"Recreating: {self.input_path} -> {self.output_path}")
        process(self.input_path, self.output_path, self.cfg)


@app.command("watch")
@illiterate_command
def watch(config: IlliterateConfig):
    process_all(config)
    observer = Observer()

    for input_path, output_path in config.files():
        observer.schedule(
            IlliterateHandler(input_path, output_path, config), input_path
        )

    observer.start()
    observer.join()


# ## Processing a config file


def process_all(cfg: IlliterateConfig):
    files = list(cfg.files())

    # This function does all the heavy-lifting...
    for input_path, output_path in track(files):
        process(input_path, output_path, cfg)
