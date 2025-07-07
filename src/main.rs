use pulldown_cmark::{CodeBlockKind, Event, Parser, Tag};
use regex::Regex;


#[derive(Debug, PartialEq, Clone)]
struct ChunkInfo {
    lang: String,
    path: Option<String>,
    name: Option<String>,
    export: bool,
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
        path,
        name: name,
        export,
    })
}


#[derive(Debug, PartialEq)]
struct Chunk {
    info: ChunkInfo,
    content: String,
}

fn extract_chunks(file_path: &str) -> Vec<Chunk> {
    let mut chunks = Vec::new();
    let content = std::fs::read_to_string(file_path).unwrap();
    let parser = Parser::new(&content);
    let mut in_chunk = false;

    for event in parser {
        match event {
            Event::Start(Tag::CodeBlock(kind)) => {
                if let CodeBlockKind::Fenced(info_str) = kind {
                    if let Some(info) = parse_info_string(&info_str) {
                        chunks.push(Chunk {
                            info,
                            content: String::new(),
                        });
                        in_chunk = true;
                    }
                }
            }
            Event::Text(text) => {
                if in_chunk {
                    if let Some(last_chunk) = chunks.last_mut() {
                        last_chunk.content.push_str(&text);
                    }
                }
            }
            Event::End(_) => {
                in_chunk = false;
            }
            _ => {}
        }
    }

    chunks
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
        assert!(chunk0.info.lang == "python");
        assert!(chunk0.content == "print(\"Hello World\")\n");

        let chunk1 = &chunks[1];
        assert!(chunk1.info.lang == "rust");
        assert!(chunk1.content == "fn main() {\n    // A first chunk\n}\n");
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
            export: true
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
            export: true
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
}
