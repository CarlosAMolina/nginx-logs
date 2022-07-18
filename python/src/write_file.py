from m_log import Log


def write_to_file_error(line: str, writer):
    print(f"Not parsed: {line}")
    writer.write(f"{line}\n")


def write_to_file_result(log: Log, writer):
    writer.writerow(log.asdict())
