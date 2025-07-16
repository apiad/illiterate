# illiterate

A fast, zero-config, programmer-first literate programming tool. illiterate exports source code from Markdown files, allowing you to keep your code and documentation in one place, perfectly in sync. It's written in Rust, distributed as a single static binary, and designed to be simple, powerful, and language-agnostic.

`illiterate` is bootstrapped. The best way to understand how to use it, is to read the [annotated source code](docs/illiterate.md) to learn how it works.

## Philosophy

* **Markdown as the Source of Truth:** Your documentation isn't just *about* the code; it *is* the code.
* **Zero-Config by Default:** No illiterate.toml or other config files needed. Everything is controlled from the command line or within the Markdown itself.
* **Programmer-First:** The primary goal is to generate clean, compilable source code. Beautiful documentation is a happy side effect.
* **Language Agnostic:** illiterate works with any programming language because it simply treats code blocks as text.

## Installation

`illiterate` is distributed as a single static binary for Linux (and Windows Subsystem for Linux).

You can install it by downloading the latest pre-compiled binary from the [GitHub Releases page](https://github.com/apiad/illiterate/releases/latest) and placing it in a directory on your PATH.

The following command will install the latest version directly into `/usr/local/bin`:

```bash
curl https://raw.githubusercontent.com/apiad/illiterate/refs/heads/main/install.sh | sh
```

That's it! Run `illiterate --help` to get started.

## Quick Start

Create a Markdown file named `my_app.md`:

    # My Awesome Application

    This is the main entry point for our program.

    ```rust {export=src/main.rs}
    fn main() {
        println!("Hello, Literate World!");
        <<add_a_goodbye_message>>
    }
    ```

    And here's a reusable code fragment that we'll inject into `main`.

    ```rust {name=add_a_goodbye_message}
    println!("Goodbye!");
    ```

Run `illiterate` to export the file:

```bash
illiterate my_app.md
```

A new file, `src/main.rs`, has been created with the following content:

```rust
fn main() {
    println!("Hello, Literate World!");
    println!("Goodbye!");
}
```

## Core Concepts

`illiterate` works by parsing special attributes inside your fenced code blocks.

### 1. Export Blocks ({export=...})

A code block marked with `{export=path/to/file.ext}` will have its contents extracted and appended to the specified file. All blocks targeting the same file are concatenated in the order they appear.

    ```python {export=app/main.py}
    import utils
    ```

### 2. Named Fragments & Includes ({name=...} and <<...>>)

A code block can be given a name with `{name=my_fragment}`. This block is not exported directly but can be included elsewhere using the `<<my_fragment>>` syntax. This allows you to explain code in logical chunks, out of order, and assemble it correctly later.

    ```rust {name=setup_database}
    // Logic to connect to the database...
    ```

    ```rust {export=src/main.rs}
    fn main() {
        // Setup the database first
        <<setup_database>>
    }
    ```

### 3. "Magic" Headless Exporting ({export})

For simple cases where one Markdown file corresponds to one source file, you can use a headless `{export}` attribute. illiterate will automatically generate the filename based on the Markdown file's name and the code block's language.

Given a file named my_module.md:

    ```rust {export}
    pub fn public_function() {
        // ...
    }
    ```

Running illiterate my_module.md will create the file my_module.rs.

## Command-Line Usage

illiterate [OPTIONS] [FILES...]

* **[FILES...]**: One or more Markdown files to process.
* **--dir <DIRECTORY>**: Sets the root output directory for all exported files. Defaults to the current directory.
* **--test**: Tests the output against generated files, without generating anything. Exists with zero if the generated files would not change. Useful for CI/CD.

## Changelog

### v0.3.1

- Minor improvements and bug fixes.

### v0.3.0

- Add flag `--test` to test the output against generated files.

### v0.2.0

- First version with full support for named references and headless exporting.

### v0.1.0

- Basic markdown parsing and extraction of simple blocks.

## Why not...?

There are many features you could conceivably expect from a literate programming tool that I purposefully avoided in favor of simplicity. Some of them are listed below with possible alternatives.

Most of these are achievable with a proper build system, e.g., using `makefile` or any other build utility.

- **Conditional inclusions**: If you want to include some code chunks based on some condition (like, optional features), you can always achieve it by separating them into different source (markdown) files, and then conditionally including them in your call to `illiterate`.
- **Replacing instead of appending**: If you want that some named chunks are treated as a replacement instead of an addition to the same named chunk, you can instead refactor your source such that source A or source B implements one version and source B another, and then use conditional compilation (see above) to decide which to include.
- **Backpatching literate sources**: In literate programming, it can be tempting to make small fixes in the tangled code that you would later want to incorporate in the literate source. However, this creates more headaches than it solves, including keeping track of where each piece of tangled code came from. Combining recursive expansion and implicit indentation of code chunks, with the language-agnostic nature of `illiterate`, it is almost impossible to do this robustly because we would need to know how to annotate (e.g., how to put comments) in any possible language to achieve this. Instead, I encourage you to fully embrace literate programming and treat tangled source the same way you treat compiled bytecode.

## Contribution

At the moment, I consider `illiterate` feature-full and don't plan on adding anything other than to improve performance or refine some corner cases I might have missed.

That being said, there are some features that I do believe would make the whole experience of working with literate sources much better, and I would happily accept PRs in this direction, including but not limited to:

- **Linting literate sources**: If you have a language with type checking or any other static checks, it would be awesome to be able to see those linting errors in the literate source. However, this is extremely hard to achieve with `illiterate` for the same reasoning we don't want backpatching (see above), and literate programming coupled with robust testing already pretty much solves the need for very complicated static analysis.  However, I do think it's doable by creating intermediate mapping files that explain which line of tangled source comes from which line of literate source, though I'm unconvinced whether the added complexity justifies the feature.
- **Support for editor X**: In the same veing, if you want to add editor support for literate sources (e.g., cross-referencing and navigation between named chunks), I'm happy to accept PRs that include editor-specific config files or even short editor extensions. These would not become part of the `illiterate` program itself, but rather would be additional tools we could add or link to in the main `illiterate` repository.

I will also happily accept PRs that improve `illiterate` in the following ways:

- Improving performance.
- Improving the literate source explanations.
- Fixes and/or tests for existing bugs and corner cases.
- Github workflows to compile for other platforms.

If you want to fork `illiterate` and modify it for your own use cases, you're absolutely welcome to. `illiterate` is fully open source and will forever be free as in free beer and free speech.

### Building from Source

This project is self-hosting! The source code for illiterate lives in illiterate.md and is exported to the src/ directory, which is checked into version control.

The workflow for contributors is simple:

1. **Clone the repository:**

```bash
git clone https://github.com/apiad/illiterate.git
cd illiterate
```

2. **Build the initial version:** The src/ directory contains pre-exported source code, so you can build it immediately.

```bash
cargo build
```

This creates a binary at `target/debug/illiterate`.

3. **Make your changes:** Edit the "source of truth" file, `illiterate.md`.

4. **Re-export the source code:** Use the binary you just built to update the `src/` directory with your changes. This will run tests as well.

```bash
make self
```

5. **Rinse and repeat** until done. Then push and send a PR.

## License

`illiterate` is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
