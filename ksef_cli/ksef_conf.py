import os


class CONF:

    @staticmethod
    def get_ksef_conf_path() -> str:
        ksef_conf_path = os.getenv("KSEFCONF")
        if ksef_conf_path is None:
            raise ValueError("Environment variable KSEFCONF is not set.")
        return ksef_conf_path

    @staticmethod
    def get_ksef_work_path() -> str:
        ksef_work_path = os.getenv("KSEFDIR")
        if ksef_work_path is None:
            raise ValueError("Environment variable KSEFDIR is not set.")
        return ksef_work_path
