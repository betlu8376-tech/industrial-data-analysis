from run_sql2 import DATABASE_PATH,PROJECT_ROOT,execute_query

from pydantic import BaseModel
from typing import Annotated
from fastapi import FastAPI, Query,Path,HTTPException

class SummaryResponse(BaseModel):
    total_count: int
    normal_count: int
    failure_count: int
    failure_rate_percent: float
app = FastAPI()


def load_summary() -> dict[str, int | float]:
    sql_path = PROJECT_ROOT / "sql" / "01_failure_summary.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    return dataframe.to_dict(orient="records")[0]


@app.get("/summary",response_model=SummaryResponse)
def get_summary(decimals: Annotated[int, Query(ge=0, le=2)] = 2) -> dict[str,int|float]:
    result = load_summary()
    result["failure_rate_percent"] = round(
        result["failure_rate_percent"], decimals
    )
    return result


@app.get("/summary/{metric_name}")
def get_metric(metric_name: str) -> dict[str,int|float]:
    result = load_summary()
    if metric_name not in result:
        raise HTTPException(status_code=404, detail="Metric not found")
    return {f"{metric_name}": result[metric_name]}

class FailureRateRequest(BaseModel):
    total_count: int
    failure_count: int

class FailureRateResponse(BaseModel):
    failure_rate_percent: float


@app.post("/failure-rate",response_model=FailureRateResponse)


def calculate_failure_rate(data: FailureRateRequest) -> FailureRateResponse:
    rate=round(100.0*data.failure_count/data.total_count,2)
    return FailureRateResponse(failure_rate_percent=rate)
