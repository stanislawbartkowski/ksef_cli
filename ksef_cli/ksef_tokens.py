from collections import namedtuple

import yaml

from ksef import KSEFSDK

from .ksef_conf import CONF

_env = {
    'prod': KSEFSDK.PRODKSEF,
    'test': KSEFSDK.DEVKSEF,
    'demo': KSEFSDK.PREKSEF
}

TOKEN = namedtuple('TOKENS', ['nip', 'env', 'token'])


def odczytaj_tokny(C: CONF, nip: str) -> TOKEN:
    ksef_conf_path = C.ksef_conf_path
    with open(ksef_conf_path, 'r') as f:
        conf = yaml.safe_load(f)
        key = f'NIP{nip}'
        tokens = conf['tokens']
        nip_env = tokens[key]
        token = nip_env['token']
        env = nip_env['env']
        ksef_env = _env.get(env)
        if ksef_env is None:
            raise ValueError(f"Unknown KSEF environment: {env}. Possible values are 'prod', 'test', 'demo'.")
        return TOKEN(nip=nip, env=ksef_env, token=token)
