from pathlib import Path
from typing import Dict, Iterator, List, Tuple


class FilenamesFilter:
    def get_pathnames_to_analyze(self, pathname: str) -> Iterator[str]:
        path = Path(pathname)
        if path.is_file():
            yield str(path)
        elif path.is_dir():
            for filename in self._get_filenames_to_analyze_in_path(path):
                yield str(path.joinpath(filename))
        else:
            raise TypeError(f"Pathname {pathname}")

    def _get_filenames_to_analyze_in_path(self, path: Path) -> List[str]:
        filenames = [file_path.name for file_path in path.glob("*")]
        return self._get_log_filenames_sort_reverse(filenames)

    def _get_log_filenames_sort_reverse(self, filenames: List[str]) -> List[str]:
        filenames_with_logs = self._get_filenames_with_logs(filenames)
        numbers_and_log_filenames = self._get_numbers_and_filenames(filenames_with_logs)
        return self._get_filenames_sorted(numbers_and_log_filenames)

    def _get_filenames_with_logs(self, filenames: List[str]) -> List[str]:
        return [filename for filename in filenames if filename.startswith("access.log")]

    def _get_numbers_and_filenames(self, filenames: List[str]) -> Dict[int, str]:
        result = {}
        for filename in filenames:
            possible_number = self._get_filename_possible_number(filename)
            try:
                number = int(possible_number)
                result.update({number: filename})
            except ValueError:
                pass
        return result

    def _get_filename_possible_number(self, filename: str) -> str:
        if filename == "access.log":
            return "0"
        else:
            number_index = -2 if filename.endswith(".gz") else -1
            return filename.split(".")[number_index]

    def _get_filenames_sorted(self, numbers_and_filenames: Dict[int, str]) -> List[str]:
        numbers_and_log_filenames_sorted: List[Tuple[int, str]] = sorted(
            numbers_and_filenames.items(), reverse=True
        )
        return [
            number_and_filename[1]
            for number_and_filename in numbers_and_log_filenames_sorted
        ]
