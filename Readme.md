# Illiterate

> Unobstrusive literate programming experience for Python pragmatists

`illiterate` is a Python module that helps you apply _some_ of the literate programming paradigm
without requirying a meta-programming language (like `noweb`) or any preprocessing step to actually
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
This is great if everyone that will ever write code in your project is willing to indulge into literate programming.
Sadly, I have found that more often that not, this is not the case.
Hence, even though it is awesome, literate programming has some major practical drawbacks that, at this moment,
make it impossible for many people to apply it widely, including:

- Poor support from editors and lack of tooling, which is not just a matter of syntax highlighting. The very feature that makes
literate programming extra powerful, i.e., macros, makes it almost impossible for any semantic analysis to work, so forget
about intellisense, smart completion or interactive linting.
- A hard entry curve, since unfortunately people in the 21st century still learns to code the "old" way, that is,
code-first. Introducing someone into literate programming is hard because it takes some time to grok it and understand the benefits.
- It's hard to incrementally switch to it. If you already have a somewhat large program writen in the "traditional" way,
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
Specifically, you should not need to use new tools, editor extensions, or preprocessors. Code writen using the 
illiterate style looks exactly like regular code, but hopefully, a bit better.

Everything stems from these key principles:

- Documentation for a codebase should be writen as prose, and it should be enjoyable to read it top to bottom. 
It should not be simply a list of modules and methods with few-line descriptions; rather, it should be a cohesive
piece of literature that clearly explains the authors intents for any small details and how everything fits into the bigger
picture.
- Documentation should be as close as possible to real code, ideally right next to it, instead of in external 
markdown files that can easily get out of sync. Furthermore, there should be some automated way
to ensure that documentation is up to date, ideally with embedded unit tests that fail if documentation is wrong.
- Documentation should be written both for users of your code and future developers, and it should be
easy for anyone to dive as deep as they want. This means that users only interested in calling your high-level
API can easily understand how to use it, while collaborators or anyone wanting to understand how everything works
should also be able to follow all the details.

