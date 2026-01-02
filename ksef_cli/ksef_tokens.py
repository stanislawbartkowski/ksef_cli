from collections import namedtuple

import yaml

from ksef import KSEFSDK

from .ksef_conf import CONF

_env = {
    'prod': KSEFSDK.PRODKSEF,
    'test': KSEFSDK.DEVKSEF,
    'demo': KSEFSDK.PREKSEF
}

TOKEN = namedtuple('TOKENS', ['nip', 'env', 'token', "p12", "password"])


def is_cert(t: TOKEN) -> bool:
    return t.p12 is not None and t.password is not None


_TOKEN = "token"
_P12 = "p12"
_PASSWORD = "password"


def odczytaj_tokny(C: CONF, nip: str) -> TOKEN:
    ksef_conf_path = C.ksef_conf_path
    with open(ksef_conf_path, 'r') as f:
        conf = yaml.safe_load(f)
        key = f'NIP{nip}'
        tokens = conf['tokens']
        nip_env = tokens[key]
        p12 = None
        password = None
        if _TOKEN in nip_env:
            token = nip_env[_TOKEN]
            p12 = None
            password = None
        else:
            token = None
            if _P12 not in nip_env or _PASSWORD not in nip_env:
                msg = f"{key} Nie jest zdefiniowany {_TOKEN}, autentykacja certyfiaktem wymaga {_P12} oraz {_PASSWORD}"
                raise ValueError(msg)
            p12 = nip_env[_P12]
            password = nip_env[_PASSWORD]

        env = nip_env['env']
        ksef_env = _env.get(env)
        if ksef_env is None:
            raise ValueError(
                f"{key} Nierozpoznane środowisko KSEF: {env}. Dopuszczalne wartości: 'prod', 'test', 'demo'.")
        return TOKEN(nip=nip, env=ksef_env, token=token, p12=p12, password=password)
