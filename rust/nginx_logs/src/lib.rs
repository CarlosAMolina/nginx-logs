use std::env;
use std::error::Error;

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

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

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let lines = read_lines(config.filename).expect("Something went wrong reading the file");
    for line in lines {
        let log = line.expect("Something went wrong reading the line");
        println!("{}", log);
    }
    //println!("Matches:");
    //// TODO
    //for line in contents.lines() {
    //    println!("Checking: {}", line);
    //    if !line.contains("111") {
    //        eprintln!("Not parsed {}", line);
    //    }
    //}
    //for line in search("111", &contents) {
    //    println!("{}", line);
    //}

    //println!("File content:\n{}", contents);
    Ok(())
}

// https://doc.rust-lang.org/rust-by-example/std_misc/file/read_lines.html
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents
        .lines()
        .filter(|line| line.contains(query))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_result() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.";

        assert_eq!(vec!["safe, fast, productive."], search(query, contents));
    }
}
