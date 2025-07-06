use pulldown_cmark::{Parser, Tag, CodeBlockKind, Event};

fn main() {

}

#[derive(Debug)]
struct Chunk {
    language: String,
    content: String,
    name: String,
    path: String,
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
                    chunks.push(Chunk {
                        name: info.to_string(),
                        content: String::new(),
                        path: String::new(),
                        language: info.to_string(),
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
        assert!(chunk0.language == "rust");
    }
}