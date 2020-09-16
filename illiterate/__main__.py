# This module simply allows calling illiterate as 
# `python -m illiterate`.
# We just import the CLI app and setup the right name so
# that documentation is correct.

from .cli import app


if __name__ == "__main__":
    app(prog_name="python -m illiterate")
