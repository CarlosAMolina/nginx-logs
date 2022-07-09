use std::env;
use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::io::{self, BufRead};
use std::path::Path;

use csv::WriterBuilder;

pub struct Config {
    file_or_path: String,
}

impl Config {
    pub fn new(mut args: env::Args) -> Result<Config, &'static str> {
        //println!("Arguments: {:?}", args);
        args.next();
        let file_or_path = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a file name or a path"),
        };
        println!("Checking: {}", file_or_path);

        Ok(Config { file_or_path })
    }
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
        file_export::export_file_to_csv(
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
            file_export::export_file_to_csv(
                &file_str,
                &mut writer_csv,
                &mut file_and_display_error,
            )?;
        }
    }
    Ok(())
}

mod m_log {
    use std::fmt;

    use serde_derive::Serialize;

    #[derive(Debug, PartialEq, Serialize)]
    pub struct Log<'a> {
        pub remote_addr: &'a str,
        pub remote_user: &'a str,
        pub time_local: &'a str,
        pub request: &'a str,
        pub status: &'a str,
        pub body_bytes_sent: &'a str,
        pub http_referer: &'a str,
        pub http_user_agent: &'a str,
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

    pub fn get_log(text: &str) -> Option<Log> {
        let mut log_parts_index = vec![0];
        let characters_to_match = vec![
            b' ', b' ', b'[', b']', b'"', b'"', b' ', b' ', b'"', b'"', b'"',
        ];
        let bytes = text.as_bytes();
        let mut match_index = 0;
        for (i, &item) in bytes.iter().enumerate() {
            if item == characters_to_match[match_index] {
                log_parts_index.push(i);
                if match_index < characters_to_match.len() - 1 {
                    match_index += 1;
                }
            }
        }
        if log_parts_index.len() == 13 {
            Some(Log {
                remote_addr: &text[log_parts_index[0]..log_parts_index[1]],
                remote_user: &text[log_parts_index[2] + 1..log_parts_index[3] - 1],
                time_local: &text[log_parts_index[3] + 1..log_parts_index[4]],
                request: &text[log_parts_index[5] + 1..log_parts_index[6]],
                status: &text[log_parts_index[7] + 1..log_parts_index[8]],
                body_bytes_sent: &text[log_parts_index[8] + 1..log_parts_index[9] - 1],
                http_referer: &text[log_parts_index[9] + 1..log_parts_index[10]],
                http_user_agent: &text[log_parts_index[11] + 1..log_parts_index[12]],
            })
        } else {
            None
        }
    }
}

pub struct FileAndDisplay<'a> {
    display: &'a std::path::Display<'a>,
    file: &'a mut io::BufWriter<std::fs::File>,
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
    Ok(mod_filenames::get_log_filenames_sort_reverse(&filenames))
}

mod mod_filenames {
    use std::collections::HashMap;

    pub fn get_log_filenames_sort_reverse(filenames: &[&str]) -> Vec<String> {
        let filenames_with_logs = get_filenames_with_logs(filenames);
        let numbers_and_log_filenames = get_numbers_and_filenames(filenames_with_logs);
        get_filenames_sorted(numbers_and_log_filenames)
    }

    fn get_filenames_with_logs(filenames: &[&str]) -> Vec<String> {
        let mut result = Vec::<String>::new();
        for filename in filenames.iter() {
            if filename.starts_with("access.log") {
                result.push(filename.to_string());
            }
        }
        result
    }

    fn get_numbers_and_filenames(filenames: Vec<String>) -> HashMap<u8, String> {
        let mut result = HashMap::new();
        for filename in filenames {
            let possible_number = get_filename_possible_number(&filename);
            if let Ok(number) = possible_number.parse::<u8>() {
                result.insert(number, filename);
            }
        }
        result
    }

    fn get_filename_possible_number(filename: &str) -> String {
        if filename == "access.log" {
            "0".to_string()
        } else {
            let mut number_index_end = 0;
            if filename.ends_with(".gz") {
                number_index_end = 1;
            }
            filename
                .split('.')
                .nth_back(number_index_end)
                .unwrap()
                .to_string()
        }
    }

    fn get_filenames_sorted(numbers_and_filenames: HashMap<u8, String>) -> Vec<String> {
        let mut numbers = Vec::from_iter(numbers_and_filenames.keys());
        numbers.sort_unstable();
        numbers.reverse();
        let mut result = Vec::new();
        for number in numbers {
            let filename = numbers_and_filenames.get(number).unwrap();
            result.push(filename.clone());
        }
        result
    }
}

