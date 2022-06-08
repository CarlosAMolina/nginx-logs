use std::env;
use std::error::Error;
use std::fmt;
use std::fs::{self, File};
use std::io::Write;
use std::io::{self, BufRead};
use std::path::Path;

use csv::Writer;
use csv::WriterBuilder;
use lazy_static::lazy_static;
use regex::Regex;
use serde_derive::Serialize;

pub struct Config {
    file_or_path: String,
}

impl Config {
    pub fn new(mut args: env::Args) -> Result<Config, &'static str> {
        println!("Arguments: {:?}", args);
        args.next();
        let file_or_path = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a file name or a path"),
        };
        println!("Checking: {}", file_or_path);

        Ok(Config { file_or_path })
    }
}

#[derive(Debug, PartialEq, Serialize)]
struct Log<'a> {
    remote_addr: &'a str,
    remote_user: &'a str,
    time_local: &'a str,
    request: &'a str,
    status: &'a str,
    body_bytes_sent: &'a str,
    http_referer: &'a str,
    http_user_agent: &'a str,
}

impl<'a> fmt::Display for Log<'a> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{},{},{},{},{},{},{},{}",
            self.remote_addr,
            self.remote_user,
            self.time_local,
            self.request,
            self.status,
            self.body_bytes_sent,
            self.http_referer,
            self.http_user_agent,
        )
    }
}

struct FileAndDisplay<'a> {
    display: &'a std::path::Display<'a>,
    file: &'a mut std::fs::File,
}

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let file_or_path_to_check = &Path::new(&config.file_or_path);
    let path_to_check = match file_or_path_to_check.is_file() {
        true => file_or_path_to_check.parent().unwrap(),
        false => file_or_path_to_check,
    };
    let path_csv = path_to_check.join("result.csv");
    //https://docs.rs/csv/latest/csv/tutorial/index.html#writing-csv
    let mut writer_csv = get_csv_writer_builder().from_path(&path_csv)?;
    println!("File with logs as csv: {}", path_csv.display());
    let path_error = path_to_check.join("error.txt");
    let display_error = path_error.display();
    // https://doc.rust-lang.org/rust-by-example/std_misc/file/create.html
    let mut file_error = get_new_file(&path_error)?;
    let mut file_and_display_error = FileAndDisplay {
        display: &display_error,
        file: &mut file_error,
    };
    println!("File with not parsed logs: {}", path_error.display());
    if file_or_path_to_check.is_file() {
        export_file_to_csv(
            &config.file_or_path,
            &mut writer_csv,
            &mut file_and_display_error,
        )?;
    } else if file_or_path_to_check.is_dir() {
        let filenames = get_filenames_to_analyze_in_path(&config.file_or_path)?;
        for filename in filenames {
            let file_str = match config.file_or_path.ends_with('/') {
                true => format!("{}{}", config.file_or_path, filename),
                false => format!("{}/{}", config.file_or_path, filename),
            };
            export_file_to_csv(&file_str, &mut writer_csv, &mut file_and_display_error)?;
        }
    }
    Ok(())
}

fn get_csv_writer_builder() -> WriterBuilder {
    WriterBuilder::new()
}

fn get_filenames_to_analyze_in_path(path: &str) -> Result<Vec<String>, Box<dyn Error>> {
    //https://doc.rust-lang.org/std/fs/fn.read_dir.html
    let entries = fs::read_dir(path)?
        .map(|res| res.map(|e| e.path()))
        .collect::<Result<Vec<_>, io::Error>>()?;
    let filenames = entries
        .iter()
        .map(|e| e.file_name().unwrap().to_str().unwrap())
        .collect::<Vec<&str>>();
    Ok(get_log_filenames_sort_reverse(&filenames))
}

fn get_log_filenames_sort_reverse(filenames: &[&str]) -> Vec<String> {
    lazy_static! {
        static ref FILE_NUMBER: Regex = Regex::new(r"^access\.log\.(?P<file_number>\d+)").unwrap();
    }
    let mut numbers = Vec::<u8>::new();
    for filename in filenames.iter() {
        FILE_NUMBER.captures(filename).and_then(|cap| {
            cap.name("file_number")
                .map(|number| numbers.push(number.as_str().parse::<u8>().unwrap()))
        });
    }
    numbers.sort_unstable();
    numbers.reverse();
    let mut result = Vec::<String>::new();
    for number in numbers.iter() {
        result.push(format!("access.log.{}", number));
    }
    if filenames.contains(&"access.log") {
        result.push("access.log".to_string());
    }
    result
}

