# Tests

Here we briefly explain the unit tests for `illiterate`.

```rust {name=tests}
#[cfg(test)]
mod tests {
    use super::*;

    <<tests_extract_chunks>>
    <<tests_info_extraction>>
    <<tests_build_chunk_map>>
    <<tests_expand_chunk>>
}
```

This one is for building the named chunk map.

```rust {name=build_chunk_map}
#[test]
fn test_build_chunk_map() {
    let chunks = extract_chunks("tests/references.md");
    let chunk_map = create_named_chunk_map(&chunks);

    assert!(chunk_map.len() == 1);
    assert!(chunk_map.contains_key("main_content"));
}
```

These tests check that we can extract chunks from a markdown file with different structures.

```rust {name=tests_extract_chunks}
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
```

These tests are for the `parse_info_string` function. They check that the function correctly parses the information string into a `ChunkInfo` struct for a bunch of combinations of the information string.

```rust {name=tests_info_extraction}
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
```

These are tests for the recursive chunk expansion logic.

```rust {name=tests_expand_chunks}
#[test]
fn expand_simple_chunk() {
    let chunks = extract_chunks("tests/references.md");
    let chunk_map = create_named_chunk_map(&chunks);

    // The exportable chunk is the first one
    let main_chunk = chunks.iter().find(|c| c.info.export).unwrap();
    let expanded = main_chunk.expand(&chunk_map);

    assert_eq!(expanded, "fn main() {\n    println!(\"Hello World\");\n\n}\n");
}

#[test]
fn test_expand_complex() {
    let chunks = extract_chunks("tests/complex_references.md");
    let chunk_map = create_named_chunk_map(&chunks);

    let main_chunk = chunks.iter().find(|c| c.info.name == Some("helper".to_string())).unwrap();
    let content = main_chunk.expand(&chunk_map);

    assert!(content.contains("let a = 0;"));
}
```
