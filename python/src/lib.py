import argparse

from filter_file import FilenamesFilter
from read_file import FileReader
import create_file
import m_log
import write_file


def get_args_parsed():
    # https://docs.python.org/3/library/argparse.html#the-add-argument-method
    parser = argparse.ArgumentParser(description="Export Nginx logs to a csv file.")
    parser.add_argument(
        "pathname",
        type=str,
        help="path to a folder with the log files or to an specific file",
    )
    return parser.parse_args()


def run(args):
    print(f"Checking: {args.pathname}")
    pathname_csv, pathname_error = create_file.get_pathnames_to_work_with(args.pathname)
    with open(pathname_csv, "w") as file_csv, open(pathname_error, "w") as file_error:
        writer_csv = create_file.get_csv_writer(file_csv)
        writer_csv.writeheader()
        for pathname in FilenamesFilter().get_pathnames_to_analyze(args.pathname):
            for line in FileReader().get_lines_in_pathname(pathname):
                if len(line) != 0:
                    log = m_log.get_log(line)
                    if log is None:
                        write_file.write_to_file_error(line, file_error)
                    else:
                        write_file.write_to_file_result(log, writer_csv)
