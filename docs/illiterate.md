# Illiterate

`illiterate` is a tool to enable literate programming.
It extracts code from Markdown files and exports it to source files.

The core of `illiterate` is a simple parser that reads Markdown files and extracts code blocks, building a web of interconnected chunks that reference other chunks.

Here is the main loop. First we parse the command line arguments, then we generate the complete output map (that contains all parsed chunks and relations), and finally we either run the test logic or the file writing logic.

```rust {export=main.rs}
// All necessary packages
<<packages>>

// Utility methods
<<utilities>>

fn main() {
    let args = Cli::parse();

    // 1. Generate the complete output in memory
    let output_map = generate_output_map(&args.files, args.dir.as_ref());

    if args.test {
        // 2a. Run the test logic
        <<test_source>>
    } else {
        // 2b. Run the file writing logic
        <<generate_source>>
    }
}

// Lots and lots of unit tests
<<tests>>
```

The comparison logic is quite simple. We just compare the output map with the expected output map. This will print all differences between the two maps and exit with a non-zero output if there is any difference.

```rust {name=test_source}
if !run_test_comparison(&output_map) {
    // Exit with a non-zero code to indicate test failure
    std::process::exit(1);
}
```

The writing logic is also quite simple. We just write all files to disk and print a success message. If there is an error, we print an error message and exit with a non-zero output.

```rust {name=generate_source}
match write_output_to_disk(&output_map) {
    Ok(_) => println!("✅ Successfully exported {} file(s).", output_map.len()),
    Err(e) => {
        eprintln!("🔥 Error writing files to disk: {}", e);
        std::process::exit(1);
    }
}
```

Now let's get into the meat of the logic.

## The CLI

First, let's build the command line interface. We will use the `clap` crate for this. First, we need to include it in the packages.

```rust {name=packages}
use clap::Parser;
```

And then we define the `Cli` struct that represents the input. Here we are using Rust's powerful macro system to construct the CLI directly from type annotations.

```rust {name=utilities}
/// A fast, zero-config, programmer-first literate programming tool.
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// One or more Markdown files to process
    #[arg(required = true)]
    files: Vec<PathBuf>,

    /// Sets the root output directory for all exported files
    #[arg(long, short, value_name = "DIRECTORY")]
    dir: Option<PathBuf>,

    /// Run in test mode. Compares generated files with their
    /// on-disk counterparts and reports differences.
    #[arg(long, short)]
    test: bool,
}
```

## The Main Loop

The core functionality in `illiterate` can be split into two big tasks:

1. building a map of all the code chunks in the input files, and;
2. using that map to construct the output files.

The first part is relatively straightforward. We will need a Markdown parser to read the input files, and a way to store the code chunks. The second part will be slightly more complicated because chunks can reference other chunks, so the expansion of a chunk into actual code requires a recursive traversal of the chunk graph.

The top-level functionality that encapsulates all this process in the method `generate_output_map`. Let's take a look at the big picture, and then dive into the actual implementation.

```rust {name=utilities}
/// Processes a list of markdown files and builds an in-memory map of the
/// files to be generated, without writing anything to disk.
fn generate_output_map(
    paths: &[PathBuf],
    root_dir: Option<&PathBuf>,
) -> HashMap<PathBuf, String> {
    // First, we'll store all raw chunks in this vector
    <<extract_all_chunks>>

    // Next, we create two data structures with all chunks
    <<create_data_structures>>

    // And finally create the final sources
    <<synthesize_sources>>

    return source_map;
}
```

The process to extract all code chunks requires iterating over each input file, performing the extraction of chunks in that file, and collecting all chunks in a global vector. We will look at the `extract_chunks` function in short, which is where the core of the work happens.

```rust {name=extract_all_chunks}
let mut all_chunks = Vec::new();

for path in paths.iter() {
    all_chunks.extend(extract_chunks(path.to_str().unwrap()));
}
```

