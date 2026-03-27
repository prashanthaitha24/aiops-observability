from __future__ import annotations

import csv
from pathlib import Path


class TrainingDataWriter:
    def __init__(self, csv_file: Path, fieldnames: list[str]) -> None:
        self.csv_file = csv_file
        self.fieldnames = fieldnames
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)

    def append_row(self, row: dict[str, float]) -> None:
        file_exists = self.csv_file.exists()

        with self.csv_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
