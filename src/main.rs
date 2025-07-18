// All necessary packages
use clap::Parser;
use pulldown_cmark::{CodeBlockKind, Event, Parser as MarkdownParser, Tag};
use regex::Regex;
use std::{
    collections::HashMap,
    env,
    fs::{self},
    io,
    path::{Path, PathBuf},
};


// Utility methods
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
/// Processes a list of markdown files and builds an in-memory map of the
/// files to be generated, without writing anything to disk.
fn generate_output_map(
    paths: &[PathBuf],
    root_dir: Option<&PathBuf>,
) -> HashMap<PathBuf, String> {
    // First, we'll store all raw chunks in this vector
    let mut all_chunks = Vec::new();
    
    for path in paths.iter() {
        all_chunks.extend(extract_chunks(path.to_str().unwrap()));
    }


    // Next, we create two data structures with all chunks
    // A map of all named chunks for easy lookup during expansion.
    let named_chunks_map = create_named_chunk_map(&all_chunks);
    
    // A list of the chunks that are marked for export.
    let exportable_chunks = all_chunks.iter().filter(|chunk| chunk.info.export);


    // And finally create the final sources
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


    return source_map;
}
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
                if let CodeBlockKind::Fenced(info_str) = kind {
                    if let Some(info) = parse_info_string(&info_str) {
                        let mut chunk = Chunk {
                            info,
                            content: String::new(),
                        };
                
                        // For empty export directives, we generate a default path
                        if chunk.info.export && chunk.info.path.is_none() {
                            let file_stem = Path::new(file_path).file_stem().unwrap().to_str().unwrap();
                            let extension = lang_ext.get(chunk.info.lang.as_str()).unwrap_or(&"txt");
                            let default_path = format!("{}.{}", file_stem, extension);
                            chunk.info.path = Some(default_path);
                
                        }
                
                        chunks.push(chunk);
                        in_chunk = true;
                    }
                }

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
fn create_named_chunk_map(chunks: &[Chunk]) -> HashMap<String, Vec<&Chunk>> {
    let mut chunk_map: HashMap<String, Vec<&Chunk>> = HashMap::new();

    for chunk in chunks.iter() {
        if let Some(name) = &chunk.info.name {
            chunk_map.entry(name.clone()).or_default().push(chunk);
        }
    }
    chunk_map
}
impl Chunk {
    /// Public method to start the expansion process.
    /// It initializes the tracking stack for circular dependency checks.
    pub fn expand(&self, named_chunks: &HashMap<String, Vec<&Chunk>>) -> String {
        let mut expansion_stack = Vec::new();
        self.expand_recursive(named_chunks, &mut expansion_stack)
    }

    /// Recursively expands the content of this chunk by replacing `<<...>>` references.
    fn expand_recursive(
        &self,
        named_chunks: &HashMap<String, Vec<&Chunk>>,
        expansion_stack: &mut Vec<String>,
    ) -> String {
        // Check for circular dependencies.
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
    
    
        // This will hold the final expanded chunk
        let mut final_content = String::new();
        // This regex matches lines with a named reference in the form <<...>>
        let include_re = Regex::new(r"^(?P<indent>\s*)<<(?P<name>[\w_.-]+)>>\s*$").unwrap();
    
        for line in self.content.lines() {
            if let Some(caps) = include_re.captures(line) {
                // This line contains a named reference.
                let indent_str = caps.name("indent").unwrap().as_str();
                let name_to_include = caps.name("name").unwrap().as_str();
    
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
    
            } else {
                // This line doesn't, so add it as is.
                final_content.push_str(line);
                final_content.push('\n');
            }
        }
    
        // Some post-process we will need to make circular checks work
        if let Some(name) = &self.info.name {
            if expansion_stack.last() == Some(name) {
                expansion_stack.pop();
            }
        }
    
    
        return final_content;
    }

}
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
                differences.push(format!("Could not read file {}: {}", path.display(), e));
            }
        }

    }

    // Also check for any files on disk that shouldn't be there (optional but good practice)
    // For now, we'll stick to the core requirement.

    if differences.is_empty() {
        println!("✅ All {} generated files are in sync with the disk.", output_map.len());
        return true;
    } else {
        println!("❌ Found {} differences:", differences.len());
        for diff in differences {
            println!("  - {}", diff);
        }
        return false;
    }
}