Once we have all chunks, we need two data structures. The first is a hash-based map of all named chunks (those that have a `name` attribute). In this structure we will associated to a single name all the chunks declared with that name, so we can later expand them in sequence.

The second structure is a simple list of all chunks that have an `export` directive, which will be processed also in sequence.

```rust {name=create_data_structures}
// A map of all named chunks for easy lookup during expansion.
let named_chunks_map = create_named_chunk_map(&all_chunks);

// A list of the chunks that are marked for export.
let exportable_chunks = all_chunks.iter().filter(|chunk| chunk.info.export);
```

The final part is to synthesize the tangled source files. This is done by iterating over all exportable chunks and expanding them. The expanded content is then appended to the appropriate file's content in the map. This creates an in-memory representation of the tangled source, that will later be either compared to filesystem source files (if `--test` is passed) or written to disk.

```rust {name=synthesize_sources}
// This map will hold the final content for each output file.
let mut source_map: HashMap<PathBuf, String> = HashMap::new();

// Define the base dir (or use default)
let base_dir = root_dir.cloned().unwrap_or_else(|| env::current_dir().unwrap());

// Expand all exportable chunks and collect their content into the output map.
for chunk in exportable_chunks {
    // This is the where the recursive magic happens
    let content = chunk.expand(&named_chunks_map);
    // This is the path to the file where the chunk should be written.
    let file_path = base_dir.join(chunk.info.path.as_ref().unwrap());
    // Append the expanded content of the current chunk to the appropriate file's content in the map.
    source_map.entry(file_path).or_default().push_str(&content);
}
```

Now that we have the big picture ready, let's take a look at the specifics.

## Extracting chunks

The first step in the main loop is to find all code chunks and build the two data structures explained before. Let's look at that code next.

We will begin by examining the code that extracts all chunks from a single source file.

We can use the markdown parser from `pulldown-cmark` to easily identify all relevant code snippets in a given source file. For this, we will need to first import relevant packages (remember we already have a `Parser` from `clap` imported).

```rust {name=packages}
use pulldown_cmark::{CodeBlockKind, Event, Parser as MarkdownParser, Tag};
```

The most important type here is `Parser`, which we rename as `MarkdownParser`. For the parsing method itself, we take advantage of `pulldown-cmark` event-based parsing. The core of the method is to iterate over all parsing events, and identify the ones we need to process.

### The Chunk Struct

Here is the `Chunk` structure we want to produce, and the related `ChunkInfo`, which represent all the information we need about a code chunk.

```rust {name=utilities}
#[derive(Debug, PartialEq)]
struct Chunk {
    info: ChunkInfo,
    content: String,
}

#[derive(Debug, PartialEq, Clone)]
struct ChunkInfo {
    lang: String,
    path: Option<String>,
    name: Option<String>,
    export: bool,
}
```

### The Extract Chunks Method

And here is, finally, the method that extracts all chunks from a single markdown file.

This method only cares when a code block begins and ends, to gather the necessary info (stored in a `ChunkInfo`) all the text in-between. The begining of a code block is rather complicated because we need to parse all attributes, so we'll leave that out for a minute, and take a look at the high-level code.

```rust {name=utilities}
fn extract_chunks(file_path: &str) -> Vec<Chunk> {
    let mut chunks = Vec::new();
    let content = std::fs::read_to_string(file_path).unwrap();
    let parser = MarkdownParser::new(&content);
    let mut in_chunk = false;

    // list of common language extensions (e.g., .py, .rs, .cpp)
    let lang_ext = language_extensions();

    for event in parser {
        match event {
            Event::Start(Tag::CodeBlock(kind)) => {
                <<process_start_code_block>>
            }
            Event::Text(text) => {
                // If we're inside a code chunk, just take every text
                // and append it to the last chunk (the one we're inside of)
                if in_chunk {
                    if let Some(last_chunk) = chunks.last_mut() {
                        last_chunk.content.push_str(&text);
                    }
                }
            }
            Event::End(_) => {
                in_chunk = false;
            }
            _ => {} // Nothing else matters
        }
    }

    return chunks;
}
```

