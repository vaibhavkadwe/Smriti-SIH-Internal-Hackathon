"""Tests for Phase 1 backend foundation."""
import pytest
from app.services.auth_service import AuthService
from app.config import settings


def test_password_hashing():
    pw = "secret123"
    hashed = AuthService.hash_password(pw)
    assert hashed != pw
    assert AuthService.verify_password(pw, hashed)
    assert not AuthService.verify_password("wrong", hashed)


def test_access_token_create_and_verify():
    data = {"sub": "12345", "role": "family_caregiver"}
    token = AuthService.create_access_token(data)
    assert isinstance(token, str)
    payload = AuthService.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "12345"
    assert payload["role"] == "family_caregiver"


def test_refresh_token_create_and_verify():
    data = {"sub": "12345"}
    token = AuthService.create_refresh_token(data)
    assert isinstance(token, str)
    payload = AuthService.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "12345"


def test_invalid_token():
    assert AuthService.verify_token("invalid.token.here") is None


def test_config_languages():
    assert "assamese" in settings.LANGUAGE_SET
    assert "bengali" in settings.LANGUAGE_SET
    assert "hindi" in settings.LANGUAGE_SET
    assert "english" in settings.LANGUAGE_SET
