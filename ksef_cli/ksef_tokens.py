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


def odczytaj_tokny(nip: str) -> TOKEN:
    ksef_conf_path = CONF.get_ksef_conf_path()
    with open(ksef_conf_path, 'r') as f:
        conf = yaml.safe_load(f)
        key = f'NIP{nip}'
        env_conf = conf[key]
        token = env_conf['token']
        env = env_conf['env']
        return TOKEN(nip=nip, env=_env[env], token=token)
