import os
import shutil

from .ksef_log import LOGGER, E
from .ksef_conf import CONF


class KSEFCLI(LOGGER):

    @classmethod
    def from_os_env(cls, nip: str):
        C = CONF.from_os_env()
        return cls(C, nip)

    def __init__(self, C: CONF, nip: str) -> None:
        super(KSEFCLI, self).__init__(C, nip)

    def clean_nip_dir(self) -> None:
        EV = self.genE(E.WYCZYSC_DANE)
        work_dir = self.C.work_nip_dir(self.nip)
        msg = f"Usunięto katalog roboczy dla NIP {self.nip}: {work_dir}"
        self.logger.info(msg)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        EV.koniec(res=True)
