# Some yes, some no

Let's try to parse some chunks that are correct like

```rust {export}
fn main() {
    // This one goes
}
```

And another like:

```rust {name=chunk1}
fn another() {
    return 0;
}
```

But then some chunks like:

```python
print("Hello World")
```

Should not be parsed.
