import logging
import time
from datetime import datetime
import csv

from .ksef_conf import CONF


def _toiso_str(t: float) -> str:
    return datetime.fromtimestamp(t).isoformat()


def _def_logger(C: CONF, nip: str):
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
        self._nip = nip

    @property
    def nip(self) -> str:
        return self._nip

    @property
    def C(self) -> CONF:
        return self._C


class E(_A):

    WYCZYSC_DANE = 0

    _d = {
        WYCZYSC_DANE: "Wyczyść dane robocze"
    }

    def __init__(self, C: CONF, nip: str, action: int):
        super(E, self).__init__(C, nip)
        self._action = action
        self._start_time = time.time()

    def koniec(self, res):
        end_time = time.time()
        elapsed = end_time - self._start_time
        info = {
            "start_time": _toiso_str(self._start_time),
            "end_time": _toiso_str(end_time),
            "elapsed_seconds": f"{elapsed:.2f}",
            "action:": self._d.get(self._action, "Nieznana akcja"),
            "result": "OK" if res else "FAIL",
            "nip": self.nip
        }
        list = ["start_time", "end_time", "elapsed_seconds",
                "action:", "result", "nip"]
        for f in self.C.get_events_file(), self.C.get_nip_events_file(self.nip):
            with open(f, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(info)


class LOGGER(_A):

    def __init__(self, C: CONF, nip: str):
        super(LOGGER, self).__init__(C, nip)
        _def_logger(C, nip)
        self._logger = logging.getLogger(__name__)

    def genE(self, action: int) -> E:
        return E(self.C, self.nip, action)

    @property
    def logger(self):
        return self._logger
