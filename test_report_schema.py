from report_schema import FailureReport
import pytest
from pydantic import BaseModel, ValidationError,model_validator




def test_report_accepts_valid_json()-> None:
    raw_json='''{
    "total_count": 10000,
    "failure_count": 339,
    "failure_rate_percent": 3.39,
    "conclusion":"共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"
}'''
    report=FailureReport.model_validate_json(raw_json)
    assert report.total_count==10000
    assert report.failure_count==339
    assert report.failure_rate_percent==3.39
    assert report.conclusion=="共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"


def test_report_accepts_zero_failure()-> None:
    raw_json = '''{
        "total_count": 10000,
        "failure_count": 0,
        "failure_rate_percent": 0,
        "conclusion":"共统计 10000 条记录，其中故障记录为 0 条，故障率为 0%。"
    }'''
    report=FailureReport.model_validate_json(raw_json)

    assert report.failure_count==0
    assert report.failure_rate_percent==0



def test_report_rejects_negative_failure_count()-> None:
    raw_json = '''{
        "total_count": 10000,
        "failure_count": -1,
        "failure_rate_percent": 3.39,
        "conclusion":"共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"
    }'''
    with pytest.raises(ValidationError, match="failure_count"):
        report=FailureReport.model_validate_json(raw_json)



def test_report_rejects_failure_count_above_total()-> None:
    raw_json = '''{
            "total_count": 100,
            "failure_count":101 ,
            "failure_rate_percent": 3.39,
            "conclusion":"共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"
    }'''
    with pytest.raises(ValueError
            , match="failure_count can not exceed total"):
        report=FailureReport.model_validate_json(raw_json)


def test_report_rejects_inconsistent_rate() -> None:
    raw_json = '''{
                "total_count": 100,
                "failure_count":30 ,
                "failure_rate_percent": 60,
                "conclusion":"共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"
    }'''
    with pytest.raises(ValueError, match="failure_rate_percent does not match counts"):
        report=FailureReport.model_validate_json(raw_json)




def test_report_accepts_rounded_rate() -> None:
    raw_json = '''{
                    "total_count": 3,
                    "failure_count":1 ,
                    "failure_rate_percent": 33.33,
                    "conclusion":"共统计 10000 条记录，其中故障记录为 339 条，故障率为 3.39%。"
    }'''
    report=FailureReport.model_validate_json(raw_json)
    assert report.failure_rate_percent==33.33