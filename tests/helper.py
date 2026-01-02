import os
import datetime

from ksef_cli.ksef_conf import CONF

from xml_konwerter import konwertujdok

NIP = "7497725064"

NIP_NABYWCA = "7952809480"

NIEPOPRAWNA_FAKTURA = "FA_3_Przykład_9_niepoprawna.xml"
FAKTURA_WZORZEC = "FA_3_Przykład_9_pattern.xml"
FAKTURA_ZAKUP = "FA_3_Przykład_8_zakup.xml"

_DATA_WYSTAWIENIA = "DATA_WYSTAWIENIA"
_NIP = "NIP"
_NIP_NABYWCA = "NIP_NABYWCA"
_NUMER_FAKTURY = "NUMER_FAKTURY"


def _workdir() -> str:
    return os.path.join(os.path.dirname(__file__), 'worktemp')


def _daj_dir() -> tuple[str, str]:
    conf_path = os.path.join(os.path.dirname(
        __file__), 'conf', "kseftokens.yaml")
    return conf_path, _workdir()


def _daj_dir_cert() -> tuple[str, str]:
    conf_path = os.path.join(os.path.dirname(
        __file__), 'conf', "kseftokenscert.yaml")
    return conf_path, _workdir()


def CO():
    conf_path, work_dir = _daj_dir()
    return CONF(conf_path, work_dir)


def CO_CERT():
    conf_path, work_dir = _daj_dir_cert()
    return CONF(conf_path, work_dir)


def ustaw_E():
    conf_path, work_dir = _daj_dir()
    CONF.test_ustaw_os_env(conf_path, work_dir)


def temp_dir() -> str:
    tmp_dir = os.path.join(_workdir(), "tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def temp_dir_remove_xml():
    tmp_dir = temp_dir()
    l_dir = os.listdir(tmp_dir)
    for l in l_dir:
        if l.endswith(".xml"):
            full_path = os.path.join(tmp_dir, l)
            os.unlink(full_path)


def _temp_dir(f: str) -> str:
    t_dir = temp_dir()
    return os.path.join(t_dir, f)


def temp_res() -> str:
    return _temp_dir("output.json")


def temp_ojosn():
    return os.path.join(_workdir(), 'output.json')


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _gen_numer_faktury():
    nr = "FV"
    data_f = datetime.datetime.now().isoformat()
    return nr + data_f


def testdatadir(filexml: str) -> str:
    dir = os.path.join(os.path.dirname(__file__), "testdata")
    return os.path.join(dir, filexml)


def prepare_invoice_faktur(patt: str, faktura: str) -> tuple[str, str]:
    inpath = testdatadir(patt)
    outpath = _temp_dir(faktura)
    invoice = _gen_numer_faktury()
    zmienne = {
        _DATA_WYSTAWIENIA: _today(),
        _NIP: NIP,
        _NIP_NABYWCA: NIP_NABYWCA,
        _NUMER_FAKTURY: invoice
    }
    konwertujdok(sou=inpath, dest=outpath, d=zmienne)
    return outpath, invoice


def prepare_invoice(patt: str) -> str:
    temp_dir_remove_xml()
    outpath, _ = prepare_invoice_faktur(patt, "faktura.xml")
    return outpath


def daj_przedzial() -> tuple[str, str]:
    d2 = datetime.datetime.now() + datetime.timedelta(days=2)
    d1 = d2 - datetime.timedelta(days=7)
    d_from = d1.strftime("%Y-%m-%d")
    d_to = d2.strftime("%Y-%m-%d")
    return d_from, d_to
