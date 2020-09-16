"""This module contains the classes that represent the types of content inside a Python file
and perform the necessary conversions.
"""

import abc
from typing import Iterable, TextIO


class Block(abc.ABC):
    def __init__(self, content):
        while content:
            if not content[0].strip():
                content.pop(0)
            else:
                break

        while content:
            if not content[-1].strip():
                content.pop()
            else:
                break

        self.content = content

    @abc.abstractmethod
    def print(self, fp: TextIO):
        pass


class Markdown(Block):
    def print(self, fp: TextIO):
        for line in self.content:
            if line.startswith("# "):
                fp.write(line[2:])
            else:
                fp.write("\n")

        fp.write("\n")


class Python(Block):
    def print(self, fp: TextIO):
        if not self.content:
            return

        fp.write("```python\n")

        for line in self.content:
            fp.write(line)

        fp.write("```\n\n")


from typing import List


class Content:
    def __init__(self, *content: Iterable[Block]) -> None:
        self.content = content

    def dump(self, fp: TextIO):
        for block in self.content:
            block.print(fp)


class Parser:
    def __init__(self, input_src: TextIO) -> None:
        self.input_src = input_src

    def parse(self):
        content = []
        current = []
        state = "markdown"

        for line in self.input_src:
            if line.startswith("#"):
                if state == "python":
                    if current:
                        content.append(Python(current))
                        current = []
                    state = "markdown"
                current.append(line)
            else:
                if state == "markdown":
                    if current:
                        content.append(Markdown(current))
                        current = []
                    state = "python"
                current.append(line)

        if current:
            if state == "markdown":
                content.append(Markdown(current))
            else:
                content.append(Python(current))

        return Content(*content)
