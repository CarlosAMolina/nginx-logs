use std::error::Error;
use std::fs::File;
use std::io::BufWriter;
use std::path::{Path, PathBuf};

use csv::WriterBuilder;

pub fn get_result_writers(
    pathname: &str,
) -> Result<(csv::Writer<File>, BufWriter<File>), Box<dyn Error>> {
    let path = Path::new(pathname);
    let (path_csv, path_error) = get_paths_to_work_with(path);
    println!("File with logs as csv: {}", path_csv.display());
    println!("File with not parsed logs: {}", path_error.display());
    let writer_csv = get_csv_writer().from_path(&path_csv)?;
    let file_error = get_file_writer(&path_error)?;
    Ok((writer_csv, file_error))
}

fn get_paths_to_work_with(path: &Path) -> (PathBuf, PathBuf) {
    let path_without_filename = match path.is_file() {
        true => path.parent().unwrap(),
        false => path,
    };
    (
        path_without_filename.join("result.csv"),
        path_without_filename.join("error.txt"),
    )
}

//https://docs.rs/csv/latest/csv/tutorial/index.html#writing-csv
fn get_csv_writer() -> WriterBuilder {
    WriterBuilder::new()
}

// https://doc.rust-lang.org/rust-by-example/std_misc/file/create.html
fn get_file_writer(path: &Path) -> Result<BufWriter<File>, String> {
    let file = match File::create(&path) {
        Err(why) => return Err(format!("couldn't create {}: {}", path.display(), why)),
        Ok(file) => file,
    };
    Ok(BufWriter::new(file))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::m_log::Log;

    //https://docs.rs/csv/latest/csv/struct.WriterBuilder.html#example-with-headers
    #[test]
    fn test_export_to_csv_escapes_comma() -> Result<(), Box<dyn Error>> {
        let mut wtr = get_csv_writer()
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
