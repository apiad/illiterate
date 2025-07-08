# illiterate

A fast, zero-config, programmer-first literate programming tool. illiterate exports source code from Markdown files, allowing you to keep your code and documentation in one place, perfectly in sync. It's written in Rust, distributed as a single static binary, and designed to be simple, powerful, and language-agnostic.

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

illiterate works by parsing special attributes inside your fenced code blocks.

#### 1. Export Blocks ({export=...})

A code block marked with {export=path/to/file.ext} will have its contents extracted and appended to the specified file. All blocks targeting the same file are concatenated in the order they appear.

    ```python {export=app/main.py}
    import utils
    ```

#### 2. Named Fragments & Includes ({name=...} and <<...>>)

A code block can be given a name with {name=my_fragment}. This block is not exported directly but can be included elsewhere using the <<my_fragment>> syntax. This allows you to explain code in logical chunks, out of order, and assemble it correctly later.

    ```rust {name=setup_database}
    // Logic to connect to the database...
    ```

    ```rust {export=src/main.rs}
    fn main() {
        // Setup the database first
        <<setup_database>>
    }
    ```

#### 3. "Magic" Headless Exporting ({export})

For simple cases where one Markdown file corresponds to one source file, you can use a headless {export} attribute. illiterate will automatically generate the filename based on the Markdown file's name and the code block's language.

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

## Roadmap

Here are some of the planned features to make illiterate even more powerful. You are welcome to contribute to any of them!

#### Architecture Visualization (--graph)

A picture is worth a thousand lines of code. This feature will generate a visual map of your project's structure.

* **Command:** `illiterate --graph [FILES...]`
* **Functionality:** Outputs a [Graphviz](https://graphviz.org/) dot language representation of the project. It will map the relationships between all {export=...} targets and the {name=...} fragments they include.
* **Example:** `illiterate --graph my_app.md | dot -Tpng > architecture.png`

#### Source Code Syncing (--update)

This provides a "reverse export" to keep the Markdown source of truth synchronized with small, quick changes made directly to the generated code.

* **Command:** `illiterate -u, --update [FILES...]`
* **Functionality:** illiterate will read the content of the on-disk source files. If a file differs from what *would have been* generated, this command will **update the corresponding code block in the Markdown file** to match the on-disk version. This is perfect for backporting quick fixes without manual copy-pasting.

#### Code Editor Integration (LSP)

To provide a seamless, real-time development experience, illiterate will function as a Language Server Protocol (LSP) server.

* **Command:** `illiterate --lsp`
* **Functionality:** This command launches the LSP server. When used with a compatible editor plugin, it enables:
  * **Error Diagnostics:** Underlines includes of non-existent fragments.
  * **Go to Definition:** F12 on `<<my_fragment>>` jumps to its definition.
  * **Completions:** Autocompletes fragment names as you type <<....
  * **Hover Information:** Shows a fragment's content when you hover over it.

## Contributing & Building from Source

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

4. **Re-export the source code:** Use the binary you just built to update the `src/` directory with your changes.

```bash
./target/debug/illiterate illiterate.md
```

5. **Re-build your changes:**

```bash
cargo build
```

## License

`illiterate` is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
