import logging

from ksef_cli.ksef_tokens import odczytaj_tokny
from ksef_cli.ksef_conf import CONF
from ksef_cli import KSEFCLI

from tests.helper import CO


def wez_logger():
    return logging.getLogger(__name__)


def test1():
    C = CONF.from_os_env()
    path = C._ksef_conf_path
    print(f"KSEF Config Path: {path}")


def test2():
    C = CO()
    odczytaj_tokny(C, "1234567890")


def test3():
    C = CO()
    nip = "1234567890"
    C = CO()
    cli = KSEFCLI(C, nip)
    cli.logger.info("KSEFCLI initialized successfully.")
    cli.clean_nip_dir()


# test1()
# test2()
test3()
