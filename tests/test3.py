import json
import os

import pytest
import yaml

from ksef_cli import (
    add_cert_credentials,
    add_token_credentials,
    load_credentials,
)
from ksef_cli.ksef_conf import CONF
from ksef_cli.main import run_main


@pytest.fixture
def conf(tmp_path):
    conf_path = tmp_path / "ksef.yaml"
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    return CONF(str(conf_path), str(work_dir))


@pytest.fixture
def conf_env(tmp_path, monkeypatch):
    conf_path = tmp_path / "ksef.yaml"
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    monkeypatch.setenv("KSEFCONF", str(conf_path))
    monkeypatch.setenv("KSEFDIR", str(work_dir))
    return CONF(str(conf_path), str(work_dir))


def _read_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


# ---------- Provider-level tests ----------


def test_add_token_creates_yaml_when_missing(conf):
    assert not os.path.exists(conf.ksef_conf_path)
    add_token_credentials(conf, "1111111111", env_s="test", token="tok-1")
    data = _read_yaml(conf.ksef_conf_path)
    assert data["tokens"]["NIP1111111111"] == {"token": "tok-1", "env": "test"}


def test_add_token_roundtrip(conf):
    add_token_credentials(conf, "1111111111", env_s="demo", token="tok-1")
    cred = load_credentials(conf, "1111111111")
    assert not cred.is_cert()
    assert cred.get_token() == "tok-1"
    assert cred.env_s == "demo"


def test_add_cert_roundtrip(conf):
    add_cert_credentials(
        conf, "2222222222", env_s="prod", p12_path="/tmp/x.p12", password="pw"
    )
    cred = load_credentials(conf, "2222222222")
    assert cred.is_cert()
    assert cred.env_s == "prod"


def test_add_token_overwrites_existing_silently(conf):
    add_token_credentials(conf, "1111111111", env_s="test", token="tok-1")
    add_token_credentials(conf, "1111111111", env_s="demo", token="tok-2")
    cred = load_credentials(conf, "1111111111")
    assert cred.get_token() == "tok-2"
    assert cred.env_s == "demo"


def test_add_cert_overwrites_token(conf):
    add_token_credentials(conf, "1111111111", env_s="test", token="tok-1")
    add_cert_credentials(
        conf, "1111111111", env_s="prod", p12_path="/tmp/x.p12", password="pw"
    )
    cred = load_credentials(conf, "1111111111")
    assert cred.is_cert()
    assert cred.env_s == "prod"


def test_add_preserves_other_nips(conf):
    add_token_credentials(conf, "1111111111", env_s="test", token="tok-1")
    add_token_credentials(conf, "2222222222", env_s="prod", token="tok-2")
    data = _read_yaml(conf.ksef_conf_path)
    assert "NIP1111111111" in data["tokens"]
    assert "NIP2222222222" in data["tokens"]


def test_invalid_env_rejected_for_token(conf):
    with pytest.raises(ValueError):
        add_token_credentials(conf, "1111111111", env_s="bogus", token="x")


def test_invalid_env_rejected_for_cert(conf):
    with pytest.raises(ValueError):
        add_cert_credentials(
            conf, "1111111111", env_s="bogus", p12_path="/tmp/x.p12", password="pw"
        )


def test_invalid_env_does_not_create_yaml(conf):
    with pytest.raises(ValueError):
        add_token_credentials(conf, "1111111111", env_s="bogus", token="x")
    assert not os.path.exists(conf.ksef_conf_path)


# ---------- CLI-level tests via run_main ----------


def test_dodaj_token_cli_action(conf_env, tmp_path):
    output = tmp_path / "out.json"
    run_main(["__main__", "dodaj_token", "1111111111", str(output), "test", "tok-1"])
    data = _read_yaml(conf_env.ksef_conf_path)
    assert data["tokens"]["NIP1111111111"] == {"token": "tok-1", "env": "test"}
    res = json.loads(output.read_text())
    assert res["OK"] is True
    assert res["auth"] == "token"
    assert res["env"] == "test"


def test_dodaj_certyfikat_cli_action(conf_env, tmp_path):
    output = tmp_path / "out.json"
    run_main([
        "__main__", "dodaj_certyfikat", "2222222222", str(output),
        "prod", "/tmp/x.p12", "pw",
    ])
    data = _read_yaml(conf_env.ksef_conf_path)
    assert data["tokens"]["NIP2222222222"] == {
        "p12": "/tmp/x.p12", "password": "pw", "env": "prod",
    }
    res = json.loads(output.read_text())
    assert res["OK"] is True
    assert res["auth"] == "certyfikat"
    assert res["env"] == "prod"
    assert res["p12"] == "/tmp/x.p12"


def test_dodaj_token_cli_bad_env_writes_error(conf_env, tmp_path):
    output = tmp_path / "out.json"
    run_main(["__main__", "dodaj_token", "1111111111", str(output), "bogus", "tok-1"])
    res = json.loads(output.read_text())
    assert res["OK"] is False
    assert "bogus" in res["errmess"]
    assert not os.path.exists(conf_env.ksef_conf_path)
