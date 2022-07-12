use std::env;
use std::error::Error;

mod create_file;
mod filter_file;
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

