use std::env;
use std::process;
use std::time::Instant;

use nginx_logs::Config;

fn main() {
    //https://rust-lang-nursery.github.io/rust-cookbook/datetime/duration.html#measure-the-elapsed-time-between-two-code-sections
    let start = Instant::now();
    let config = Config::new(env::args()).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {}", err);
        process::exit(1);
    });
    if let Err(e) = nginx_logs::run(config) {
        eprintln!("Application error: {}", e);
        process::exit(1);
    }
    let duration = start.elapsed();
    println!("Time elapsed: {:?}", duration);
}