The thing we care most about at the begining of a code block is the info string which contains the language name (e.g., rust) and all possible attributes, like `export` and `name`.

The parsing of this info string is performed in the aptly named `parse_info_string`, which we'll look next. But with that in place, the only significant complexity remaining is to generate a default path for empty `{export}` directives.

```rust {name=process_start_code_block}
if let CodeBlockKind::Fenced(info_str) = kind {
    if let Some(info) = parse_info_string(&info_str) {
        let mut chunk = Chunk {
            info,
            content: String::new(),
        };

        // For empty export directives, we generate a default path
        if chunk.info.export && chunk.info.path.is_none() {
            <<generate_default_path>>
        }

        chunks.push(chunk);
        in_chunk = true;
    }
}
```

Generating a default path is basically a bit of Rust golf to find the stem of the current markdown file (the part of the filename without the extension), and append the corresponding from a predefined hash map we hard-coded.

```rust {name=generate_default_path}
let file_stem = Path::new(file_path).file_stem().unwrap().to_str().unwrap();
let extension = lang_ext.get(chunk.info.lang.as_str()).unwrap_or(&"txt");
let default_path = format!("{}.{}", file_stem, extension);
chunk.info.path = Some(default_path);
```

And just for completion, here is the hard-coded hash map.

```rust {name=utilities}
fn language_extensions() -> HashMap<&'static str, &'static str> {
    let mut map = HashMap::new();

    map.insert("python", "py");
    map.insert("javascript", "js");
    map.insert("java", "java");
    map.insert("csharp", "cs");
    map.insert("cpp", "cpp");
    map.insert("c", "c");
    map.insert("typescript", "ts");
    map.insert("php", "php");
    map.insert("swift", "swift");
    map.insert("ruby", "rb");
    map.insert("go", "go");
    map.insert("kotlin", "kt");
    map.insert("rust", "rs");
    map.insert("r", "r");
    map.insert("matlab", "m");
    map.insert("perl", "pl");
    map.insert("scala", "scala");
    map.insert("objc", "m");
    map.insert("lua", "lua");
    map.insert("dart", "dart");
    map.insert("haskell", "hs");
    map.insert("groovy", "groovy");
    map.insert("elixir", "ex");
    map.insert("julia", "jl");
    map.insert("fsharp", "fs");
    map.insert("clojure", "clj");
    map.insert("erlang", "erl");
    map.insert("assembly", "asm");
    map.insert("sql", "sql");
    map.insert("bash", "sh");

    return map;
}
```

### The Parse Info String Method

To finish off this part of the functionality, we'll end by looking at the `parse_info_string` method.

The core of this method is using regular expressions to first, split the info string into pieces, and then parsing each of those pieces. For example, consider a code block like the following:

    ```rust {export=main.rs}
    ```

The info string will be `rust {export=main.rs}`. Our method needs to split it into `rust` and `export=main.rs`, to later extract the `main.rs` string from the `export` attribute.

There is no much else we can say about this rather than showing the entire method, so buckle up.

```rust {name=utilities}
fn parse_info_string(info_string: &str) -> Option<ChunkInfo> {
    // First, capture the language and the rest of the attributes string.
    let lang_re = Regex::new(r"^\s*(?P<lang>\w+)\s*(?P<attrs>.*)$").unwrap();
    let caps = lang_re.captures(info_string)?;
    let lang = caps.name("lang").unwrap().as_str().to_string();
    let attrs_str = caps.name("attrs").unwrap().as_str();

    // This regex finds all attributes, handling both `{key=value}` and `{key}` formats.
    let attr_re = Regex::new(r"\{(?P<key>[a-zA-Z\d_]+)(=(?P<value>[^}]+))?\}").unwrap();

    let mut path = None;
    let mut name = None;
    let mut export = false;

    // Iterate over all attribute matches found in the string.
    for attr_caps in attr_re.captures_iter(attrs_str) {
        let key = attr_caps.name("key").unwrap().as_str();
        // The "value" capture group is now optional.
        let value = attr_caps.name("value");

        <<extract_attribute_values>>
    }

    if path.is_none() && name.is_none() && !export {
        return None;
    }

    return Some(ChunkInfo {
        lang: lang,
        path: path,
        name: name,
        export: export,
    });
}
```

