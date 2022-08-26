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

#### Run with Python and Docker

Create the Docker image and volume:

´´´bash
./run-docker -b
´´´

Copy to the volume the logs to analyze. The volume's path is `/var/lib/docker/volumes/nginx-logs-volume/_data`.

Run the script:

´´´bash
./run-docker -r
´´´

You can see the results in the volume's path.

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

## Compare resources

To compare the resources like the CPU and memory required by Python and Rust we can measure them and plot the results.

### Processes created

These are the processes created:

- python: created when the python code is executed.
- nginx_logs: created when the rust code is executed.

You can analyze the resources required by each process.

### Measure resources

After compiling the Rust program, run:

```bash
cd measure
./run-and-measure
```

