# Block references

This is a chunk with a reference to another chunk.

```rust {export}
fn main() {
    <<main_content>>
}
```

And here is the content:

```rust {name=main_content}
println!("Hello World");
```