fn main() {
    let args = Cli::parse();

    // 1. Generate the complete output in memory
    let output_map = generate_output_map(&args.files, args.dir.as_ref());

    if args.test {
        // 2a. Run the test logic
        if !run_test_comparison(&output_map) {
            // Exit with a non-zero code to indicate test failure
            std::process::exit(1);
        }

    } else {
        // 2b. Run the file writing logic
        match write_output_to_disk(&output_map) {
            Ok(_) => println!("✅ Successfully exported {} file(s).", output_map.len()),
            Err(e) => {
                eprintln!("🔥 Error writing files to disk: {}", e);
                std::process::exit(1);
            }
        }

    }
}

// Lots and lots of unit tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_simple_chunk() {
        let chunks = extract_chunks("tests/simple.md");
    
        assert!(chunks.len() == 1);
    
        let chunk0 = &chunks[0];
        assert!(chunk0.info.lang == "rust");
        assert_eq!(chunk0.info.path, Some("simple.rs".to_string()));
    }
    
    #[test]
    fn test_extract_two_chunks() {
        let chunks = extract_chunks("tests/two_chunks.md");
    
        assert!(chunks.len() == 2);
    
        let chunk0 = &chunks[0];
        assert!(chunk0.info.lang == "python");
        assert!(chunk0.content == "print(\"Hello World\")\n");
        assert_eq!(chunk0.info.name, Some("hello_world".to_string()));
    
        let chunk1 = &chunks[1];
        assert!(chunk1.info.lang == "rust");
        assert!(chunk1.content == "fn main() {\n    // A first chunk\n}\n");
        assert_eq!(chunk1.info.path, Some("main.rs".to_string()));
    }
    
    #[test]
    fn some_yes_some_no() {
        let chunks = extract_chunks("tests/some_yes_some_no.md");
        assert!(chunks.len() == 2);
    }

    #[test]
    fn test_full_string_parsing() {
        let info = "rust {export=src/main.rs} {name=chunk_1}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            path: Some("src/main.rs".to_string()),
            name: Some("chunk_1".to_string()),
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_language_and_name() {
        let info = "python {name=hello_world}";
        let expected = ChunkInfo {
            lang: "python".to_string(),
            path: None,
            name: Some("hello_world".to_string()),
            export: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_attributes_in_different_order() {
        let info = "rust {name=chunk_1} {export=src/main.rs}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            path: Some("src/main.rs".to_string()),
            name: Some("chunk_1".to_string()),
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_language_only() {
        let info = "python";
        assert_eq!(parse_info_string(info), None);
    }
    
    #[test]
    fn test_with_export_only() {
        let info = "javascript {export=app.js}";
        let expected = ChunkInfo {
            lang: "javascript".to_string(),
            path: Some("app.js".to_string()),
            name: None,
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_with_headless_export_only() {
        let info = "rust {export}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            path: None,
            name: None,
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_headless_export_with_name() {
        let info = "rust {name=my_frag} {export}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            path: None,
            name: Some("my_frag".to_string()),
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_with_name_only() {
        let info = "rust {name=my_fragment}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            path: None,
            name: Some("my_fragment".to_string()),
            export: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_with_extra_whitespace() {
        let info = "  bash   {export=run.sh}  ";
        let expected = ChunkInfo {
            lang: "bash".to_string(),
            path: Some("run.sh".to_string()),
            name: None,
            export: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }
    
    #[test]
    fn test_no_match_for_invalid_format() {
        let info = "{invalid_format}";
        assert_eq!(parse_info_string(info), None);
    }
    
    #[test]
    fn test_empty_string() {
        let info = "";
        assert_eq!(parse_info_string(info), None);
    }

    // ERROR: Chunk 'tests_build_chunk_map' not found
    // ERROR: Chunk 'tests_expand_chunk' not found
}
