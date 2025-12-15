import os
import datetime

from ksef_cli.ksef_conf import CONF

from ksef.sdk.konwdokument import KONWDOKUMENT

NIP = "7497725064"

NIP_NABYWCA = "7952809480"

NIEPOPRAWNA_FAKTURA = "FA_3_Przykład_9_niepoprawna.xml"
FAKTURA_WZORZEC = "FA_3_Przykład_9_pattern.xml"


def _workdir() -> str:
    return os.path.join(os.path.dirname(__file__), 'worktemp')


def CO():
    conf_path = os.path.join(os.path.dirname(
        __file__), 'conf', "kseftokens.yaml")
    return CONF(conf_path, _workdir())


def _temp_dir(f: str) -> str:
    tmp_dir = os.path.join(_workdir(), "tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return os.path.join(tmp_dir, f)


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


def prepare_invoice(patt) -> str:
    inpath = testdatadir(patt)
    outpath = _temp_dir("faktura.xml")
    zmienne = {
        KONWDOKUMENT.DATA_WYSTAWIENIA: _today(),
        KONWDOKUMENT.NIP: NIP,
        KONWDOKUMENT.NIP_NABYWCA: NIP_NABYWCA,
        KONWDOKUMENT.NUMER_FAKTURY: _gen_numer_faktury()
    }
    KONWDOKUMENT.konwertuj(sou=inpath, dest=outpath, zmienne=zmienne)
    return outpath
