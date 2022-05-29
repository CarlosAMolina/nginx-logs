use std::env;
use std::error::Error;
use std::fmt;
use std::fs::File;
use std::io::Write;
use std::io::{self, BufRead};
use std::path::Path;

use lazy_static::lazy_static;
use regex::Regex;

pub struct Config {
    filename: String,
}

impl Config {
    pub fn new(mut args: env::Args) -> Result<Config, &'static str> {
        println!("Arguments: {:?}", args);
        args.next();
        let filename = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a file name"),
        };
        println!("Filename: {}", filename);

        Ok(Config { filename })
    }
}

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

struct WritableFile<'a> {
    display: &'a std::path::Display<'a>,
    file: &'a mut std::fs::File, 
}

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let filename = format!("{}.csv", config.filename);
    let path = &Path::new(&filename);
    let display = path.display();
    // https://doc.rust-lang.org/rust-by-example/std_misc/file/create.html
    let mut file = get_new_file(path, &display)?;
    let mut file_csv = WritableFile {
        display: &display,
        file: &mut file,
    };
    println!("File with logs as csv: {}", file_csv.display);
    let filename = format!("{}.error.txt", config.filename);
    let path = Path::new(&filename);
    let display = path.display();
    let mut file = get_new_file(path, &display)?;
    let mut file_not_parsed = WritableFile {
        display: &display,
        file: &mut file,
    };
    println!("File with not parsed logs: {}", file_not_parsed.display);
    let lines = read_lines(config.filename).expect("Something went wrong reading the file");
    lazy_static! {
        static ref RE: Regex = Regex::new(
            r#"(?x)
          (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) # IPv4
          \s-\s
          (.+)                                 # Remote user
          \s\[
          (.+)                                 # Time local
          \]\s"
          (.+)                                 # Request
          "\s
          (\d{1,3})                            # Status
          \s
          (\d+)                                # Body bytes sent
          \s"
          (.+)                                 # HTTP referer
          "\s"
          (.+)                                 # HTTP user agent
          "
        "#,
        )
        .unwrap();
    }
    let csv_headers = "remote_addr,remote_user,time_local,request,status,body_bytes_sent,http_referer,http_user_agent".to_string();
    write_line_to_file(&mut file_csv, csv_headers)?;
    for line in lines {
        let log_line = line.expect("Something went wrong reading the line");
        let log = get_log(&log_line, &RE).map(|m| m.to_string());
        match log {
            None => {
                eprintln!("Not parsed: {}", log_line);
                write_line_to_file(&mut file_not_parsed, log_line)?;
            }
            Some(log_csv) => {
                write_line_to_file(&mut file_csv, log_csv)?;
            }
        }
    }
    Ok(())
}

fn get_new_file(path: &std::path::Path, display: &std::path::Display) -> Result<std::fs::File, String> {
    let file = match File::create(&path) {
        Err(why) => return Err(format!("couldn't create {}: {}", display, why)),
        Ok(file) => file,
    };
    Ok(file)
}

fn write_line_to_file(file: &mut WritableFile, line: String) -> Result<(), String> {
    if let Err(e) = file.file.write_all(line.as_bytes()) {
        return Err(format!("couldn't write to {}: {}", file.display, e.to_string()))
    }
    if let Err(e) = file.file.write_all(b"\n") {
        return Err(e.to_string())
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

fn get_log<'a>(text: &'a str, re: &'a Regex) -> Option<Log<'a>> {
    re.captures(text).and_then(|cap| {
        let groups = (
            cap.get(1),
            cap.get(2),
            cap.get(3),
            cap.get(4),
            cap.get(5),
            cap.get(6),
            cap.get(7),
            cap.get(8),
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
