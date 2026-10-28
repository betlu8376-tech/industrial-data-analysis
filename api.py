
from run_sql2 import DATABASE_PATH,PROJECT_ROOT,execute_query

from pydantic import BaseModel,Field
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
    total_count: int=Field(gt=0)
    failure_count: int=Field(ge=0)

class FailureRateResponse(BaseModel):
    failure_rate_percent: float


@app.post("/failure-rate",response_model=FailureRateResponse)


def calculate_failure_rate(data: FailureRateRequest) -> FailureRateResponse:
    if data.total_count < data.failure_count:
        raise HTTPException(status_code=422, detail="failure_count cannot exceed total_count")

    rate=round(100.0*data.failure_count/data.total_count,2)
    return FailureRateResponse(failure_rate_percent=rate)


class ProductTypeSummaryResponse(BaseModel):
    product_type:str
    total_count: int=Field(gt=0)
    failure_count: int=Field(ge=0)
    failure_rate_percent: float


def load_product_type_summary() -> list[dict[str, str | int | float]]:
    sql_path = PROJECT_ROOT / "sql" / "02_failure_by_product_type.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    rn={"total_nums":"total_count","failure_counts":"failure_count"}
    dataframe = dataframe.rename(columns=rn)
    return dataframe.to_dict(orient="records")

@app.get("/failure-by-product-type",response_model=list[ProductTypeSummaryResponse])
def get_failure_by_product_type() -> list[dict[str, str | int | float]]:
    result = load_product_type_summary()
    return result

class ProductWearSummaryResponse(BaseModel):
    tool_wear_group:str
    total_count: int=Field(gt=0)
    failure_count: int=Field(ge=0)
    failure_rate_percent: float

def load_product_wear_summary() -> list[dict[str, str | int | float]]:
    sql_path=PROJECT_ROOT / "sql" / "05_failure_by_tool_wear.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    rn={"total_nums":"total_count","failure_counts":"failure_count"}
    dataframe = dataframe.rename(columns=rn)
    return dataframe.to_dict(orient="records")

@app.get("/failure-by-tool-wear",response_model=list[ProductWearSummaryResponse])
def get_failure_by_tool_wear() -> list[dict[str, str | int | float]]:
    result = load_product_wear_summary()
    return result


class ProductTorqueSummaryResponse(BaseModel):
    torque_nm_group:str
    total_count: int=Field(gt=0)
    failure_count: int=Field(ge=0)
    failure_rate_percent: float

def load_product_torque_summary() -> list[dict[str, str | int | float]]:
    sql_path=PROJECT_ROOT / "sql" / "06_failure_by_torque.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    rn={"total_nums":"total_count","failure_counts":"failure_count"}
    dataframe = dataframe.rename(columns=rn)
    return dataframe.to_dict(orient="records")

@app.get("/failure-by-torque",response_model=list[ProductTorqueSummaryResponse ])
def get_failure_by_torque() -> list[dict[str, str | int | float]]:
    result = load_product_torque_summary()
    return result