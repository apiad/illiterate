use pulldown_cmark::{CodeBlockKind, Event, Parser, Tag};
use regex::Regex;


/// Holds the parsed information from a code block's info string.
/// `headless_export` is true if `{export}` is found.
/// `export` is Some(path) if `{export=path}` is found.
#[derive(Debug, PartialEq, Clone)]
struct ChunkInfo {
    lang: String,
    export: Option<String>,
    name: Option<String>,
    headless: bool,
}

/// Parses a fenced code block's info string (e.g., "rust {export=main.rs} {name=chunk_1}")
/// using a regular expression with named capture groups.
///
/// It returns an `Option<ChunkInfo>` which is `Some` on a successful parse
/// and `None` if the string doesn't match the expected format.
fn parse_info_string(info_string: &str) -> Option<ChunkInfo> {
    // First, capture the language and the rest of the attributes string.
    let lang_re = Regex::new(r"^\s*(?P<lang>\w+)\s*(?P<attrs>.*)$").unwrap();

    let caps = lang_re.captures(info_string)?;

    let lang = caps.name("lang").unwrap().as_str().to_string();
    let attrs_str = caps.name("attrs").unwrap().as_str();

    // This regex finds all attributes, handling both `{key=value}` and `{key}` formats.
    // The `(?:=(?P<value>[^}]+))?` part makes the `=value` optional.
    let attr_re = Regex::new(r"\{(?P<key>\w+)(?:=(?P<value>[^}]+))?\}").unwrap();

    let mut export = None;
    let mut name = None;
    let mut headless = false;

    // Iterate over all attribute matches found in the string.
    for attr_caps in attr_re.captures_iter(attrs_str) {
        let key = attr_caps.name("key").unwrap().as_str();
        // The "value" capture group is now optional.
        let value = attr_caps.name("value");

        match key {
            "export" => {
                if let Some(val_match) = value {
                    // This was {export=...}, so we have a path.
                    export = Some(val_match.as_str().to_string());
                } else {
                    // This was {export}, the headless version.
                    headless = true;
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

    return Some(ChunkInfo {
        lang: lang,
        export: export,
        name: name,
        headless: headless,
    })
}

#[derive(Debug, PartialEq)]
struct Chunk {
    info: ChunkInfo,
    content: String,
}

fn extract_chunks(file_path: &str) -> Vec<Chunk> {
    let mut chunks = Vec::new();

    // open file path
    let content = std::fs::read_to_string(file_path).unwrap();
    let parser = Parser::new(&content);

    for event in parser {
        match event {
            Event::Start(Tag::CodeBlock(kind)) => {
                if let CodeBlockKind::Fenced(info) = kind {
                    let chunk_info = parse_info_string(&info).unwrap();

                    chunks.push(Chunk {
                        info: chunk_info,
                        content: String::new(),
                    })
                }
            }

            _ => {}
        }
    }

    return chunks;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_simple_chunk() {
        // open tests/simple.md
        let chunks = extract_chunks("tests/simple.md");

        assert!(chunks.len() == 1);

        let chunk0 = &chunks[0];
        assert!(chunk0.info.lang == "rust");
    }

    #[test]
    fn test_extract_two_chunks() {
        // open tests/two_chunks.md
        let chunks = extract_chunks("tests/two_chunks.md");

        assert!(chunks.len() == 2);

        let chunk0 = &chunks[0];
        assert!(chunk0.info.lang == "rust");

        let chunk1 = &chunks[1];
        assert!(chunk1.info.name.as_ref().unwrap() == "hello_world")
    }

    #[test]
    fn test_full_string_parsing() {
        let info = "rust {export=src/main.rs} {name=chunk_1}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            export: Some("src/main.rs".to_string()),
            name: Some("chunk_1".to_string()),
            headless: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_attributes_in_different_order() {
        let info = "rust {name=chunk_1} {export=src/main.rs}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            export: Some("src/main.rs".to_string()),
            name: Some("chunk_1".to_string()),
            headless: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_language_only() {
        let info = "python";
        let expected = ChunkInfo {
            lang: "python".to_string(),
            export: None,
            name: None,
            headless: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_with_export_only() {
        let info = "javascript {export=app.js}";
        let expected = ChunkInfo {
            lang: "javascript".to_string(),
            export: Some("app.js".to_string()),
            name: None,
            headless: false
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_with_headless_export_only() {
        let info = "rust {export}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            export: None,
            name: None,
            headless: true,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_headless_export_with_name() {
        let info = "rust {name=my_frag} {export}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            export: None,
            name: Some("my_frag".to_string()),
            headless: true
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_with_name_only() {
        let info = "rust {name=my_fragment}";
        let expected = ChunkInfo {
            lang: "rust".to_string(),
            export: None,
            name: Some("my_fragment".to_string()),
            headless: false,
        };
        assert_eq!(parse_info_string(info), Some(expected));
    }

    #[test]
    fn test_with_extra_whitespace() {
        let info = "  bash   {export=run.sh}  ";
        let expected = ChunkInfo {
            lang: "bash".to_string(),
            export: Some("run.sh".to_string()),
            name: None,
            headless: false,
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
}
