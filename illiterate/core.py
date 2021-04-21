"""This module contains the classes that represent the types of content 
inside a Python file and perform the necessary conversions.
"""

import logging

logger = logging.getLogger("illiterate")

# To represent the different types of content in a single Python file,
# we will use three classes.
# These classes will represent, respectively, a block of [Markdown](ref:illiterate.core:Markdown) text,
# a block of [Python](ref:illiterate.core:Python) code, and a top-level [docstring](ref:illiterate.core:Docstring).

# The only difference between these types of content that we care of
# is how they are printed as Markdown.
# Other than that, all types of content are simply a list of text lines.

# There is however one common functionality for all of them.
# Depending on how the file is structured, we might end up with
# spurious empty lines at the begining or end of any block.
# This might not be a big issue for Markdown, in some cases, but it is
# definitely a problem for Python code.
# Hence, we will remove all the empty lines at the begining and the end
# of each block.

# The common functionality will go into an abstract class.

import abc
import re
from typing import Iterable, TextIO, List

# ## Content Blocks

# The only relevant functionality in this class is cleaning up
# the list of content.
# We also define an abstract method `print` which inheritors
# will override to determine how different types of content are printed.


class Block(abc.ABC):
    def __init__(self, content: List[str], module_name: str):
        self.module_name = module_name

        while content:
            if not content[0].strip():  # testing for emptyness
                content.pop(0)  # from the top down
            else:
                break

        while content:
            if not content[-1].strip():  # testing for emptyness
                content.pop()  # from the bottom up
            else:
                break

        self.content = content

    @abc.abstractmethod
    def print(self, fp: TextIO):
        pass


# Markdown blocks are either formed by lines starting with `#`
# (i.e., Python comments) or blank lines.
# For every line that starts with `#_`, we simply remove the first two
# characters, i.e., the sharp symbol and the starting space.
# For blank lines, we just output them as-is.

# The only slightly complex functionality in Markdown blocks is formatting
# references. We want to write something `ref:illiterate.core:Markdown`
# in our documentation, and have it translated automatically to
# `../illiterate.core#ref:Markdown`.


class Markdown(Block):
    def print(self, fp: TextIO):
        for line in self.content:
            line = self.fix_links(line.strip())

            if line.startswith("# "):
                fp.write(line[2:] + "\n")
            else:
                fp.write("\n")

        fp.write("\n")

    # Fixing the links is very easy if we use a regular expression.
    # Notice that we let the last part (the class or method name) as optional.
    # This means we can link to modules directly with `ref:module`.

    links_re = re.compile(r"\(ref:(?P<module>[a-zA-Z_\.]+)(:(?P<name>[a-zA-Z_\.]+))?\)")

    def fix_links(self, line):
        return self.links_re.sub(r"(../\g<module>/#ref:\g<name>)", line)


# Python blocks are even easier, since we will print them as-is.
# There are two points to keep in mind.
# First is, we need to output a Markdown fenced code block
# before and after the actual code.
# Second, we are going to collect all class and method definitions that appear
# in this block and output some invisible HTML anchors.
# These anchors won't render in the Markdown or the table of content but you
# can use them to link to method.
# For example, see the [`Parser`](#class:Parser) class defined below.


class Python(Block):
    def print(self, fp: TextIO):
        if not self.content:
            return

        fp.write("\n".join(self.get_anchors()) + "\n\n")

        fp.write("```python\n")

        for line in self.content:
            fp.write(line)

        fp.write("```\n\n")

    # To get all valid anchors we'll make use of a simple regular expression.

    # !!! warning
    #     The current implementation only works with top-level definitions of classes and methods.
    #     To extend this to second-level definitions and beyond, we're gonna have to introduce some
    #     sort of stack to keep track of the outer definitions, because a class name can be defined
    #     in a different Python block than its inner methods.

    anchor_re = re.compile(r"(?P<type>(class|def))\s(?P<name>[a-zA-Z0-9_]+)")

    def get_anchors(self):
        anchors = []

        for line in self.content:
            match: re.Match = self.anchor_re.match(line)

            if match:
                anchors.append(f"<a name=\"ref:{match.group('name')}\"></a>")
                logger.debug("Found anchor: %r" % match)

        return anchors


# Another interesting type of content is module-level docstrings.
# Instead of outputting these as standard Python code, we'll use a block quote.


class Docstring(Block):
    def print(self, fp: TextIO):
        fp.write("!!! note\n")

        for line in self.content:
            line = line.strip()

            if line != '"""':
                fp.write(f"    {line}\n")


# Once we have our content types correctly implemented, we will
# define a container class that stores a sequence of possible `Block`s.
# This will make it easier later to dump a bunch of different blocks with
# a single instruction.


class Content:
    def __init__(self, *content: Iterable[Block]) -> None:
        self.content = content

    def dump(self, fp: TextIO):
        for block in self.content:
            block.print(fp)


# ## The Parser

# Finally, we have come to the core functionality of `illiterate`, the class
# that reads Python source code and produces the corresponding blocks.
# The parser is then a very simple automaton with three states.

# Since we don't really care about the structure of the code, this parser
# is very simple. Formally, we are dealing with a regular language, since
# we can determine what type of content we are dealing with based solely on the
# first character.


class Parser:
    def __init__(self, input_src: TextIO, inline: bool, module_name: str) -> None:
        self.input_src = input_src
        self.inline = inline
        self.module_name = module_name
        self.content = []
        self.state = State.Markdown

    # The automaton switches states according to the first character of the current line.
    # Intuitively, as long as we are seeing either a `#` or blank lines, we are
    # seeing Markdown. Once we see a line that doesn't begin with a `#`, that
    # must be code or docstring.

    # If `inline == True`, which is activated with `--inline` in the CLI, we will
    # parse any comments that appear on a line by itself, such as these ones, as
    # Markdown.
    # Otherwise, only comments that appear exactly at the beginning of the line
    # will be considered Markdown, and the rest will be parsed as code.

    # Doctrings always start with """. Once inside a docstring, until a line doesn't end
    # with """, we assume everything is part of the string.

    def parse(self):
        self.content = []
        current = []

        for line in self.input_src:
            if self.state == State.Docstring:
                if line.strip().startswith('"""'):
                    current = self.store(current)
                    self.state = State.Markdown

            elif self.state == State.Python:
                if line.startswith("#") or (
                    self.inline and line.strip().startswith("#")
                ):
                    current = self.store(current)
                    self.state = State.Markdown
                elif line.strip().startswith('"""'):
                    current = self.store(current)
                    self.state = State.Docstring

            elif self.state == State.Markdown:
                if line.strip().startswith('"""'):
                    current = self.store(current)
                    self.state = State.Docstring
                elif not (
                    line.startswith("#")
                    or (self.inline and line.strip().startswith("#"))
                ):
                    current = self.store(current)
                    self.state = State.Python

            current.append(line)

        self.store(current)

        return Content(*self.content)

    # This small utility function creates the actual `Block` instance.
    # We make return an empty list so that we can use it as shown before,
    # by calling it and restoring `current = []` in the same line.

    def store(self, current):
        if not current:
            return []

        if self.state == State.Markdown:
            self.content.append(Markdown(current, self.module_name))
        elif self.state == State.Python:
            self.content.append(Python(current, self.module_name))
        elif self.state == State.Docstring:
            self.content.append(Docstring(current, self.module_name))

        return []


# Finally, here are the states.

import enum


class State(enum.Enum):
    Markdown = 1
    Docstring = 2
    Python = 3


# And this is it 🖖.
