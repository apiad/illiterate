# Illiterate

[<img alt="PyPI" src="https://img.shields.io/pypi/v/illiterate">](https://pypi.org/project/illiterate)
[<img alt="PyPI - License" src="https://img.shields.io/pypi/l/illiterate">](https://github.com/apiad/illiterate)
[<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/illiterate">](https://pypi.org/project/illiterate)
[<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/apiad/illiterate?style=social">](https://github.com/apiad/illiterate/stargazers)
[<img alt="GitHub forks" src="https://img.shields.io/github/forks/apiad/illiterate?style=social">](https://github.com/apiad/illiterate/network/members)

> Unobtrusive literate programming experience for Python pragmatists

`illiterate` is a Python module that helps you apply _some_ of the literate programming paradigm
without requiring a meta-programming language (like `noweb`) or any preprocessing step to actually
get your code up and running.

It works kind of opposite to how literate programming suggests, in the sense that you write code-first
and embed documentation into your code. I know, purist literate programmers will hate this but hey, it's a compromise.

## What is all this (il)literate programming about?

If you've never heard about literate programming before, then I suggest you to read at least the 
[Wikipedia entry](https://en.wikipedia.org/wiki/Literate_programming)
and then we can continue discussing. 
It is a fascinating topic, and there are [many resources](http://www.literateprogramming.com) out there.

Back already? Ok, so here is illiterate's take on this matter.

Ideally, for literate programming to work, you would code in a meta-language mixing prose, code, and macros.
This is great if everyone that will ever write code in your project is willing to indulge in literate programming.
Sadly, I have found that more often that not, this is not the case.
Hence, even though it is awesome, literate programming has some major practical drawbacks that, at this moment,
make it impossible for many people to apply it widely, including:

- Poor support from editors and lack of tooling, which is not just a matter of syntax highlighting. The very feature that makes
literate programming extra powerful, i.e., macros, makes it almost impossible for any semantic analysis to work, so forget
about intellisense, smart completion, or interactive linting.
- A hard entry curve, since unfortunately people in the 21st century still learns to code the "old" way, that is,
code-first. Introducing someone into literate programming is hard because it takes some time to grok it and understand the benefits.
- It's hard to incrementally switch to it. If you already have a somewhat large program written in the "traditional" way,
it's very hard to port it to the literate programming paradigm incrementally. 

All these reasons make it, at least for me, almost impossible to apply pure literate programming in anything more
than toy projects. However, I do love the paradigm, and I do think it makes you a better programmer, and makes your code
easier to maintain and understand. I wanted a way to introduce as much of literate programming as possible into the
traditional programming paradigms, but still being able to use the same tools, introducing literate programming
idiosyncrasies incrementally into existing
codebases but "flying under the radar" as much as possible, so detractors don't complain.

Hence, `illiterate` was born. It is called that way in part because is kind of a twist on the literate programming
paradigm, and also because it is supposed to help us illiterates to write more literate code.

## So what does illiterate proposes?

Glad you asked. The idea is to encourage a more literate codebase while introducing as few changes as possible.
Specifically, you should not need to use new tools, editor extensions, or preprocessors. Code written using the 
illiterate style looks exactly like regular code, but hopefully, a bit better.

Everything stems from these key principles:

- Documentation for a codebase should be written as prose, and it should be enjoyable to read it top to bottom. 
It should not be simply a list of modules and methods with few-line descriptions; rather, it should be a cohesive
piece of literature that clearly explains the authors' intents for any small details and how everything fits into the bigger
picture.
- Documentation should be as close as possible to real code, ideally right next to it, instead of in external 
markdown files that can easily get out of sync. Furthermore, there should be some automated way
to ensure that documentation is up to date, ideally with embedded unit tests that fail if documentation is wrong.
- Documentation should be written both for users of your code and future developers, and it should be
easy for anyone to dive as deep as they want. This means that users only interested in calling your high-level
API can easily understand how to use it, while collaborators or anyone wanting to understand how everything works
should also be able to follow all the details.

To achieve these objectives, illiterate proposes really only one major paradigm shift:

> **Your code is the documentation.**

That's it. You will simply write all the documentation for your code right inside your code, as comments and as Python docstrings,
according that what is more convenient for each case. But keep this in mind, *all your code will be published as-is for documentation purposes*.

Now you are forced to think about your code in terms of: "well, this will be read by users at some point, so I better make it as publishable as possible".
This means that you can no longer simply put some throw-away code in some forsaken `_tmp.py` file. That file will appear in the documentation, so it better be publishable.

## How this works?

The only thing that illiterate does is taking your Python repository and turn it into Markdown files.
It will parse all your code, and output nicely formatted Markdown versions of each `.py` file. It is up to you that what is writen in those `.py` files is something worth publishing as documentation.

To use it, you simply run:

    python -m illiterate [src] [output]

Where `[src]` is the folder that is the root of your project's code (i.e., the top-level folder with an `__init__.py` inside), and `[output]` is where you want the markdown files. You can add `--copy from:to` to copy verbatim some files into the output folder.
I do this for copying the `Readme.md` into an `index.md` which becomes the homepage.

For example, in this project, standing on the root folder (where this Readme is located), you would run the following (🤓 yeah, it is kind if Inception-ish):

    python -m illiterate illiterate docs --copy Readme.md:index.md

This will take all the code in `illiterate`, convert it to Markdown, and drop it inside the `docs` folder.
It will also copy the `Readme.md` file into `docs/index.md`.

What you do with those Markdowns is up to you. In this project, I use [mkdocs](https://mkdocs.org) for documentation. 
If you have `mkdocs`, then make sure to have your `mkdocs.yml` correctly configured so that it renders those freshly created markdowns. 
You can also see the `mkdocs.yml` in this repository to get an idea of how that configuration looks, but beware, I'm using some custom
themes and other stuff you might or might not want.

You can mix illiterate with regular markdown simply by hand-crafting all the documentation you want in pure Markdown and then conveniently designing your `mkdocs.yml`.

## Next steps

This project is quite small, but it is a self-fulfilling prophecy. The remaining [documentation](https://apiad.net/illiterate/illiterate.__init__) has been written with `illiterate`. Just keep reading and you'll see for yourself what does this mean.
