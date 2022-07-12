use csv::Writer;
use std::error::Error;
use std::fs::File;
use std::io::{BufWriter, Write};

use crate::m_log::Log;

pub fn write_to_file_error(
    line: String,
    file_error: &mut BufWriter<File>,
) -> Result<(), Box<dyn Error>> {
    eprintln!("Not parsed: {}", line);
    write_line_to_file(file_error, line)?;
    Ok(())
}

fn write_line_to_file(file_error: &mut BufWriter<File>, line: String) -> Result<(), String> {
    if let Err(e) = file_error.write_all(format!("{}\n", line).as_bytes()) {
        return Err(e.to_string());
    }
    Ok(())
}

pub fn write_to_file_result(
    line: Log,
    writer_csv: &mut Writer<File>,
) -> Result<(), Box<dyn Error>> {
    writer_csv.serialize(line)?;
    Ok(())
}
