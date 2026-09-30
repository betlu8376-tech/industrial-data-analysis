from fastapi.testclient import TestClient
from api import app

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
