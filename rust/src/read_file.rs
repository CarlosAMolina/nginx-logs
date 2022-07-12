use std::fs::File;
use std::io::{BufRead, BufReader, Lines};


use flate2::read::GzDecoder;


pub fn get_lines_in_file(file_str: &str) -> Lines<Box<dyn BufRead>> {
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
        true => Box::new(BufReader::new(GzDecoder::new(file))),
        false => Box::new(BufReader::new(file))
    };
    result
}
