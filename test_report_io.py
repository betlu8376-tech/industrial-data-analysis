from pathlib import Path
from report_schema import FailureReport
import json
from report_io import save_report



def test_save_report_writes_json(tmp_path: Path) -> None:
    report=FailureReport(total_count=100,
                         failure_count=10,
                         failure_rate_percent=10,
                         conclusion="共统计 100 条记录，其中故障记录为 10 条，故障率为 10%。"
                         )
    output_path = tmp_path / "nested" / "failure_report.json"
    save_report(report, output_path)
    assert output_path.is_file()

    with output_path.open("r",encoding="utf-8") as file:
        save_data = json.load(file)
        assert save_data["total_count"] == 100
        assert save_data["failure_count"] == 10
        assert save_data["failure_rate_percent"] == 10
        assert save_data["conclusion"]=="共统计 100 条记录，其中故障记录为 10 条，故障率为 10%。"