fn export_file_to_csv(
    file_to_check: &str,
    writer_csv: &mut Writer<File>,
    file_and_display_error: &mut FileAndDisplay,
) -> Result<(), Box<dyn Error>> {
    println!("Init file: {}", file_to_check);

    let lines = read_lines(file_to_check).expect("Something went wrong reading the file");
    for line in lines {
        let log_line = line.expect("Something went wrong reading the line");
        let log = get_log(&log_line);
        match log {
            None => {
                eprintln!("Not parsed: {}", log_line);
                write_line_to_file(file_and_display_error, log_line)?;
            }
            Some(log_csv) => {
                writer_csv.serialize(log_csv)?;
            }
        }
    }
    writer_csv.flush()?;
    Ok(())
}

fn get_new_file(path: &std::path::Path) -> Result<std::fs::File, String> {
    let file = match File::create(&path) {
        Err(why) => return Err(format!("couldn't create {}: {}", path.display(), why)),
        Ok(file) => file,
    };
    Ok(file)
}

fn write_line_to_file(file_and_display: &mut FileAndDisplay, line: String) -> Result<(), String> {
    if let Err(e) = file_and_display.file.write_all(line.as_bytes()) {
        return Err(format!(
            "couldn't write to {}: {}",
            file_and_display.display, e
        ));
    }
    if let Err(e) = file_and_display.file.write_all(b"\n") {
        return Err(e.to_string());
    }
    Ok(())
}

// https://doc.rust-lang.org/rust-by-example/std_misc/file/read_lines.html
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn get_log(text: &str) -> Option<Log> {
    lazy_static! {
        static ref RE: Regex = Regex::new(
            r#"(?x)
          ^
          ((\d{1,3}[\.]){3}\d{1,3}) # IPv4
          \s-\s
          (.+)                      # Remote user
          \s\[
          (.+)                      # Time local
          \]\s"
          (.*)                      # Request
          "\s
          (\d{1,3})                 # Status
          \s
          (\d+)                     # Body bytes sent
          \s"
          (.+)                      # HTTP referer
          "\s"
          (.+)                      # HTTP user agent
          "
        "#,
        )
        .unwrap();
    }
    RE.captures(text).and_then(|cap| {
        let groups = (
            cap.get(1),
            cap.get(3),
            cap.get(4),
            cap.get(5),
            cap.get(6),
            cap.get(7),
            cap.get(8),
            cap.get(9),
        );
        match groups {
            (
                Some(remote_addr),
                Some(remote_user),
                Some(time_local),
                Some(request),
                Some(status),
                Some(body_bytes_sent),
                Some(http_referer),
                Some(http_user_agent),
            ) => Some(Log {
                remote_addr: remote_addr.as_str(),
                remote_user: remote_user.as_str(),
                time_local: time_local.as_str(),
                request: request.as_str(),
                status: status.as_str(),
                body_bytes_sent: body_bytes_sent.as_str(),
                http_referer: http_referer.as_str(),
                http_user_agent: http_user_agent.as_str(),
            }),
            _ => None,
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_get_log_filenames_sort_reverse() {
        let filenames = vec![
            "foo.txt",
            "access.log",
            "access.log.5",
            "access.log.2",
            "access.log.10",
            "access.log.1",
        ];
        assert_eq!(
            vec![
                "access.log.10",
                "access.log.5",
                "access.log.2",
                "access.log.1",
                "access.log",
            ],
            get_log_filenames_sort_reverse(&filenames)
        );
    }

    //https://docs.rs/csv/latest/csv/struct.WriterBuilder.html#example-with-headers
    #[test]
    fn test_export_to_csv_escapes_comma() -> Result<(), Box<dyn Error>> {
        let mut wtr = get_csv_writer_builder()
            .has_headers(false)
            .from_writer(vec![]);
        wtr.serialize(Log {
            remote_addr: "foo",
            remote_user: "foo",
            time_local: "foo",
            request: "foo, bar",
            status: "foo",
            body_bytes_sent: "foo",
            http_referer: "foo",
            http_user_agent: "foo",
        })?;
        let data = String::from_utf8(wtr.into_inner()?)?;
        assert_eq!(data, "foo,foo,foo,\"foo, bar\",foo,foo,foo,foo\n");
        Ok(())
    }

    #[test]
    fn test_get_log_for_parsed_log() {
        assert_eq!(
            Some(Log{
                remote_addr: "8.8.8.8",
                remote_user: "-",
                time_local: "28/Oct/2021:00:18:22 +0100",
                request: "GET / HTTP/1.1",
                status: "200",
                body_bytes_sent: "77",
                http_referer: "-",
                http_user_agent: "foo bar 1"}
                ),
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100] \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }

    #[test]
    fn test_get_log_for_not_parsed_log() {
        assert_eq!(
            None,
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100 \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }
}