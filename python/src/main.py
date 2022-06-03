import argparse

if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html#the-add-argument-method
    parser = argparse.ArgumentParser(description="Export Nginx logs to a csv file.")
    parser.add_argument(
        "path",
        type=str,
        help="path to a folder with the log files or to an specific file",
    )
    args = parser.parse_args()
    print(f"Checking: {args.path}")
