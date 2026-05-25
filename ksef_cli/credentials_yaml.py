from __future__ import annotations

import os

import yaml

from .credentials import (
    CertCredentials,
    Credentials,
    CredentialsProvider,
    TokenCredentials,
    register_provider,
    resolve_env,
)
from .ksef_conf import CONF
from .readp12 import read_cert


class YamlCredentialsProvider(CredentialsProvider):
    name = "yaml"

    TOKEN_KEY = "token"
    P12_KEY = "p12"
    PASSWORD_KEY = "password"
    ENV_KEY = "env"
    TOKENS_KEY = "tokens"

    def get_credentials(self, conf: CONF, nip: str) -> Credentials:
        ksef_conf_path = conf.ksef_conf_path
        with open(ksef_conf_path, "r") as f:
            data = yaml.safe_load(f)

        key = f"NIP{nip}"
        entry = data[self.TOKENS_KEY][key]
        env_s = entry[self.ENV_KEY]
        env = resolve_env(env_s)

        if self.TOKEN_KEY in entry:
            return TokenCredentials(
                nip=nip, env=env, env_s=env_s, token=entry[self.TOKEN_KEY]
            )

        if self.P12_KEY not in entry or self.PASSWORD_KEY not in entry:
            raise ValueError(
                f"{key} Nie jest zdefiniowany {self.TOKEN_KEY}, "
                f"autentykacja certyfikatem wymaga {self.P12_KEY} oraz {self.PASSWORD_KEY}"
            )

        p12_path = entry[self.P12_KEY]
        password = entry[self.PASSWORD_KEY]

        head, _ = os.path.split(p12_path)
        if head == "":
            p12_path = os.path.join(os.path.dirname(ksef_conf_path), p12_path)

        def loader() -> tuple[bytes, bytes]:
            return read_cert(file_path=p12_path, password=password)

        return CertCredentials(nip=nip, env=env, env_s=env_s, cert_loader=loader)

    def _write_entry(self, conf: CONF, nip: str, entry: dict) -> None:
        ksef_conf_path = conf.ksef_conf_path
        if os.path.exists(ksef_conf_path):
            with open(ksef_conf_path, "r") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        data.setdefault(self.TOKENS_KEY, {})
        data[self.TOKENS_KEY][f"NIP{nip}"] = entry
        with open(ksef_conf_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def add_token(self, conf: CONF, nip: str, env_s: str, token: str) -> None:
        self._write_entry(
            conf,
            nip,
            {self.TOKEN_KEY: token, self.ENV_KEY: env_s},
        )

    def add_cert(
        self, conf: CONF, nip: str, env_s: str, p12_path: str, password: str
    ) -> None:
        self._write_entry(
            conf,
            nip,
            {self.P12_KEY: p12_path, self.PASSWORD_KEY: password, self.ENV_KEY: env_s},
        )


register_provider(YamlCredentialsProvider())
