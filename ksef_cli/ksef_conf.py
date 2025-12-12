import os


class CONF:

    KSEFCONF_ENV = "KSEFCONF"
    KSEFDIR_ENV = "KSEFDIR"

    @staticmethod
    def get_ksef_conf_path() -> str:
        ksef_conf_path = os.getenv(CONF.KSEFCONF_ENV)
        if ksef_conf_path is None:
            raise ValueError(
                f"Environment variable ${CONF.KSEFCONF_ENV} is not set.")
        return ksef_conf_path

    @staticmethod
    def get_ksef_work_path() -> str:
        ksef_work_path = os.getenv(CONF.KSEFDIR_ENV)
        if ksef_work_path is None:
            raise ValueError(
                f"Environment variable ${CONF.KSEFDIR_ENV} is not set.")
        return ksef_work_path

    @staticmethod
    def _get_work_subdirectory(nip: str, dir: str) -> str:
        path = os.path.join(CONF.get_ksef_work_path(), dir, nip)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def get_ksef_log_dir(nip: str) -> str:
        return CONF._get_work_subdirectory(nip, "log")
