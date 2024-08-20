from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success() -> dict:
    response = client.post("/api/login", data={"username": "admin", "password": "presale"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_write_success():
    login_resp = client.post("/api/login", data={"username": "admin", "password": "presale"})
    assert login_resp.status_code == 200

    token = login_resp.json()["access_token"]
    token_type = login_resp.json()["token_type"]
    data = {
              "data": {
                "to_write": {"k1": 4, "k2": "SS"}
              },
              "token": {
                "access_token": token,
                "token_type": token_type
              }
            }
    response = client.post("/api/write", data=data)

    assert response.status_code == 200
