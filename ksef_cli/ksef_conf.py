from dataclasses import dataclass
import os


class NIP:

    def __init__(self, nip: str):
        nip_l = nip.split("$")
        self._nip = nip_l[0]
        self._subdir = None if len(nip_l) == 1 else nip_l[1]

    @property
    def nip(self) -> str:
        return self._nip

    @property
    def nipdir(self) -> str:
        return self._nip if self._subdir is None else os.path.join(self._nip, self._subdir)


class CONF:

    _KSEFCONF_ENV = "KSEFCONF"
    _KSEFDIR_ENV = "KSEFDIR"

    def __init__(self, ksef_conf_path: str, ksef_work_path: str):
        self._ksef_conf_path = ksef_conf_path
        self._ksef_work_path = ksef_work_path

    @staticmethod
    def test_ustaw_os_env(ksef_conf: str, ksef_dir: str):
        os.environ[CONF._KSEFCONF_ENV] = ksef_conf
        os.environ[CONF._KSEFDIR_ENV] = ksef_dir

    @property
    def ksef_conf_path(self) -> str:
        return self._ksef_conf_path

    @classmethod
    def from_os_env(cls):
        ksef_conf_path = os.getenv(CONF._KSEFCONF_ENV)
        if ksef_conf_path is None:
            raise ValueError(
                f"Environment variable {CONF._KSEFCONF_ENV} is not set.")

        ksef_work_path = os.getenv(CONF._KSEFDIR_ENV)
        if ksef_work_path is None:
            raise ValueError(
                f"Environment variable {CONF._KSEFDIR_ENV} is not set.")
        return cls(ksef_conf_path, ksef_work_path)

    def work_nip_dir(self, nip: NIP) -> str:
        path = os.path.join(self._ksef_work_path, nip.nipdir)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _get_work_subdirectory(self, nip: NIP, dir: str) -> str:
        path = os.path.join(self.work_nip_dir(nip), dir)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_nip_log_file(self, nip: NIP) -> str:
        return os.path.join(self.work_nip_dir(nip), "ksef.log")

    def get_log_file(self) -> str:
        return os.path.join(self._ksef_work_path, "ksef.log")

    def get_nip_events_file(self, nip: NIP) -> str:
        return os.path.join(self.work_nip_dir(nip), "events.csv")

    def get_events_file(self) -> str:
        return os.path.join(self._ksef_work_path, "events.csv")

    def get_invoice_upo(self, nip: NIP, ksef_numer: str) -> str:
        kdir = self._get_work_subdirectory(nip,  ksef_numer)
        return os.path.join(kdir, "upo.xml")

    def get_invoice_faktura(self, nip: NIP, ksef_numer: str) -> str:
        kdir = self._get_work_subdirectory(nip,  ksef_numer)
        return os.path.join(kdir, "faktura.xml")
