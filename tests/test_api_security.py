"""API authentication tests; do not require model downloads."""
import hashlib
import json
import os
import time

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from starlette.requests import Request
from server import api


def request(host="127.0.0.1"):
    return Request({
        "type": "http", "http_version": "1.1", "method": "GET",
        "scheme": "http", "path": "/", "raw_path": b"/",
        "query_string": b"", "headers": [],
        "client": (host, 12345), "server": ("127.0.0.1", 8000),
    })


@pytest.fixture(autouse=True)
def strict_defaults(monkeypatch):
    for key, value in {
        "AUTH_MODE": "strict", "API_KEY_ENV": None, "JWT_SECRET": None,
        "JWT_PUBLIC_KEY": None, "JWT_PRIVATE_KEY": None, "JWT_USERS": None,
        "JWT_ISSUER": None, "JWT_AUDIENCE": None,
    }.items():
        monkeypatch.setattr(api, key, value)


def test_strict_denies_unconfigured_auth():
    client = TestClient(api.app)
    assert client.get("/").status_code == 200
    assert client.get("/tools").status_code == 503
    assert client.get("/metrics").status_code == 503
    assert client.post("/generate", json={"prompt": "test"}).status_code == 503


def test_bad_and_valid_keys(monkeypatch):
    monkeypatch.setattr(api, "API_KEY_ENV", "secret-key")
    client = TestClient(api.app)
    assert client.get("/tools").status_code == 401
    assert client.get("/tools", headers={"X-API-Key": "invalid"}).status_code == 401
    assert client.get("/tools", headers={"X-API-Key": "secret-key"}).status_code == 200


def test_development_local_only(monkeypatch):
    monkeypatch.setattr(api, "AUTH_MODE", "development")
    assert api.require_api_key(request("127.0.0.1")) is None
    assert api.require_api_key(request("::1")) is None
    with pytest.raises(HTTPException) as exc:
        api.require_api_key(request("10.0.0.2"))
    assert exc.value.status_code == 503


def test_jwt_must_be_verified_and_not_expired(monkeypatch):
    now = int(time.time())
    valid = jwt.encode({"sub": "alice", "exp": now + 600}, "secret", algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        api.validate_jwt(request(), valid)
    assert exc.value.status_code == 503
    monkeypatch.setattr(api, "JWT_SECRET", "secret")
    assert api.validate_jwt(request(), valid)["sub"] == "alice"
    for token in (
        "invalid",
        jwt.encode({"sub": "alice", "exp": now - 600}, "secret", algorithm="HS256"),
        jwt.encode({"sub": "alice"}, "secret", algorithm="HS256"),
    ):
        with pytest.raises(HTTPException) as exc:
            api.validate_jwt(request(), token)
        assert exc.value.status_code == 401
    with pytest.raises(HTTPException) as exc:
        api.validate_jwt(request(), None)
    assert exc.value.status_code == 401


def test_password_configuration_fail_closed(monkeypatch):
    assert not api._verify_credentials("alice", "password")
    monkeypatch.setattr(api, "JWT_USERS", json.dumps({"alice": "password"}))
    assert not api._verify_credentials("alice", "password")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", b"password", salt, 260_000).hex()
    encoded = "pbkdf2_sha256$260000$" + salt.hex() + "$" + digest
    monkeypatch.setattr(api, "JWT_USERS", json.dumps({"alice": encoded}))
    assert api._verify_credentials("alice", "password")
    assert not api._verify_credentials("alice", "incorrect")


def test_token_issue_refuses_unconfigured_credentials(monkeypatch):
    monkeypatch.setattr(api, "API_KEY_ENV", "secret-key")
    monkeypatch.setattr(api, "JWT_SECRET", "secret")
    client = TestClient(api.app)
    response = client.post(
        "/token", headers={"X-API-Key": "secret-key"},
        data={"username": "alice", "password": "password"},
    )
    assert response.status_code == 401


def test_token_refresh_rejects_invalid_bearer(monkeypatch):
    monkeypatch.setattr(api, "API_KEY_ENV", "secret-key")
    monkeypatch.setattr(api, "JWT_SECRET", "secret")
    client = TestClient(api.app)
    headers = {"X-API-Key": "secret-key"}
    assert client.post("/token/refresh", headers=headers).status_code == 401
    headers["Authorization"] = "Bearer invalid"
    assert client.post("/token/refresh", headers=headers).status_code == 401
