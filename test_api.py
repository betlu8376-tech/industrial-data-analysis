from fastapi.testclient import TestClient
from types_pandas import dataframe_stub

from api import app

import pandas as pd
from unittest.mock import patch

from run_sql2 import DATABASE_PATH, PROJECT_ROOT

client = TestClient(app)



def test_failure_rate_success() -> None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 10000, "failure_count": 339}
    )
    assert response.status_code == 200
    assert response.json() == {
        "failure_rate_percent": 3.39
    }


def test_failure_count_exceeds_total() -> None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 100, "failure_count": 339})
    assert response.status_code == 422
    assert response.json()=={
        "detail": "failure_count cannot exceed total_count"
    }

def test_total_count_zero() -> None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 0, "failure_count": 1}
    )
    assert response.status_code == 422
    # assert response.json() == {}


def test_failure_count_negative() -> None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 100, "failure_count": -1}
    )
    assert response.status_code == 422


def test_failure_count_zero() -> None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 100, "failure_count": 0}
    )
    assert response.status_code == 200
    assert response.json() == {"failure_rate_percent": 0.0}


def test_all_failed() ->None:
    response = client.post(
        "/failure-rate",
        json={"total_count": 100, "failure_count": 100}
    )
    assert response.status_code == 200
    assert response.json() == {"failure_rate_percent": 100.0}


def test_failure_by_product_type_success() -> None:
    dataframe=pd.DataFrame([
        {"product_type":"L","total_nums": 100, "failure_counts": 10,"failure_rate_percent": 10.0},
        {"product_type": "M", "total_nums": 200, "failure_counts": 4, "failure_rate_percent": 2.0},
        {"product_type":"H","total_nums": 50, "failure_counts": 0,"failure_rate_percent": 0.0}
    ])
    with(
    patch("api.execute_query", return_value=dataframe)as mock_query,

    ):
        response=client.get("/failure-by-product-type")
        assert response.status_code == 200
        expected_dataframe=[
            {"product_type": "L","total_count": 100,"failure_count": 10,"failure_rate_percent": 10.0},
            {"product_type": "M", "total_count": 200, "failure_count": 4, "failure_rate_percent": 2.0},
            {"product_type": "H", "total_count": 50, "failure_count": 0, "failure_rate_percent": 0.0},
        ]
        assert response.json() == expected_dataframe
        mock_query.assert_called_once_with(DATABASE_PATH,PROJECT_ROOT / "sql" / "02_failure_by_product_type.sql")


def test_failure_by_product_type_empty()->None:
    dataframe=pd.DataFrame(columns=["product_type","total_nums", "failure_counts","failure_rate_percent"])
    with(
        patch("api.execute_query", return_value=dataframe)as mock_query,

        ):
            response=client.get("/failure-by-product-type")
            assert response.status_code == 200  
            assert response.json() == []