fn get_new_file(path: &std::path::Path) -> Result<io::BufWriter<std::fs::File>, String> {
    let file = match File::create(&path) {
        Err(why) => return Err(format!("couldn't create {}: {}", path.display(), why)),
        Ok(file) => file,
    };
    Ok(io::BufWriter::new(file))
}

mod file_export {
    use super::*;
    use std::path::Path;

    use csv::Writer;
    use flate2::read::GzDecoder;

    pub fn export_file_to_csv<P>(
        file: &str,
        writer_csv: &mut Writer<File>,
        file_and_display_error: &mut FileAndDisplay,
    ) -> Result<(), Box<dyn Error>>
    where
        P: AsRef<Path>,
    {
        if file.ends_with(".gz") {
            export_gz_file_to_csv(file, writer_csv, file_and_display_error)?;
        } else {
            export_log_file_to_csv(file, writer_csv, file_and_display_error)?;
        }
        Ok(())
    }

    fn export_log_file_to_csv(
        file: &str,
        writer_csv: &mut Writer<File>,
        file_and_display_error: &mut FileAndDisplay,
    ) -> Result<(), Box<dyn Error>> {
        println!("Init file: {}", file);
        let lines = get_file_lines(file, read_lines);
        for line in lines {
            export_line_to_file(line, writer_csv, file_and_display_error)?;
        }
        writer_csv.flush()?;
        Ok(())
    }

    // TODO reformat code duplicated as export_log_file_to_csv
    fn export_gz_file_to_csv<P>(
        file: &str,
        writer_csv: &mut Writer<File>,
        file_and_display_error: &mut FileAndDisplay,
    ) -> Result<(), Box<dyn Error>>
    where
        P: AsRef<Path>,
    {
        export_file_to_csv_parent(file, read_gz_lines, writer_csv, file_and_display_error)
    }

    fn export_file_to_csv_parent<P, R>(
        file: &str,
        lines_reader: fn(&str) -> io::Result<io::Lines<io::BufReader<R>>>,
        writer_csv: &mut Writer<File>,
        file_and_display_error: &mut FileAndDisplay,
    ) -> Result<(), Box<dyn Error>>
    where
        P: AsRef<Path>,
        R: io::Read,
    {
        println!("Init file: {}", file);
        let lines = get_file_lines(file, lines_reader);
        for line in lines {
            export_line_to_file(line, writer_csv, file_and_display_error)?;
        }
        writer_csv.flush()?;
        Ok(())
    }

    fn get_file_lines<P, R>(
        file: P,
        lines_reader: fn(P) -> io::Result<io::Lines<io::BufReader<R>>>,
    ) -> io::Lines<io::BufReader<R>>
    where
        P: AsRef<Path>,
        R: io::Read,
    {
        lines_reader(file).expect("Something went wrong reading the file")
    }

    fn export_line_to_file(
        line: Result<String, io::Error>,
        writer_csv: &mut Writer<File>,
        file_and_display_error: &mut FileAndDisplay,
    ) -> Result<(), Box<dyn Error>> {
        let log_line = line.expect("Something went wrong reading the line");
        let log = m_log::get_log(&log_line);
        match log {
            None => {
                eprintln!("Not parsed: {}", log_line);
                write_line_to_file(file_and_display_error, log_line.to_string())?;
            }
            Some(log_csv) => {
                writer_csv.serialize(log_csv)?;
            }
        }
        Ok(())
    }

    fn write_line_to_file(
        file_and_display: &mut FileAndDisplay,
        line: String,
    ) -> Result<(), String> {
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

    fn read_gz_lines<P>(
        filename: P,
    ) -> io::Result<io::Lines<io::BufReader<flate2::read::GzDecoder<File>>>>
    where
        P: AsRef<Path>,
    {
        let file = File::open(filename)?;
        Ok(io::BufReader::new(GzDecoder::new(file)).lines())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::m_log::Log;
    use crate::mod_filenames;

    #[test]
    fn test_get_log_filenames_sort_reverse() {
        let filenames = vec![
            "foo.txt",
            "error.log.111",
            "access.log",
            "access.log.5.gz",
            "access.log.2",
            "access.log.10.gz",
            "access.log.1.gz",
        ];
        assert_eq!(
            vec![
                "access.log.10.gz",
                "access.log.5.gz",
                "access.log.2",
                "access.log.1.gz",
                "access.log",
            ],
            mod_filenames::get_log_filenames_sort_reverse(&filenames)
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
            m_log::get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100] \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }

    #[test]
    fn test_get_log_for_not_parsed_log() {
        assert_eq!(
            None,
            m_log::get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100 \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }
}
