import os
import shutil
import tempfile
from typing import Callable
from requests import HTTPError

import xml.etree.ElementTree as et
import zipfile

from ksef import KSEFSDK

from .ksef_log import LOGGER, E
from .ksef_conf import CONF
from .ksef_tokens import odczytaj_tokny


class KSEFCLI(LOGGER):

    @staticmethod
    def ksef_action(action: int):
        def ksef_action_decorator(func: Callable):
            def wrapper(self, output: str, **kwargs):
                EV = self.genE(action, output=output)
                try:
                    token = odczytaj_tokny(self.C, self.nip)
                except Exception as e:
                    errmess = f"Nie można odczytać tokena KSeF dla NIP {self.nip}"
                    EV.koniec(res=False, errmess=errmess)
                    self.logger.error(errmess)
                    self.logger.exception(e)
                    return False, errmess
                try:
                    K = KSEFSDK.initsdk(
                        env=token.env, nip=token.nip, token=token.token)
                    res_dict, mess = func(self, K, **kwargs)
                    K.session_terminate()
                    EV.koniec(res=True, errmess=mess, res_dict=res_dict)
                    return True, ""
                except HTTPError as e:
                    EV.koniec(res=False, errmess=str(e))
                    self.logger.exception(e)
                    response = e.response.text
                    self.logger.error(response)
                    return False, str(e)
                except Exception as e:
                    EV.koniec(res=False, errmess=str(e))
                    self.logger.exception(e)
                    return False, str(e)
            return wrapper
        return ksef_action_decorator

    @classmethod
    def from_os_env(cls, nip: str):
        C = CONF.from_os_env()
        return cls(C, nip)

    def __init__(self, C: CONF, nip: str) -> None:
        super(KSEFCLI, self).__init__(C, nip)

    def clean_nip_dir(self, res_pathname: str) -> None:
        EV = self.genE(E.WYCZYSC_DANE, output=res_pathname)
        work_dir = self.C.work_nip_dir(self.nip)
        msg = f"Usunięto katalog roboczy dla NIP {self.nip}: {work_dir}"
        self.logger.info(msg)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        EV.koniec(res=True, errmess="")

    @ksef_action(action=E.CZYTANIE_FAKTUR_ZAKUPOWYCH)
    def czytaj_faktury_zakupowe(self, K: KSEFSDK, data_od: str, data_do: str) -> tuple[dict, str]:
        faktury_zakupowe = K.get_invoices_zakupowe_metadata(
            date_from=data_od, date_to=data_do)
        return {
            "faktury": faktury_zakupowe
        }, f"{data_od} - {data_do}"

    @ksef_action(action=E.WYSLIJ_FAKTURE)
    def wyslij_fakture_do_ksef(self, K: KSEFSDK, invoice_path: str) -> tuple[dict, str]:
        with open(invoice_path, mode="r") as f:
            invoice_xml = f.read()
        K.start_session()
        ok, err_mess, numer_ksef = K.send_invoice(invoice=invoice_xml)
        if not ok:
            K.close_session()
            raise ValueError(err_mess)
        self.logger.info(f"Faktura wysłana do KSeF. KSeF numer {numer_ksef}")
        # zapisz upo
        upo = K.pobierz_upo()
        upo_file = self.C.get_invoice_upo(self._nip, numer_ksef)
        with open(upo_file, mode="w") as f:
            self.logger.info(f"Zapisz UPO do {upo_file}")
            f.write(upo)
        K.close_session()
        faktura_file = self.C.get_invoice_faktura(
            nip=self._nip, ksef_numer=numer_ksef)
        self.logger.info(
            f"Archiwizacja faktury {invoice_path} -> {faktura_file}")
        shutil.copyfile(invoice_path, faktura_file)

        return {
            "numer_ksef": numer_ksef
        }, numer_ksef

    def wez_upo(self, res_pathname: str, ksef_number: str) -> tuple[bool, str]:
        EV = self.genE(E.WEZ_UPO, output=res_pathname)
        upo_file = self.C.get_invoice_upo(self._nip, ksef_numer=ksef_number)
        errmess = None
        if not os.path.exists(upo_file):
            errmess = f'Plik {upo_file} nie istnieje'
        else:
            with open(upo_file, mode="r") as f:
                upo_xml = f.read()
                try:
                    et.fromstring(upo_xml)
                except Exception:
                    errmess = f"Plik {upo_file} nie jest poprawnym plikiem XML"
        if errmess is None:
            res = {
                "upo": upo_file
            }
            EV.koniec(True, upo_file, res_dict=res)
            return True, ""
        EV.koniec(False, errmess)
        return False, ""

    @ksef_action(action=E.WEZ_FAKTURE)
    def wez_fakture(self, K: KSEFSDK, ksef_number: str) -> tuple[dict, str]:
        invoice = K.get_invoice(ksef_number=ksef_number)
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(invoice.encode())
            return {
                "invoice": t.name
            }, ""

    @ksef_action(action=E.WYSLIJ_WSADOWO)
    def wyslij_wsadowo_do_ksef(self, K: KSEFSDK, faktury_dir: str) -> tuple[dict, str]:

        files = os.listdir(faktury_dir)
        self.logger.info(f"Szukanie faktur w katalogy {faktury_dir}")

        with tempfile.NamedTemporaryFile(delete=False) as t:
            with zipfile.ZipFile(t.name, "w", zipfile.ZIP_DEFLATED) as zip:
                for f in files:
                    if not f.endswith(".xml"):
                        continue
                    full_path = os.path.join(faktury_dir, f)
                    self.logger.info(f"Faktura {full_path}")
                    zip.write(full_path)

        # teraz odczytuj
        maxPartSize = 100 * 1000 * 1000  # 100 MB

        def bytes_generator():
            with open(t.tname, "rb") as z:
                b = z.read(maxPartSize)
                if b is None:
                    return
                yield b

        ok, err_mess, invoices = K.send_batch_session_bytes(
            payload=bytes_generator)
        os.unlink(t.name)
        if not ok:
            raise ValueError(err_mess)

        msg = f"Wysłano {len(invoices)}, błędnych {len([i for i in invoices if not i.ok])}"
        self.logger.info(msg)
        return {
            "invoices": invoices
        }, msg
