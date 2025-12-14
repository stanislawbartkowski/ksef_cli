import os
import shutil

from .ksef_conf import CONF



class KSEFCLI:

    @classmethod
    def from_os_env(cls, nip: str):
        C = CONF.from_os_env()
        return cls(C, nip)

    def __init__(self, C: CONF, nip: str) -> None:
        self._C = C
        self._nip = nip

    def clean_nip_dir(self) -> None:
        work_dir = self._C.get_ksef_work_dir(self._nip)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        
