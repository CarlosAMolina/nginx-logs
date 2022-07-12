use std::error::Error;
use std::fs::File;
use std::io;
use std::path::Path;

use csv::WriterBuilder;

pub fn get_result_files(
    path: &str,
) -> Result<(csv::Writer<std::fs::File>, io::BufWriter<std::fs::File>), Box<dyn Error>> {
    let file_or_path_to_check = Path::new(path);
    let (path_csv, path_error) = get_paths_to_work_with(file_or_path_to_check);
    println!("File with logs as csv: {}", path_csv.display());
    println!("File with not parsed logs: {}", path_error.display());
    let writer_csv = get_csv_writer_builder().from_path(&path_csv)?;
    let file_error = get_new_file(&path_error)?;
    Ok((writer_csv, file_error))
}

fn get_paths_to_work_with(
    file_or_path_to_check: &std::path::Path,
) -> (std::path::PathBuf, std::path::PathBuf) {
    let path_to_check = match file_or_path_to_check.is_file() {
        true => file_or_path_to_check.parent().unwrap(),
        false => file_or_path_to_check,
    };
    (
        path_to_check.join("result.csv"),
        path_to_check.join("error.txt"),
    )
}

//https://docs.rs/csv/latest/csv/tutorial/index.html#writing-csv
fn get_csv_writer_builder() -> WriterBuilder {
    WriterBuilder::new()
}

// https://doc.rust-lang.org/rust-by-example/std_misc/file/create.html
fn get_new_file(path: &std::path::Path) -> Result<io::BufWriter<std::fs::File>, String> {
    let file = match File::create(&path) {
        Err(why) => return Err(format!("couldn't create {}: {}", path.display(), why)),
        Ok(file) => file,
    };
    Ok(io::BufWriter::new(file))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::m_log::Log;

    //https://docs.rs/csv/latest/csv/struct.WriterBuilder.html#example-with-headers
    #[test]
    fn test_export_to_csv_escapes_comma() -> Result<(), Box<dyn Error>> {
        let mut wtr = get_csv_writer_builder()
            .has_headers(false)
            .from_writer(vec![]);
        wtr.serialize(Log {
            remote_addr: "foo",
            remote_user: "foo",
            time_local: "foo",
            request: "foo, bar",
            status: "foo",
            body_bytes_sent: "foo",
            http_referer: "foo",
            http_user_agent: "foo",
        })?;
        let data = String::from_utf8(wtr.into_inner()?)?;
        assert_eq!(data, "foo,foo,foo,\"foo, bar\",foo,foo,foo,foo\n");
        Ok(())
    }

}
