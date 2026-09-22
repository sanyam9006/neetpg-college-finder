import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_register_and_login_flow():
    # Use unique random email/phone for test isolation
    import random
    rand_id = random.randint(10000, 99999)
    email = f"dr_test_{rand_id}@example.com"
    phone = f"98{rand_id}1234"

    # 1. Register candidate
    reg_payload = {
        "name": f"Dr. Test Candidate {rand_id}",
        "email": email,
        "phone": phone,
        "batch_year": "2021 (Intern)",
        "password": "securepassword123"
    }

    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200, reg_resp.text
    data = reg_resp.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == email
    assert data["user"]["name"] == f"Dr. Test Candidate {rand_id}"
    assert data["user"]["batch_year"] == "2021 (Intern)"
    token = data["user"]["token"]
    assert token is not None

    # 2. Duplicate registration should fail
    dup_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400
    assert "already registered" in dup_resp.json()["detail"]

    # 3. Login with email
    login_payload_email = {
        "email_or_phone": email,
        "password": "securepassword123"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload_email)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["user"]["email"] == email

    # 4. Login with phone
    login_payload_phone = {
        "email_or_phone": phone,
        "password": "securepassword123"
    }
    phone_resp = client.post("/api/v1/auth/login", json=login_payload_phone)
    assert phone_resp.status_code == 200
    current_token = phone_resp.json()["user"]["token"]

    # 5. Login with invalid password
    bad_resp = client.post("/api/v1/auth/login", json={"email_or_phone": email, "password": "wrongpassword"})
    assert bad_resp.status_code == 401

    # 6. Verify /me endpoint with active session token
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {current_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    # 7. Admin unauthorized access without header should fail with 401
    no_auth_resp = client.get("/api/v1/auth/users")
    assert no_auth_resp.status_code == 401

    # Query param alone is no longer accepted (prevents token leakage in logs)
    query_auth_resp = client.get("/api/v1/auth/users?admin_key=neetpg_admin_2024")
    assert query_auth_resp.status_code == 401

    # Invalid Bearer token should fail with 403
    bad_admin_resp = client.get("/api/v1/auth/users", headers={"Authorization": "Bearer wrong_key"})
    assert bad_admin_resp.status_code == 403

    # 8. Admin authorized list candidates using Authorization: Bearer
    admin_resp = client.get("/api/v1/auth/users", headers={"Authorization": "Bearer neetpg_admin_2024"})
    assert admin_resp.status_code == 200
    admin_data = admin_resp.json()
    assert admin_data["status"] == "success"
    assert admin_data["count"] >= 1
    found = any(u["email"] == email for u in admin_data["users"])
    assert found, "Newly registered user must be in admin candidate list"

    # 9. Admin CSV export using Authorization: Bearer
    csv_resp = client.get("/api/v1/auth/users/export", headers={"Authorization": "Bearer neetpg_admin_2024"})
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "Full Name,Email Address,Phone Number" in csv_resp.text
    assert email in csv_resp.text

    # 10. Admin dashboard HTML page
    dash_resp = client.get("/admin")
    assert dash_resp.status_code == 200
    assert "Candidate Database | NEET PG Admin" in dash_resp.text

