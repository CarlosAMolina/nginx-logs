use std::env;
use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::io::{self, BufRead};
use std::path::Path;

mod m_log;

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
    let (mut writer_csv, mut file_error) = create_file::get_result_files(&config.file_or_path)?;
    for filename in filter_file::get_filenames_to_analyze(&config.file_or_path)?{
        //for line in reader.lines() {
        for line in read_file::get_lines_in_file(&filename) {
            let line_str = line.expect("Something went wrong reading the line");
            let log = m_log::get_log(&line_str);
            match log {
                None => {
                    write_file::write_to_file_error(line_str, &mut file_error)?;
                }
                Some(log_csv) => {
                    write_file::write_to_file_result(log_csv, &mut writer_csv)?;
                }
            }
        }
    }
    writer_csv.flush()?;
    Ok(())
}

mod create_file {
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
        let file_error = get_new_file(&path_error)?;
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

mod filter_file {
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

mod read_file {
    use super::*;

    use flate2::read::GzDecoder;


    pub fn get_lines_in_file(file_str: &str) -> io::Lines<Box<dyn BufRead>> {
        let reader = get_file_reader(file_str);
        reader.lines()
    }

    // https://stackoverflow.com/questions/36088116/how-to-do-polymorphic-io-from-either-a-file-or-stdin-in-rust
    fn get_file_reader(
        file_str: &str,
    ) -> Box<dyn BufRead>{
        println!("Init file: {}", file_str);
        let file = File::open(file_str).unwrap();
        let result: Box<dyn BufRead> = match file_str.ends_with(".gz") {
            true => Box::new(io::BufReader::new(GzDecoder::new(file))),
            false => Box::new(io::BufReader::new(file))
        };
        result
    }
}


mod write_file {
    use super::*;

    use csv::Writer;


    pub fn write_to_file_error(
        line: String,
        file_error: &mut io::BufWriter<std::fs::File>,
    ) -> Result<(), Box<dyn Error>> {
        eprintln!("Not parsed: {}", line);
        write_line_to_file(file_error, line)?;
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

    pub fn write_to_file_result(
        line: m_log::Log,
        writer_csv: &mut Writer<File>,
    ) -> Result<(), Box<dyn Error>> {
        writer_csv.serialize(line)?;
        Ok(())
    }


}

// TODO test private functions
#[cfg(test)]
mod tests {
    use super::*;
    use crate::m_log::Log;
    use crate::filter_file;

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
            filter_file::get_log_filenames_sort_reverse(&filenames)
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

}
