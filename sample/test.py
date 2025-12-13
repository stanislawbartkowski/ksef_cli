import os

from ksef_cli.ksef_tokens import odczytaj_tokny
from ksef_cli.ksef_conf import CONF

from tests.helper import CO


def test1():
    C = CONF.from_os_env()
    path = C._ksef_conf_path
    print(f"KSEF Config Path: {path}")


def test2():
    C = CO()
    token = odczytaj_tokny(C, "1234567890")


# test1()
test2()
