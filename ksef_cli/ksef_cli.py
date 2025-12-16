import os
import shutil
from typing import Callable

import xml.etree.ElementTree as et

from ksef import KSEFSDK
from requests import HTTPError

from .ksef_log import LOGGER, E
from .ksef_conf import CONF
from .ksef_tokens import odczytaj_tokny


class KSEFCLI(LOGGER):

    @classmethod
    def from_os_env(cls, nip: str):
        C = CONF.from_os_env()
        return cls(C, nip)

    def __init__(self, C: CONF, nip: str) -> None:
        super(KSEFCLI, self).__init__(C, nip)

    def clean_nip_dir(self) -> None:
        EV = self.genE(E.WYCZYSC_DANE, output=None)
        work_dir = self.C.work_nip_dir(self.nip)
        msg = f"Usunięto katalog roboczy dla NIP {self.nip}: {work_dir}"
        self.logger.info(msg)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        EV.koniec(res=True, errmess="")

    def _do_action(self, action: int, output: str, run_func: Callable, **kwargs) -> tuple[bool, str]:
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
            res_dict, mess = run_func(K, **kwargs)
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

    def _czytaj_faktury_zakupe_action(self, K: KSEFSDK, data_od: str, data_do: str) -> tuple[dict, str]:
        faktury_zakupowe = K.get_invoices_zakupowe_metadata(
            date_from=data_od, date_to=data_do)
        return {
            "faktury": faktury_zakupowe
        }, f"{data_od} - {data_do}"

    def czytaj_faktury_zakupowe(self, res_pathname: str, data_od: str, data_do: str) -> tuple[bool, str]:
        return self._do_action(
            action=E.CZYTANIE_FAKTUR_ZAKUPOWYCH,
            output=res_pathname,
            run_func=self._czytaj_faktury_zakupe_action,
            data_od=data_od,
            data_do=data_do
        )

    def _wyslij_fakture_do_ksef_action(self, K: KSEFSDK, invoice_path: str) -> tuple[dict, str]:
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
        return {
            "numer_ksef": numer_ksef
        }, numer_ksef

    def wyslij_fakture_do_ksef(self, res_pathname: str, invoice_path: str) -> tuple[bool, str]:
        return self._do_action(
            action=E.WYSLIJ_FAKTURE,
            output=res_pathname,
            run_func=self._wyslij_fakture_do_ksef_action,
            invoice_path=invoice_path
        )

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
