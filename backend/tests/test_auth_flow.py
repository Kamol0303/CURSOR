import pyotp


async def test_password_login_requires_mfa_for_super_admin(client, seeded_db):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin.tamor", "password": "Tamor#2026Admin!"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["mfa_required"] is True
    assert body["data"]["challenge_token"]


async def test_mfa_login_and_refresh_rotation_detects_replay(client, seeded_db):
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin.tamor", "password": "Tamor#2026Admin!"},
    )
    challenge_token = login.json()["data"]["challenge_token"]
    totp_code = pyotp.TOTP(seeded_db["secret"]).now()

    verify = await client.post("/api/v1/auth/mfa/verify", json={"challenge_token": challenge_token, "code": totp_code})
    assert verify.status_code == 200
    refresh_cookie = verify.cookies.get("tamor_refresh")
    assert refresh_cookie

    client.cookies.set("tamor_refresh", refresh_cookie)
    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    rotated_cookie = refresh.cookies.get("tamor_refresh")
    assert rotated_cookie and rotated_cookie != refresh_cookie

    client.cookies.set("tamor_refresh", refresh_cookie)
    replay = await client.post("/api/v1/auth/refresh")
    assert replay.status_code == 401
    assert replay.json()["detail"]["code"] == "REFRESH_TOKEN_REPLAY_DETECTED"


async def test_parent_otp_login_flow(client):
    request_otp = await client.post("/api/v1/auth/parent/request-otp", json={"phone": "+998901234567"})
    assert request_otp.status_code == 200
    delivery = request_otp.json()["data"]["delivery"]
    code = delivery.rsplit("code=", 1)[1]

    verify = await client.post("/api/v1/auth/parent/verify-otp", json={"phone": "+998901234567", "code": code})
    assert verify.status_code == 200
    assert verify.json()["data"]["user"]["phone"] == "+998901234567"
