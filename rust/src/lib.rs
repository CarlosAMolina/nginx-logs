use std::env;
use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::io::{self, BufRead};
use std::path::Path;

use flate2::read::GzDecoder;

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
    let (mut writer_csv, mut file_error) = mod_files::get_result_files(&config.file_or_path)?;

    // TODO move to a method
    //https://stackoverflow.com/questions/36088116/how-to-do-polymorphic-io-from-either-a-file-or-stdin-in-rust
    let file_str = "/tmp/logs/access.log";
    let file = File::open(file_str).unwrap();
    let reader: Box<dyn BufRead> = match file_str.ends_with(".gz") {
        true => Box::new(io::BufReader::new(GzDecoder::new(file))),
        false => Box::new(io::BufReader::new(file))
    };
    for line in reader.lines() {
        println!("{:?}", line);
    }


    let filenames = mod_filenames::get_filenames_to_analyze(&config.file_or_path)?;
    for filename in filenames {
        file_export::export_file_to_csv(&filename, &mut writer_csv, &mut file_error)?;
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

mod mod_files {
    use super::*;
    use std::error::Error;

    use csv::WriterBuilder;

    pub fn get_result_files(
        path: &str,
    ) -> Result<(csv::Writer<std::fs::File>, io::BufWriter<std::fs::File>), Box<dyn Error>> {
        let file_or_path_to_check = Path::new(path);
        let (path_csv, path_error) = get_paths_to_work_with(file_or_path_to_check);
        println!("File with logs as csv: {}", path_csv.display());
        println!("File with not parsed logs: {}", path_error.display());
        //https://docs.rs/csv/latest/csv/tutorial/index.html#writing-csv
        let writer_csv = get_csv_writer_builder().from_path(&path_csv)?;
        // https://doc.rust-lang.org/rust-by-example/std_misc/file/create.html
        let file_error = mod_files::get_new_file(&path_error)?;
        Ok((writer_csv, file_error))
    }

    fn get_paths_to_work_with(
        file_or_path_to_check: &std::path::Path,
    ) -> (std::path::PathBuf, std::path::PathBuf) {
        let path_to_check = match file_or_path_to_check.is_file() {
            true => file_or_path_to_check.parent().unwrap(),
            false => file_or_path_to_check,
        };
        (
            path_to_check.join("result.csv"),
            path_to_check.join("error.txt"),
        )
    }

    fn get_csv_writer_builder() -> WriterBuilder {
        WriterBuilder::new()
    }

    fn get_new_file(path: &std::path::Path) -> Result<io::BufWriter<std::fs::File>, String> {
        let file = match File::create(&path) {
            Err(why) => return Err(format!("couldn't create {}: {}", path.display(), why)),
            Ok(file) => file,
        };
        Ok(io::BufWriter::new(file))
    }
}

mod mod_filenames {
    use super::*;

    use std::collections::HashMap;

    pub fn get_filenames_to_analyze(
        file_or_path_to_check: &str,
    ) -> Result<Vec<String>, Box<dyn Error>> {
        let file_or_path = Path::new(file_or_path_to_check);
        if file_or_path.is_file() {
            Ok(vec![file_or_path_to_check.to_string()])
        } else {
            let filenames = get_filenames_to_analyze_in_path(file_or_path_to_check)?;
            let mut result = Vec::new();
            for filename in filenames {
                result.push(file_or_path.join(filename).to_str().unwrap().to_string());
            }
            Ok(result)
        }
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

mod file_export {
    use super::*;

    use csv::Writer;
    use flate2::read::GzDecoder;

    pub enum ReaderGzOrPlain<S, T> {
        ReaderGz(S),
        ReaderPlain(T),
    }

    //) -> Result<io::Lines<Box<dyn io::Read>>, Box<dyn Error>>
    //) -> Result<io::Lines<io::BufReader<std::fs::File>>, Box<dyn Error>>
    // https://stackoverflow.com/questions/33390395/can-a-function-return-different-types-depending-on-conditional-statements-in-the
    // https://users.rust-lang.org/t/return-different-types/51534
    // TODO continue here
    pub fn get_file_lines_b(
        file_str: &str,
    ) -> ReaderGzOrPlain<io::BufReader<flate2::read::GzDecoder<File>>, io::BufReader<std::fs::File>> {
        println!("Init file: {}", file_str);
        let file = File::open(file_str).unwrap();
        if file_str.ends_with(".gz") {
            return ReaderGzOrPlain::ReaderGz(io::BufReader::new(GzDecoder::new(file)));
        }
        //ReaderGzOrPlain::ReaderPlain(io::BufReader::new(file))
        ReaderGzOrPlain::ReaderGz(io::BufReader::new(GzDecoder::new(file)))
    }

    pub fn export_file_to_csv(
        file: &str,
        writer_csv: &mut Writer<File>,
        file_error: &mut io::BufWriter<std::fs::File>,
    ) -> Result<(), Box<dyn Error>> {
        println!("Init file: {}", file);
        if file.ends_with(".gz") {
            let lines = get_file_lines(file, read_gz_lines)?;
            export_lines_to_file(lines, writer_csv, file_error)?;
        } else {
            let lines = get_file_lines(file, read_log_lines)?;
            export_lines_to_file(lines, writer_csv, file_error)?;
        };
        writer_csv.flush()?;
        Ok(())
    }

    fn get_file_lines<R>(
        file: &str,
        lines_reader: fn(File) -> io::Result<io::Lines<io::BufReader<R>>>,
    ) -> Result<io::Lines<io::BufReader<R>>, Box<dyn Error>>
    where
        R: io::Read,
    {
        let file = File::open(file)?;
        Ok(lines_reader(file).expect("Something went wrong reading the file"))
    }

    // https://doc.rust-lang.org/rust-by-example/std_misc/file/read_lines.html
    fn read_log_lines(file: File) -> io::Result<io::Lines<io::BufReader<File>>> {
        Ok(io::BufReader::new(file).lines())
    }
    fn read_gz_lines(
        file: File,
    ) -> io::Result<io::Lines<io::BufReader<flate2::read::GzDecoder<File>>>> {
        Ok(io::BufReader::new(GzDecoder::new(file)).lines())
    }

    fn export_lines_to_file<R>(
        lines: io::Lines<io::BufReader<R>>,
        writer_csv: &mut Writer<File>,
        file_error: &mut io::BufWriter<std::fs::File>,
    ) -> Result<(), Box<dyn Error>>
    where
        R: io::Read,
    {
        for line in lines {
            export_line_to_file(line, writer_csv, file_error)?;
        }
        Ok(())
    }

    fn export_line_to_file(
        line: Result<String, io::Error>,
        writer_csv: &mut Writer<File>,
        file_error: &mut io::BufWriter<std::fs::File>,
    ) -> Result<(), Box<dyn Error>> {
        let log_line = line.expect("Something went wrong reading the line");
        let log = m_log::get_log(&log_line);
        match log {
            None => {
                eprintln!("Not parsed: {}", log_line);
                write_line_to_file(file_error, log_line.to_string())?;
            }
            Some(log_csv) => {
                writer_csv.serialize(log_csv)?;
            }
        }
        Ok(())
    }

    fn write_line_to_file(
        file_error: &mut io::BufWriter<std::fs::File>,
        line: String,
    ) -> Result<(), String> {
        if let Err(e) = file_error.write_all(format!("{}\n", line).as_bytes()) {
            return Err(e.to_string());
        }
        Ok(())
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
