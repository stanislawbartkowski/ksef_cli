import os

from ksef_cli.ksef_conf import CONF
from ksef_cli.ksef_tokens import odczytaj_tokny

from tests.helper import set_os


def test1():
    path = CONF.get_ksef_conf_path()
    print(f"KSEF Config Path: {path}")


def test2():
    set_os()
    token = odczytaj_tokny("1234567890")

# test1()
test2()