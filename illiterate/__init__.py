"""Illiterate is a Python library for crafting self-documenting code, 
loosely following the literate programming paradigm.

The library itself is coded following illiterate "best practices", 
so by reading this, either in source code or in the rendered documentation,
you should be able to understand what we want to achieve.
If you don't, then we have done a pretty bad job.
"""

# The basic idea is that code should be self-explanatory, but not in
# the sense that it doesn't require comments. Rather, it should be
# self-explanatory because comments and code together flow naturally and
# interweave with each other in a manner that is easy to read by people
# beyond those who wrote it.

# This means that comments should be writen in prose, with correct grammar,
# and not in short phrases next to some instructions without any context.
# It should be pleasing to read.

# This also means that you are forced to organize your source code in a way
# that allows the narrative to flow. For example, it will force you to put
# the most important definitions (clases and methods) at the top, and leave
# implementation details for the end.

# I know some will complain, and say "but why am I forced to organize my code in a specific way!?".
# Well, there is no real restriction to organizing code in Python other than for scoping rules,
# i.e., that any symbol you use is already defined before. Other than that, you either don't care
# how the code is organized, in which case it is better to have some guidelines, or you do
# care how your code is organized. In this second case, if the way your code is organized is not already
# optimized for readibility, then my opinion is that you're organizing it wrong. Plain and simple.

# With illiterate, you always organize your code in the way that best fits the explanation.
# And when you are required to import something or define something at some point, then you better
# have a good excuse for including it there. If you're doing it right, you should have already
# explained your whys and you should be fairly justified at that point.

# To get in the right mindset for this paradigm shift, think of your source in the following terms.
# You are a narrator talking to yourself (the future you), trying to explain how this code works.
# Instead of the code being the important thing, is the narrative what matters.
# The code just happens to be inserted into some points of the narrative to actually do what the
# narrative says.

# There are many ways to explain an idea, but one of the most succesful from my point of view is
# by trying to answer the following questions, in order: why, what, and how.
# Always start with the motivation, **why** is code necessary, to solve which problem?
# Then move to the proposed solution, **what** are you actually gonna do, which are the components of the solution?
# And then add the implementation details: **how** is each subtask implemented?

# There are many advantages to this idea. Two of the most important ones are:

# - Anyone reading this code in the future should be able to understand it, specially because
#   now not only the implementation details are there, but also all the motivation behind choosing some
#   approach rather than another.

# - It will make much easier for yourself to actually develop the project, I promise, because it will
#   force you to think about the problem you want to solve before thinking about the solution. And it will
#   force you to write down explicitely what is that problem, what is the expected solution, which are the main
#   assumptions.

# ## Writing as an illiterate

# Now let's talk about using illiterate. As you have seen so far, these are just regular comments in the code.
# That's it, nothing has changed. You just need the right mindset.

# Each comment will be parsed and ultimately rendered as Markdown, so you are free to include any Markdown
# styling that you want, including lists, **bold**, `code`, and even sections (using `##`).
# At the begining of this file you can see the docstrings. They are rendered exactly the same in the final
# documentation as regular Markdown, but since they also serve as the internal documentation of this module
# for IntelliSense purposes, you have to decide how much narrative do you want to be part of the "core" documentation.

# And then you just add the code as always. Illiterate Python files are just regular Python files,
# so everything should work the same as before.

# ## High-level implementation

# Illiterate is a very simple program. All it does is parse Python files, which are converted to some
# intermediate representation, and then writes them back in Markdown. However, this "parsing" is very simple,
# because we don't really need to understand the Python code. We just need to separate a file into blocks
# of Markdown and blocks of Python, and then write that back.

# To organize this process, we will have classes that represent the different types of content,
# and then a very simple parser that scans a file top-to-bottom and builds the corresponding block.
# At this point, however, we only care about the high-level architecture.

# Starting at root folder, we will process all the `.py` files in sequence, producing for each one
# a markdown file that will be saved to the output folder.

# ### The outer loop

# In the output, filenames will match the folder structure that we find, only changing the
# `.py` with an `.md` extension and every "/" with a dot.
# For example `src/moduleA/moduleB/file.py` will become `output/moduleA.moduleB.file.md`.
# We will use `pathlib.Path` for that purpose.

from pathlib import Path

# Next comes our top level function that processes each file.
# Notice how we also have docstrings in each function, as usual.
# Docstrings are for guiding developers when inspecting our code via IntelliSense and such.
# Hence, they should be fairly self-contained.

# You will also notice that methods have comments, as usual. However, inline comments do not
# lend themselves very well to a coherent and flowing narrative. They are better suited to
# explain very concise ideas.
# For this reason, illiterate won't render those comments as Markdown. They are an integral part
# of your code, and will be rendered as code.

# Hence, you will be forced to refactor your methods so that they are as small as possible.
# That way, they will have as little comments as possible, ideally none, because the surrounding
# comments are already enough to make everything as clear as it needs to be.
# If a method, including comments, is longer than one screen of text, consider refactoring it.

# One more thing, before I forget, is that we want [fancy progress bars](https://tqdm.github.io/).

import tqdm

# And finally, as promised, here comes the function.


def process(src_folder: Path, output_folder: Path):
    """Processes all the Python source files in `src_folder`, recursively,
    and writes the corresponding Markdown files to `output_folder`.
    """

    # Each input file can be found recursively with `.rglob`,
    # which works pretty much like `ls -lR`.
    for input_path in tqdm.tqdm(src_folder.rglob("*.py"), unit="file"):
        # The output path matches the input path but with the right extension,
        # using "." as separator, and rooted at `output_path`
        output_path = output_folder / ".".join(input_path.with_suffix(".md").parts)
        # And just process that file
        process_one(input_path, output_path)


# ### Processing each file

# Processing a single file is quite straightforward as well.
# We will be using a `Parser` class that does all the heavy-lifting.
# We fed the parser with the input and it will return an object (of type `Content`)
# that knows how to write itself into a file in Markdown.

from .core import Parser


def process_one(input_path: Path, output_path: Path):
    # We need to create this folder hierarchy if it doesn't exists
    output_path.parent.mkdir(exist_ok=True)

    # First we parse
    with input_path.open() as fp:
        content = Parser(fp).parse()

    # And then we dump the parsed content
    with output_path.open("w") as fp:
        content.dump(fp)


# And that's it. As you can see, being forced to describe our process in this way also
# forces us to write pretty small methods, and to organize our code in the way that is
# easier to explain. This might seem daunting at first, but believe me (and thousands of
# computer scientists and software engineers that have been saying this for decades),
# every effort that you take now to make your code more readable will be paid in the future
# when you have to come back.

# ## Where to go from here?

# As you have seen, illiterate makes no assumption about the order in which your files will be read.
# If you want to force a particular order, that goes into your `mkdocs.yml`
# (or wherever your documentation engine says). However, since this is Markdown, you can include
# links anywhere you want, since only you know how your documentation engine generates links.

# As an example, you can read more about the [`Parser` class](./illiterate.core.md#the-parser),
# or you can directy see [how the CLI works](./illiterate.cli.md).
