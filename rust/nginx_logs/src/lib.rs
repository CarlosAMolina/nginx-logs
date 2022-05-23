use std::error::Error;
use std::fs;

pub struct Config {
    filename: String,
}

impl Config {
    pub fn new(args: &[String]) -> Result<Config, &'static str> {
        println!("Arguments: {:?}", args);
        if args.len() < 2 {
            return Err("not enough arguments");
        }
        let filename = args[1].clone();
        println!("Filename: {}", filename);

        Ok(Config{filename})
    }
}

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.filename)
        .expect("Something went wrong reading the file");

    println!("File content:\n{}", contents);
    Ok(())
}
