import os


class CONF:

    KSEFCONF_ENV = "KSEFCONF"
    KSEFDIR_ENV = "KSEFDIR"

    def __init__(self, ksef_conf_path: str, ksef_work_path: str):
        self._ksef_conf_path = ksef_conf_path
        self._ksef_work_path = ksef_work_path

    @property
    def ksef_conf_path(self) -> str:
        return self._ksef_conf_path

    @classmethod
    def from_os_env(cls):
        ksef_conf_path = os.getenv(CONF.KSEFCONF_ENV)
        if ksef_conf_path is None:
            raise ValueError(
                f"Environment variable ${CONF.KSEFCONF_ENV} is not set.")

        ksef_work_path = os.getenv(CONF.KSEFDIR_ENV)
        if ksef_work_path is None:
            raise ValueError(
                f"Environment variable ${CONF.KSEFDIR_ENV} is not set.")
        return cls(ksef_conf_path, ksef_work_path)

    def _get_work_subdirectory(self, nip: str, dir: str) -> str:
        path = os.path.join(self._ksef_work_path, dir, nip)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_ksef_log_dir(self, nip: str) -> str:
        return self._get_work_subdirectory(nip, "log")