And here is the missing part to extract attribute values. For now, we only accept the `export` and `name` attributes.

```rust {name=extract_attribute_values}
match key {
    "export" => {
        export = true;
        if let Some(val_match) = value {
            // This was {export=...}, so we have a path.
            path = Some(val_match.as_str().to_string());
        }
    }
    "name" => {
        if let Some(val_match) = value {
            name = Some(val_match.as_str().to_string());
        }
        // Note: {name} without a value is ignored.
    }
    _ => {} // Ignore unknown attributes
}
```

Of course, we can't forget to import the `regex` package.

```rust {name=packages}
use regex::Regex;
```

Putting all of the above together, we now have the ability to extract code chunks from all markdown files, and store them in a huge list of `Chunk` objects. Let's move to sorting them.

### Sorting Chunks

Once we have all code chunks, we need to separate them into two lists. One is simply the list of chunks with an `export` directive, which will already did. The other is what I call a `named_chunk_map`, which is a hash map of strings to the list of all chunks named with that key. This is necessary because we later want to concatenate all those equally-named chunks in a single blob.

This is a straightforward method that simply iterates over all chunks with a `name=...` directive and appends them to the corresponding key.

```rust {name=utilities}
fn create_named_chunk_map(chunks: &[Chunk]) -> HashMap<String, Vec<&Chunk>> {
    let mut chunk_map: HashMap<String, Vec<&Chunk>> = HashMap::new();

    for chunk in chunks.iter() {
        if let Some(name) = &chunk.info.name {
            chunk_map.entry(name.clone()).or_default().push(chunk);
        }
    }
    chunk_map
}
```

## Expanding Chunks

Once we have all chunks correctly sorted out (the exportable chunks in a flat list, and the named chunks in a map grouped by name), we can start to tangle the output files.

The basic idea, as we already saw, is to go over all exportable chunks, and build the corresponding output files by expanding all references to named chunks, recursively. This will create an in-memory representation of all output files with the flat, tangled content that ultimately must either be written to disk or compared with the existing sources in disk.

The only piece left is the recursive expansion of named chunks. The main method is shown below:


```rust {name=utilities}
impl Chunk {
    /// Public method to start the expansion process.
    /// It initializes the tracking stack for circular dependency checks.
    pub fn expand(&self, named_chunks: &HashMap<String, Vec<&Chunk>>) -> String {
        let mut expansion_stack = Vec::new();
        self.expand_recursive(named_chunks, &mut expansion_stack)
    }

    <<expand_recursive>>
}
```

And here is the recursive implementation:

```rust {name=expand_recursive}
/// Recursively expands the content of this chunk by replacing `<<...>>` references.
fn expand_recursive(
    &self,
    named_chunks: &HashMap<String, Vec<&Chunk>>,
    expansion_stack: &mut Vec<String>,
) -> String {
    // Check for circular dependencies.
    <<check_circular_dependencies_in>>

    // This will hold the final expanded chunk
    let mut final_content = String::new();
    // This regex matches lines with a named reference in the form <<...>>
    let include_re = Regex::new(r"^(?P<indent>\s*)<<(?P<name>[\w_.-]+)>>\s*$").unwrap();

    for line in self.content.lines() {
        if let Some(caps) = include_re.captures(line) {
            // This line contains a named reference.
            let indent_str = caps.name("indent").unwrap().as_str();
            let name_to_include = caps.name("name").unwrap().as_str();

            <<process_named_reference>>
        } else {
            // This line doesn't, so add it as is.
            final_content.push_str(line);
            final_content.push('\n');
        }
    }

    // Some post-process we will need to make circular checks work
    <<check_circular_dependencies_out>>

    return final_content;
}
```

