use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::io::Error as IoError;
use std::path::Path;

pub fn get_pathnames_to_analyze(
    pathname: &str,
) -> Result<Vec<String>, Box<dyn Error>> {
    let path = Path::new(pathname);
    if path.is_file() {
        Ok(vec![pathname.to_string()])
    } else {
        let filenames = get_filenames_to_analyze_in_directory(pathname)?;
        let mut result = Vec::new();
        for filename in filenames {
            result.push(path.join(filename).to_str().unwrap().to_string());
        }
        Ok(result)
    }
}

fn get_filenames_to_analyze_in_directory(pathname: &str) -> Result<Vec<String>, Box<dyn Error>> {
    //https://doc.rust-lang.org/std/fs/fn.read_dir.html
    let entries = fs::read_dir(pathname)?
        .map(|res| res.map(|e| e.path()))
        .collect::<Result<Vec<_>, IoError>>()?;
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

#[cfg(test)]
mod tests {
    use super::*;

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
            get_log_filenames_sort_reverse(&filenames)
        );
    }
}
