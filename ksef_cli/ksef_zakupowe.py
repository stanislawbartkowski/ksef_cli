import os
import json
import shutil

from collections import namedtuple

from ksef_cli.ksef_log import LOGGER

METADATADICT = namedtuple(
    "METADATA", ["storagedate", "ksefnumber", "subdir", "metadata"])


class KSEF_ZAKUPOWE_HELPER:

    PERMANENTSTORAGEDATE = "permanentStorageDate"
    KSEFNUMBER = "ksefNumber"
    METADATA = "metadata.json"
    FAKTURA = "faktura.xml"
    TMETADATA = "_metadata.json"

    @staticmethod
    def _read_directory(lgr: LOGGER, kdir: str, subdir: str | None) -> list[METADATADICT]:
        dlist = os.listdir(kdir)
        lgr.logger.info(f"Czytanie faktur zakupowych z katalogu {kdir}")
        res: list[METADATADICT] = []
        for d in dlist:
            fullpath = os.path.join(kdir, d)
            # tylko podkatalogi
            if not os.path.isdir(fullpath):
                continue
            metadata = os.path.join(fullpath, KSEF_ZAKUPOWE_HELPER.METADATA)
            if not os.path.isfile(metadata):
                lgr.logger.info(f"Brak pliku {metadata}")
                continue
            fakturapath = os.path.join(fullpath, KSEF_ZAKUPOWE_HELPER.FAKTURA)
            if not os.path.isfile(fakturapath):
                lgr.logger.warning(
                    f"Jest plik {metadata} ale brak {fakturapath}")
                continue
            with open(metadata, "r") as f:
                mdata = json.load(f)
            storagedate = mdata[KSEF_ZAKUPOWE_HELPER.PERMANENTSTORAGEDATE]
            ksefnumber = mdata[KSEF_ZAKUPOWE_HELPER.KSEFNUMBER]
            lgr.logger.info(f"Odczytano fakturę {ksefnumber}")
            m = METADATADICT(storagedate=storagedate, ksefnumber=ksefnumber,
                             subdir=subdir, metadata=mdata)
            res.append(m)

        return res

    @staticmethod
    def odczytaj_wszystkie_faktury_zakupowe(lgr: LOGGER) -> list[METADATADICT]:
        c, nip = lgr.C, lgr.nip
        kdir = c.zakupowe_dir_nip(nip)
        res: list[METADATADICT] = []
        if nip.subdir is None:
            # w numerze NIP nie ma subdir
            return KSEF_ZAKUPOWE_HELPER._read_directory(lgr, kdir, None)
        # szukaj kazdym podkatalogu
        dlist = os.listdir(kdir)
        for d in dlist:
            sdir = os.path.join(kdir, d)
            if not os.path.isdir(sdir):
                continue
            res += KSEF_ZAKUPOWE_HELPER._read_directory(lgr, sdir, d)
        return res

    @staticmethod
    def daj_ostatnia_data(flist: list[METADATADICT]) -> str | None:
        if len(flist) == 0:
            return None
        return max([k.storagedate for k in flist])

    @staticmethod
    def _read_metadata(tempdir: str | None) -> list[dict]:
        if tempdir is None:
            return []
        mpath = os.path.join(tempdir, KSEF_ZAKUPOWE_HELPER.TMETADATA)
        with open(mpath, "r") as f:
            mdict = json.load(f)
        return mdict["invoices"]

    @staticmethod
    def _daj_faktura_dir(lgr: LOGGER, ksefnumber: str) -> str:
        c, nip = lgr.C, lgr.nip
        nipsubdir = c.zakupowe_dir_nip_subdir(nip)
        ksefsub = os.path.join(nipsubdir, ksefnumber)
        return ksefsub

    @staticmethod
    def _kopiuj_fakture(lgr: LOGGER, ksefnumber: str, tempdir: str, fdict: dict):
        ksefsub = KSEF_ZAKUPOWE_HELPER._daj_faktura_dir(lgr, ksefnumber)
        os.makedirs(ksefsub)
        mdest = os.path.join(ksefsub, KSEF_ZAKUPOWE_HELPER.METADATA)
        lgr.logger.info(f"Zapisanie pliku {mdest}")
        with open(mdest, "w") as f:
            json.dump(fdict, f)
        ksefsou = os.path.join(tempdir, ksefnumber)+".xml"
        ksefdest = os.path.join(ksefsub, KSEF_ZAKUPOWE_HELPER.FAKTURA)
        lgr.logger.info(f"Kopiowanie {ksefsou} => {ksefdest}")
        shutil.copy(ksefsou, ksefdest)

    @staticmethod
    def uaktualnij_faktury(lgr: LOGGER, alist: list[METADATADICT], tempdir: str | None) -> list[METADATADICT]:
        mlist = KSEF_ZAKUPOWE_HELPER._read_metadata(tempdir)
        if len(mlist) == 0:
            return []
        existing_f = {k.ksefnumber for k in alist}
        res = []
        for m in mlist:
            ksefnumber = m[KSEF_ZAKUPOWE_HELPER.KSEFNUMBER]
            storagedate = m[KSEF_ZAKUPOWE_HELPER.PERMANENTSTORAGEDATE]
            if ksefnumber in existing_f:
                lgr.logger.info(f"Faktura {ksefnumber} już została odczytana")
                continue
            KSEF_ZAKUPOWE_HELPER._kopiuj_fakture(
                lgr, ksefnumber, tempdir, m)
            mt = METADATADICT(storagedate=storagedate, ksefnumber=ksefnumber,
                              subdir=lgr.nip.subdir, metadata=m)
            res.append(mt)
        return res

    @staticmethod
    def daj_faktura_zakupowa_path(lgr: LOGGER, ksefnumber: str) -> str:
        ksefsub = KSEF_ZAKUPOWE_HELPER._daj_faktura_dir(lgr, ksefnumber)
        return os.path.join(ksefsub, KSEF_ZAKUPOWE_HELPER.FAKTURA)
