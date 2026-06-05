import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login():
    response = client.post("/api/auth/login", data={
        "username": "admin@oasis.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_wonya_test_endpoint():
    login_response = client.post("/api/auth/login", data={
        "username": "admin@oasis.com",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/paiements/wonya/test",
        json={
            "montant": 1500,
            "devise": "CDF",
            "mobilemoney": "ORANGE",
            "execute": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["api_url"] is not None
    assert data["partner_ref"] is not None
    assert data["payload"]["Action"] == "C2B"
    assert data["payload"]["RefPartenaire"] == data["partner_ref"]
