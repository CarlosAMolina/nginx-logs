use csv::Writer;
use std::error::Error;
use std::fs::File;
use std::io::{BufWriter, Write};

use crate::m_log::Log;

pub fn write_to_file_error(
    line: String,
    writer: &mut BufWriter<File>,
) -> Result<(), Box<dyn Error>> {
    eprintln!("Not parsed: {}", line);
    write_line_to_file(line, writer)?;
    Ok(())
}

fn write_line_to_file(line: String, writer: &mut BufWriter<File>) -> Result<(), String> {
    if let Err(e) = writer.write_all(format!("{}\n", line).as_bytes()) {
        return Err(e.to_string());
    }
    Ok(())
}

pub fn write_to_file_result(line: Log, writer: &mut Writer<File>) -> Result<(), Box<dyn Error>> {
    writer.serialize(line)?;
    Ok(())
}
