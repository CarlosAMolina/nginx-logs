## Introduction

Project to convert Nginx's logs to a csv file.

Available options:

- Convert files in a folder.
- Convert an specific log file.

Files that can be converted:

- Plain text files. Example: access.log
- Gz compressed files. Example: access.log.2.gz

This project is written in Python and Rust and can measure the resources required by each language and compare them.

## Run the project

You can run the Python or the Rust version.

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

#### Run with Rust and Docker

Follow the steps described for Python but using the Rust folder.

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

To compare the resources like:

- Storage
- CPU
- Memory

Required by Python and Rust we can measure them and plot the results.

A detailed explanation can be found in this [link](https://cmoli.es/projects/rust-vs-other-languages/introduction.html).

### Measure storage

Create the Docker image for Python and Rust (described above) and check the size:

```bash
docker images
```

### Measure memory and CPU resources

First compile the Rust program and change the working directory:

```bash
cd measure/measure/
```

#### Measure memory

Run the following script:

```bash
./run-and-measure-memory
```

#### Measure CPU

Run the script that executes the Python and Rust programs and saves the measurements:

```bash
./run-and-measure-cpu
```

The values are exported to files in the `measure/measure/results` folder.

### Plot the measurements

Change directory to:

```bash
cd measure/plot/
```

Install the requirements.txt file and run:

```bash
python src/plot_resources.py
```

The graphs will be exported to files.

### Test plot

Run, in the `measure/plot` folder:

```bash
python -m unittest discover -s tests
```

