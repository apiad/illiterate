# Illiterate

[<img alt="PyPI" src="https://img.shields.io/pypi/v/illiterate">](https://pypi.org/project/illiterate)
[<img alt="PyPI - License" src="https://img.shields.io/pypi/l/illiterate">](https://github.com/apiad/illiterate)
[<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/illiterate">](https://pypi.org/project/illiterate)
[<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/apiad/illiterate?style=social">](https://github.com/apiad/illiterate/stargazers)
[<img alt="GitHub forks" src="https://img.shields.io/github/forks/apiad/illiterate?style=social">](https://github.com/apiad/illiterate/network/members)

> Unobtrusive literate programming experience for pragmatists

`illiterate` is a Python module that helps you apply _some_ of the literate programming paradigm using markdown files.

If you've never heard about literate programming before, then I suggest you to read at least the
[Wikipedia entry](https://en.wikipedia.org/wiki/Literate_programming)
and then we can continue discussing.
It is a fascinating topic, and there are [many resources](http://www.literateprogramming.com) out there.

In short, literate programming means your code is embed in its documentation: both are one and the same. You write code as if you were writing a book with some code snippets intertwined. Then, a preprocessor takes out all the code snippets and "weaves" the actual program.

This allows you, the author, to _write the code in the best way for a human to understand it_, instead of in the way the computer needs. The preprocessor (the _weaver_) is responsible for reordering and interpolating all chunks in the right way so they make sense to a computer.

The best way to see this in action is to use it, so the rest of this document will show you how `illiterate` is built using the literate programming. This is also, incidentally, the official source code for `illiterate`, such that running `illiterate` in this Readme file will reproduce the exact source code of illiterate.

## Literate programming in action

The first thing literate programming in action.

```python
#: source=example.py

print("Hello World")

<<< rest-of-program >>>
```

Here is a test

```python
#: id=rest-of-program

print("Another part")
```
