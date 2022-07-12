use std::env;
use std::error::Error;
use std::fs;
use std::io::Error as IoError;
use std::path::Path;

mod create_file;
mod m_log;
mod read_file;
mod write_file;

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
            .collect::<Result<Vec<_>,IoError>>()?;
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

}