The recursive expansion itself is not that complicated once we have everything in place. We just need to iterate over all named chunks associated with the corresponding name and call their `expand_recursive` method.

The `expansion_stack` parameter is what helps us keep track of the current call stack, so we never enter a loop. We will see that next.

```rust {name=process_named_reference}
match named_chunks.get(name_to_include) {
    Some(chunks_to_include) => {
        for chunk in chunks_to_include {
            // Recursively expand the included chunk.
            let expanded_include = chunk.expand_recursive(named_chunks, expansion_stack);
            // Add the captured indentation to each line of the expanded content.
            for expanded_line in expanded_include.lines() {
                final_content.push_str(indent_str);
                final_content.push_str(expanded_line);
                final_content.push('\n');
            }
            final_content.push('\n');
        }
    }
    None => {
        // Handle missing chunk reference
        panic!("ERROR: Chunk '{}' not found", name_to_include);
    }
}
```

So the only piece left is to check for circular dependencies. We keep a stack of the current call stack and check if we are trying to expand a chunk that is already in the stack. If so, we panic.

```rust {name=check_circular_dependencies_in}
if let Some(name) = &self.info.name {
    if expansion_stack.contains(name) {
        let error_msg = format!(
            "\n// ERROR: Circular reference detected for chunk '{}'\n",
            name
        );
        return error_msg;
    }
    expansion_stack.push(name.clone());
}
```

And at the end of the method, we need to add this piece of code to pop the chunk from the stack.

```rust {name=check_circular_dependencies_out}
if let Some(name) = &self.info.name {
    if expansion_stack.last() == Some(name) {
        expansion_stack.pop();
    }
}
```

With this method in place, we are basically done. All that's left is a couple utility methods we called from `main`.

## Final Utilities

The first such utility method is simply to write the in-memory file map to the disk.

```rust {name=utilities}
/// Writes the in-memory file map to the disk, overwriting existing files.
fn write_output_to_disk(output_map: &HashMap<PathBuf, String>) -> io::Result<()> {
    for (path, content) in output_map {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        fs::write(path, content)?;
    }
    Ok(())
}
```

And the other missing method is the one that compares the in-memory file map with the files on disk. This is useful for CI/CD to make sure we don't commit markdown files that are out of sync with the tangled source code.

```rust {name=utilities}
/// Compares the in-memory file map with files on disk and reports differences.
fn run_test_comparison(output_map: &HashMap<PathBuf, String>) -> bool {
    let mut differences = Vec::new();

    for (path, generated_content) in output_map {
        match fs::read_to_string(path) {
            Ok(disk_content) => {
                if &disk_content != generated_content {
                    differences.push(format!("Content mismatch in {}", path.display()));
                }
            }
            Err(e) if e.kind() == io::ErrorKind::NotFound => {
                differences.push(format!("Missing expected file on disk: {}", path.display()));
            }
            Err(e) => {
                differences.push(format!(
                    "Could not read file {}: {}",
                    path.display(),
                    e
                ));
            }
        }
    }

    // Also check for any files on disk that shouldn't be there (optional but good practice)
    // For now, we'll stick to the core requirement.

    if differences.is_empty() {
        println!("✅ All {} generated files are in sync with the disk.", output_map.len());
        true
    } else {
        println!("❌ Found {} differences:", differences.len());
        for diff in differences {
            println!("  - {}", diff);
        }
        false
    }
}
```

Finally, here are some missing packages we've been assuming were imported.


```rust {name=packages}
use std::{
    collections::HashMap,
    env,
    fs::{self},
    io,
    path::{Path, PathBuf},
};
```
