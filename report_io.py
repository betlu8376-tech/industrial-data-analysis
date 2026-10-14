from pathlib import Path
from report_schema import FailureReport
import json


def save_report(report: FailureReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text=report.model_dump_json(indent=2)
    with output_path.open("w",encoding="utf-8") as file:
        file.write(text)