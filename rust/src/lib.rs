use std::env;
use std::error::Error;

mod create_file;
mod filter_file;
mod m_log;
mod read_file;
mod write_file;

pub struct Config {
    pathname: String,
}

impl Config {
    pub fn new(mut args: env::Args) -> Result<Config, &'static str> {
        //println!("Arguments: {:?}", args);
        args.next();
        let pathname = match args.next() {
            Some(arg) => arg,
            None => return Err("No pathname provided"),
        };
        println!("Checking: {}", pathname);

        Ok(Config { pathname })
    }
}

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let (mut writer_csv, mut writer_error) = create_file::get_result_writers(&config.pathname)?;
    for pathname in filter_file::get_pathnames_to_analyze(&config.pathname)? {
        //for line in reader.lines() {
        for line in read_file::get_lines_in_pathname(&pathname) {
            let line_str = line.expect("Something went wrong reading the line");
            let log = m_log::get_log(&line_str);
            match log {
                Some(log_csv) => {
                    write_file::write_to_file_result(log_csv, &mut writer_csv)?;
                }
                None => {
                    write_file::write_to_file_error(line_str, &mut writer_error)?;
                }
            }
        }
    }
    writer_csv.flush()?;
    Ok(())
}
