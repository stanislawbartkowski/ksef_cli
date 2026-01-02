import logging

from ksef_cli.ksef_tokens import odczytaj_tokny
from ksef_cli.ksef_conf import CONF
from ksef_cli import KSEFCLI

import tests.helper as T


def wez_logger():
    return logging.getLogger(__name__)


def test1():
    C = CONF.from_os_env()
    path = C._ksef_conf_path
    print(f"KSEF Config Path: {path}")


def test2():
    C = T.CO()
    odczytaj_tokny(C, "1234567890")


def test3():
    nip = "1234567890"
    C = T.CO()
    cli = KSEFCLI(C, nip)
    output = T.temp_ojosn()
    cli.logger.info("KSEFCLI initialized successfully.")
    cli.clean_nip_dir(res_pathname=output)


def test4():
    C = T.CO()
    nip = "1234567890"
    cli = KSEFCLI(C, nip)
    output = T.temp_ojosn()
    res = cli.czytaj_faktury_zakupowe(output, "2023-01-01", "2023-12-31")
    print(res)


def test5():
    C = T.CO()
    nip = T.NIP
    fa = T.NIEPOPRAWNA_FAKTURA
    invoice_path = T.testdatadir(fa)
    cli = KSEFCLI(C, nip)
    output = T.temp_ojosn()
    res = cli.wyslij_fakture_do_ksef(
        output=output, invoice_path=invoice_path)
    print(res)


def test6():
    C = T.CO()
    nip = T.NIP
    fa = T.FAKTURA_WZORZEC
    invoice_path = T.prepare_invoice(fa)
    cli = KSEFCLI(C, nip)
    output = T.temp_ojosn()
    res = cli.wyslij_fakture_do_ksef(
        output=output, invoice_path=invoice_path)
    print(res)


def test7():
    C = T.CO()
    nip = T.NIP
    fa = T.FAKTURA_WZORZEC
    _ = T.prepare_invoice(fa)
    tmp_dir = T.temp_dir()
    cli = KSEFCLI(C, nip)
    output = T.temp_ojosn()
    res = cli.wyslij_wsadowo_do_ksef(output=output, faktury_dir=tmp_dir)
    print(res)


def test8():
    C = T.CO_CERT()
    odczytaj_tokny(C, "1234567")


# test1()
# test2()
# test3()
# test4()
# test5()
# test6()
# test7()
test8()
