from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional

from ksef import KSEFSDK

from .ksef_conf import CONF


KSEF_ENV = {
    "prod": KSEFSDK.PRODKSEF,
    "test": KSEFSDK.DEVKSEF,
    "demo": KSEFSDK.PREKSEF,
    "unittest": KSEFSDK.UNITTEST,
}


def resolve_env(env_s: str) -> int:
    env = KSEF_ENV.get(env_s)
    if env is None:
        raise ValueError(
            f"Nierozpoznane środowisko KSEF: {env_s}. Dopuszczalne wartości: {sorted(KSEF_ENV)}."
        )
    return env


@dataclass
class Credentials(ABC):
    nip: str
    env: int
    env_s: str

    @abstractmethod
    def is_cert(self) -> bool: ...

    def get_token(self) -> str:
        raise NotImplementedError("This Credentials variant does not expose a token")

    def get_cert(self) -> tuple[bytes, bytes]:
        raise NotImplementedError("This Credentials variant does not expose a certificate")


@dataclass
class TokenCredentials(Credentials):
    token: str

    def is_cert(self) -> bool:
        return False

    def get_token(self) -> str:
        return self.token


@dataclass
class CertCredentials(Credentials):
    cert_loader: Callable[[], tuple[bytes, bytes]]

    def is_cert(self) -> bool:
        return True

    def get_cert(self) -> tuple[bytes, bytes]:
        return self.cert_loader()


class CredentialsProvider(ABC):
    name: str = ""

    @abstractmethod
    def get_credentials(self, conf: CONF, nip: str) -> Credentials: ...

    def add_token(self, conf: CONF, nip: str, env_s: str, token: str) -> None:
        raise NotImplementedError(
            f"Provider {self.name!r} does not support adding token credentials"
        )

    def add_cert(
        self, conf: CONF, nip: str, env_s: str, p12_path: str, password: str
    ) -> None:
        raise NotImplementedError(
            f"Provider {self.name!r} does not support adding certificate credentials"
        )


ENV_VAR = "KSEF_CREDENTIALS_PROVIDER"
ENTRY_POINT_GROUP = "ksef_cli.credentials_providers"

_providers: dict[str, CredentialsProvider] = {}
_default_provider_name = "yaml"
_entry_points_loaded = False


def register_provider(provider: CredentialsProvider, name: Optional[str] = None) -> None:
    key = name or provider.name
    if not key:
        raise ValueError("Provider must define a non-empty .name or pass name explicitly")
    _providers[key] = provider


def set_default_provider(name: str) -> None:
    global _default_provider_name
    _default_provider_name = name


def registered_providers() -> list[str]:
    return sorted(_providers)


def _load_entry_points() -> None:
    global _entry_points_loaded
    if _entry_points_loaded:
        return
    _entry_points_loaded = True
    try:
        from importlib.metadata import entry_points

        eps = entry_points(group=ENTRY_POINT_GROUP)
    except Exception:
        return
    for ep in eps:
        try:
            obj = ep.load()
            provider = obj() if isinstance(obj, type) else obj
            register_provider(provider, name=ep.name)
        except Exception:
            continue


def _ensure_builtin_defaults(name: str) -> None:
    if name == "yaml" and "yaml" not in _providers:
        from . import credentials_yaml  # noqa: F401


def get_provider(name: Optional[str] = None) -> CredentialsProvider:
    selected = name or os.environ.get(ENV_VAR) or _default_provider_name
    if selected not in _providers:
        _ensure_builtin_defaults(selected)
    if selected not in _providers:
        _load_entry_points()
    if selected not in _providers:
        raise ValueError(
            f"Unknown credentials provider: {selected!r}. Registered: {registered_providers()}"
        )
    return _providers[selected]


def load_credentials(conf: CONF, nip: str, provider_name: Optional[str] = None) -> Credentials:
    return get_provider(provider_name).get_credentials(conf, nip)


def add_token_credentials(
    conf: CONF,
    nip: str,
    env_s: str,
    token: str,
    provider_name: Optional[str] = None,
) -> None:
    resolve_env(env_s)
    get_provider(provider_name).add_token(conf, nip, env_s, token)


def add_cert_credentials(
    conf: CONF,
    nip: str,
    env_s: str,
    p12_path: str,
    password: str,
    provider_name: Optional[str] = None,
) -> None:
    resolve_env(env_s)
    get_provider(provider_name).add_cert(conf, nip, env_s, p12_path, password)
