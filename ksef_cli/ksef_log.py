import logging
import time
from datetime import datetime
import csv
import json

from .ksef_conf import CONF, NIP


def _toiso_str(t: float) -> str:
    return datetime.fromtimestamp(t).isoformat()


def _def_logger(C: CONF, nip: NIP):
    format_st = "%(asctime)s %(message)s"
    formatter = logging.Formatter(fmt=format_st, datefmt="%Y-%m-%d %H:%M:%S")
    logging.basicConfig(level=logging.INFO, format=format_st)
    for fname in [C.get_log_file(), C.get_nip_log_file(nip)]:
        file_handler = logging.FileHandler(fname, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)


class _A:
    def __init__(self, C: CONF, nip: str):
        self._C = C
        self._nip = NIP(nip)

    @property
    def nip(self) -> NIP:
        return self._nip

    @property
    def C(self) -> CONF:
        return self._C


class E(_A):

    WYCZYSC_DANE = 0
    CZYTANIE_FAKTUR_ZAKUPOWYCH = 1
    WYSLIJ_FAKTURE = 2
    WEZ_UPO = 3
    WEZ_FAKTURE = 4
    WYSLIJ_WSADOWO = 5
    CZYTANIE_FAKTUR_SPRZEDAZY = 6
    CZYTANIE_FAKTUR_ZBIORCZO = 7
    CZYTANIE_ZAKUPY_PRZYROSTOWO = 8
    UAKTUALNIJ_ZAKUPY_PRZYROSTOWO = 9
    WEZ_FAKTURA_BUFOR = 10
    DODAJ_TOKEN = 11
    DODAJ_CERTYFIKAT = 12
    POBIERZ_TOKENY = 13
    SPRAWDZ_TOKEN = 14
    SPRAWDZ_CERTYFIKAT = 15

    _d = {
        WYCZYSC_DANE: "Wyczyść dane robocze",
        CZYTANIE_FAKTUR_ZAKUPOWYCH: "Czytanie faktur zakupowych",
        WYSLIJ_FAKTURE: "Wyślij fakture do KSeF",
        WEZ_UPO: "Weź UPO",
        WEZ_FAKTURE: "Weź fakturę z KSeF",
        WYSLIJ_WSADOWO: "Wyślij faktury wsadowo",
        CZYTANIE_FAKTUR_SPRZEDAZY: "Czytanie faktur sprzedaży",
        CZYTANIE_FAKTUR_ZBIORCZO: "Czytanie faktur zbiorczo",
        CZYTANIE_ZAKUPY_PRZYROSTOWO: "Czytanie przyrostowe",
        UAKTUALNIJ_ZAKUPY_PRZYROSTOWO: "Uaktualnij przyrostowe",
        WEZ_FAKTURA_BUFOR: "Faktura z bufora zakupowego",
        DODAJ_TOKEN: "Dodaj token dla NIP",
        DODAJ_CERTYFIKAT: "Dodaj certyfikat dla NIP",
        POBIERZ_TOKENY: "Pobierz listę tokenów z KSeF",
        SPRAWDZ_TOKEN: "Sprawdź poprawność tokena",
        SPRAWDZ_CERTYFIKAT: "Sprawdź poprawność certyfikatu"
    }

    def __init__(self, C: CONF, nip: str, action: int, output: str | None):
        super(E, self).__init__(C, nip)
        self._action = action
        self._start_time = time.time()
        self._output = output

    @staticmethod
    def zapisz_res(output: str | None, res: bool, errmess: str | None, res_dict: dict):
        if output is not None:
            # zapisz output
            res_output = {
                "OK": res,
                "errmess": errmess,
            }
            res_output.update(res_dict)
            with open(output, "w") as f:
                json.dump(res_output, f)

    def koniec(self, res: bool, errmess: str, res_dict=None):
        res_dict = res_dict or {}
        end_time = time.time()
        elapsed = end_time - self._start_time
        info = {
            "start_time": _toiso_str(self._start_time),
            "end_time": _toiso_str(end_time),
            "elapsed_seconds": f"{elapsed:.2f}",
            "a": self._action,
            "action": self._d.get(self._action, "Nieznana akcja"),
            "result": "OK" if res else "FAIL",
            "errmess": "" if res else errmess,
            "nip": self.nip.nip_s,
            "addinfo": errmess if res else ""
        }
        list = ["start_time", "end_time", "elapsed_seconds",
                "a", "action", "result", "errmess", "nip", "addinfo"]
        for f_name in [self.C.get_events_file(), self.C.get_nip_events_file(self.nip)]:
            with open(f_name, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list, delimiter="|")
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(info)
        E.zapisz_res(self._output, res=res, errmess=errmess, res_dict=res_dict)


class LOGGER(_A):

    def __init__(self, C: CONF, nip: str):
        super(LOGGER, self).__init__(C, nip)
        _def_logger(C, self.nip)
        self._logger = logging.getLogger(__name__)

    def genE(self, action: int, output: str | None) -> E:
        return E(self.C, nip=self.nip.nip_s, action=action, output=output)

    @property
    def logger(self):
        return self._logger
