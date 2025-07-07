# A file with complex references

This is a method we will need later:

```rust {name=helper}
fn helper() {
    <<helper_content>>
    return 42;
}
```

This is our main method:

```rust {export}
fn main() {
    <<main_content>>
    helper();
}

<<helper>>
```

This is the main content:

```rust {name=main_content}
println!("Hello World");
```

And finally this is what goes inside the helper:

```rust {name=helper_content}
let a = 0;
```

Let's see how this goes.
