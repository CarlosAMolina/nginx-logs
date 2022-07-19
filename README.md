## Contents

- [Introduction](#introduction)
- [Folders](#folders)
  - [Python](#python)
    - [Run with Python](#run-with-python)
    - [Test Python](#test-python)
  - [Rust](#rust)
    - [Run with Rust](#run-with-rust)
    - [Test Rust](#test-rust)

## Introduction

Project to convert Nginx's logs to a csv file.

Available options:

- Convert files in a folder.
- Convert an specific log file.

Files that can be converted:

- Plain text files. Example: access.log
- Gz compressed files. Example: access.log.2.gz


## Folders

### Python

Code using the Python language.

Run at the main path of the project:

```bash
cd python
```

#### Run with Python

Work with files in a folder:

```bash
python src/main.py /tmp/logs
```

Work with a log file:

```bash
python src/main.py /tmp/logs/access.log.2.gz
```

#### Test Python

```bash
python -m unittest discover -s tests
```

### Rust

Code using the Rust language.

Run at the main path of the project:

```bash
cd rust
```

#### Run with Rust

Work with files in a folder:

```bash
cargo run /tmp/logs
```

Work with a log file:

```bash
cargo run /tmp/logs/access.log.2.gz
```

#### Test Rust

```bash
cargo test
```

