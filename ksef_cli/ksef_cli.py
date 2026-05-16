import io
import os
import shutil
import tempfile
from typing import Callable
from requests import HTTPError
from datetime import date, timedelta
from dateutil.parser import parse

import xml.etree.ElementTree as et
import zipfile

from ksef import KSEFSDK

from ksef_cli.ksef_zakupowe import KSEF_ZAKUPOWE_HELPER

from .ksef_log import LOGGER, E
from .ksef_conf import CONF, NIP
from .ksef_tokens import odczytaj_tokny, TOKEN, is_cert
from .readp12 import read_cert


def _tomorrow() -> str:
    today = date.today()
    t = timedelta(days=2)
    tomorrow = today + t
    return tomorrow.isoformat()


def _minus_days(minus_days: int) -> str:
    today = date.today()
    t = timedelta(days=minus_days)
    d = today - t
    return d.isoformat()


def _iso_format_to_date(s: str) -> str:
    # d = datetime.fromisoformat(s)
    # use parse to be compatible with python 3.10
    d = parse(s)
    return d.date().isoformat()


def _daj_cert(conf_path: str, t: TOKEN) -> tuple[bytes, bytes]:
    path_p12 = t.p12
    password = t.password
    head, _ = os.path.split(path_p12)
    if head == "":
        # ścieżka względna do pliku konfiguracyjnego
        conf_dir = os.path.dirname(conf_path)
        path_p12 = os.path.join(conf_dir, path_p12)
    return read_cert(file_path=path_p12, password=password)


class KSEFCLI(LOGGER, KSEF_ZAKUPOWE_HELPER):
    @staticmethod
    def ksef_action(action: int, enable_session=True):
        def ksef_action_decorator(func: Callable):
            def wrapper(self, output: str, **kwargs):
                EV = self.genE(action, output=output)
                try:
                    self.logger.info(f"Czytanie konfiguracji z pliku {self.C.ksef_conf_path}")
                    nip: NIP = self.nip
                    token: TOKEN = odczytaj_tokny(self.C, nip.nip)
                except Exception as e:
                    errmess = f"Nie można odczytać tokena KSeF dla NIP {nip.nip}"
                    EV.koniec(res=False, errmess=errmess)
                    self.logger.error(errmess)
                    self.logger.exception(e)
                    return False, errmess
                try:
                    if is_cert(token):
                        key, cert = _daj_cert(self.C.ksef_conf_path, token)
                        # autentykacja certyfikatem
                        K = (
                            KSEFSDK.initsdkcert(env=token.env, nip=token.nip, p12pk=key, p12pc=cert)
                            if enable_session
                            else None
                        )
                    else:
                        # autentykacja tokenem
                        K = KSEFSDK.initsdk(env=token.env, nip=token.nip, token=token.token) if enable_session else None
                    res_dict, mess = func(self, K, **kwargs)
                    if K:
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
        # faktury zakupowe
        zak_dir = self.C.zakupowe_dir_nip_subdir(self.nip)
        if os.path.exists(zak_dir):
            shutil.rmtree(zak_dir)
        EV.koniec(res=True, errmess="")

    def _czytaj_faktury(self, K: KSEFSDK, data_od: str, data_do: str, subject: str) -> tuple[dict, str]:
        faktury_zakupowe = K.get_invoices_metadata(date_from=data_od, date_to=data_do, subject=subject)
        return {"faktury": faktury_zakupowe}, f"{data_od} - {data_do}"

    @ksef_action(action=E.CZYTANIE_FAKTUR_ZAKUPOWYCH)
    def czytaj_faktury_zakupowe(self, K: KSEFSDK, data_od: str, data_do: str) -> tuple[dict, str]:
        return self._czytaj_faktury(K, data_od, data_do, subject=KSEFSDK.SUBJECT2)

    @ksef_action(action=E.CZYTANIE_FAKTUR_SPRZEDAZY)
    def czytaj_faktury_sprzedazy(self, K: KSEFSDK, data_od: str, data_do: str) -> tuple[dict, str]:
        return self._czytaj_faktury(K, data_od, data_do, subject=KSEFSDK.SUBJECT1)

    def _zapisz_upo(self, ksef_numer: str, upo: str):
        upo_file = self.C.get_invoice_upo(self._nip, ksef_numer)
        with open(upo_file, mode="w") as f:
            self.logger.info(f"Zapisz UPO do {upo_file}")
            f.write(upo)

    def _zapamiętaj_fakture(self, ksef_numer: str, invoice_path: str):
        faktura_file = self.C.get_invoice_faktura(nip=self._nip, ksef_numer=ksef_numer)
        self.logger.info(f"Archiwizacja faktury {invoice_path} -> {faktura_file}")
        shutil.copyfile(invoice_path, faktura_file)

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
        self._zapisz_upo(ksef_numer=numer_ksef, upo=upo)
        K.close_session()
        self._zapamiętaj_fakture(ksef_numer=numer_ksef, invoice_path=invoice_path)

        return {"numer_ksef": numer_ksef}, numer_ksef

    def wez_upo(self, res_pathname: str, ksef_number: str) -> tuple[bool, str]:
        EV = self.genE(E.WEZ_UPO, output=res_pathname)
        upo_file = self.C.get_invoice_upo(self._nip, ksef_numer=ksef_number)
        errmess = None
        if not os.path.exists(upo_file):
            errmess = f"Plik {upo_file} nie istnieje"
        else:
            with open(upo_file, mode="r") as f:
                upo_xml = f.read()
                try:
                    et.fromstring(upo_xml)
                except Exception:
                    errmess = f"Plik {upo_file} nie jest poprawnym plikiem XML"
        if errmess is None:
            res = {"upo": upo_file}
            EV.koniec(True, upo_file, res_dict=res)
            return True, ""
        EV.koniec(False, errmess)
        return False, ""

    @ksef_action(action=E.WEZ_FAKTURE)
    def wez_fakture(self, K: KSEFSDK, ksef_number: str) -> tuple[dict, str]:
        invoice = K.get_invoice(ksef_number=ksef_number)
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(invoice.encode())
            return {"invoice": t.name}, ""

    @staticmethod
    def _czytaj_zbiorczo(K: KSEFSDK, data_od: str, data_do: str, subject: str) -> tuple[int, str | None]:
        liczba_faktur, zipped_dane = K.get_batch_invoices(date_from=data_od, date_to=data_do, subject=subject)
        if liczba_faktur == 0:
            return 0, None
        t = tempfile.mkdtemp()
        dir_name = t
        with zipfile.ZipFile(io.BytesIO(zipped_dane)) as z:
            for name in z.namelist():
                t_file = os.path.join(dir_name, name)
                t_data = z.read(name)
                with open(t_file, "wb") as t:
                    t.write(t_data)
        return liczba_faktur, dir_name

    @ksef_action(action=E.CZYTANIE_FAKTUR_ZBIORCZO)
    def czytaj_faktury_zbiorczo(self, K: KSEFSDK, data_od: str, data_do: str, subject: str) -> tuple[dict, str]:
        liczba_faktur, dir_name = self._czytaj_zbiorczo(K, data_od, data_do, subject)

        def _wynik(dir_name: str | None) -> tuple[dict, str]:
            mess = f"Znaleziono {liczba_faktur} faktur w okresie {data_od} - {data_do} dla subject {subject}"
            return {"katalog": dir_name, "liczba_faktur": liczba_faktur}, mess

        return _wynik(dir_name=dir_name)

    @ksef_action(action=E.CZYTANIE_FAKTUR_ZBIORCZO)
    def REMOVE_czytaj_faktury_zbiorczo(self, K: KSEFSDK, data_od: str, data_do: str, subject: str) -> tuple[dict, str]:
        liczba_faktur, zipped_dane = K.get_batch_invoices(date_from=data_od, date_to=data_do, subject=subject)

        def _wynik(dir_name: str | None) -> tuple[dict, str]:
            mess = f"Znaleziono {liczba_faktur} faktur w okresie {data_od} - {data_do} dla subject {subject}"
            return {"katalog": dir_name, "liczba_faktur": liczba_faktur}, mess

        if liczba_faktur == 0:
            return _wynik(dir_name=None)
        t = tempfile.mkdtemp()
        dir_name = t
        with zipfile.ZipFile(io.BytesIO(zipped_dane)) as z:
            for name in z.namelist():
                t_file = os.path.join(dir_name, name)
                t_data = z.read(name)
                with open(t_file, "wb") as t:
                    t.write(t_data)
        return _wynik(dir_name=dir_name)

    @ksef_action(action=E.WYSLIJ_WSADOWO)
    def wyslij_wsadowo_do_ksef(self, K: KSEFSDK, faktury_dir: str) -> tuple[dict, str]:

        files = os.listdir(faktury_dir)
        self.logger.info(f"Szukanie faktur w katalogu {faktury_dir}")

        faktury = []

        with tempfile.NamedTemporaryFile(delete=False) as t:
            with zipfile.ZipFile(t.name, "w", zipfile.ZIP_DEFLATED) as zip:
                for f in files:
                    if not f.endswith(".xml"):
                        continue
                    full_path = os.path.join(faktury_dir, f)
                    faktury.append(full_path)
                    self.logger.info(f"Faktura {full_path}")
                    zip.write(full_path)

        # teraz odczytuj
        maxPartSize = 100 * 1000 * 1000  # 100 MB

        def bytes_generator():
            with open(t.name, "rb") as z:
                b = z.read(maxPartSize)
                if b is None:
                    return
                yield b

        def _zapisz_upo(i: KSEFSDK.INVOICES, upo: str):
            numer_ksef = i.ksefNumber
            self._zapisz_upo(ksef_numer=numer_ksef, upo=upo)

        ok, err_mess, invoices = K.send_batch_session_bytes(payload=bytes_generator(), wez_upo=_zapisz_upo)
        os.unlink(t.name)
        if not ok and not invoices:
            raise ValueError(err_mess)

        # zapamiętaj źrodłowe faktury
        for i in [i for i in invoices if i.ok]:
            ksef_numer = i.ksefNumber
            i_number = i.ordinalNumer  # numerowane od 1
            self._zapamiętaj_fakture(ksef_numer=ksef_numer, invoice_path=faktury[i_number - 1])

        msg = f"Wysłano {len(invoices)}, błędnych {len([i for i in invoices if not i.ok])}"
        self.logger.info(msg)
        # zamien namedtuple na dictionary
        d_invoices = [d._asdict() for d in invoices]
        return {"invoices": d_invoices}, msg

    def daj_konfiguracje(self, output: str):
        errmess = None
        auth = "token"
        nip: NIP = self.nip
        ok: bool = True
        mess = "Skonfigurowane"
        try:
            token: TOKEN = odczytaj_tokny(self.C, nip.nip)
            if token.p12 is not None:
                auth = "certyfikat"
        except Exception as e:
            errmess = f"Połączenie z KSeF 2.0 nie jest skonfigurawane dla {nip.nip}"
            mess = "Nie jest skonfigurowane"
            self.logger.warning(errmess, e)
            ok = False
        res = {
            "auth": auth,
            "mess": mess,
            "env": token.env_s if ok else None,
            "files": {
                "ksef_conf": self.C.ksef_conf_path,
                "work_dir": self.C.work_nip_dir(nip),
                "events_file": self.C.get_nip_events_file(nip),
                "log_file": self.C.get_nip_log_file(nip),
                "work_zakupowe": self.C.zakupowe_dir_nip_subdir(nip),
            },
        }
        E.zapisz_res(output, res=ok, errmess=errmess, res_dict=res)
        return ok, mess

    @ksef_action(action=E.CZYTANIE_ZAKUPY_PRZYROSTOWO, enable_session=False)
    def daj_bufor_zakupowe(self, _: KSEFSDK) -> tuple[dict, str]:
        alist = self.odczytaj_wszystkie_faktury_zakupowe(self)
        max_data = self.daj_ostatnia_data(alist)
        msg = f"Liczba zakupowych {len(alist)}, ostatnia data: {max_data if max_data else 'bufor pusty'}"
        d_list = [d.metadata for d in alist]
        return {"invoices": d_list, "ostatnia_data": max_data}, msg

    @ksef_action(action=E.UAKTUALNIJ_ZAKUPY_PRZYROSTOWO)
    def uaktualnij_bufor_zakupowe(self, K: KSEFSDK) -> tuple[dict, str]:
        alist = self.odczytaj_wszystkie_faktury_zakupowe(self)
        max_data = self.daj_ostatnia_data(alist)
        date_from = _minus_days(60) if max_data is None else _iso_format_to_date(max_data)
        date_to = _tomorrow()
        self.logger.info(f"Odczyt faktur zakupowych od {date_from} do {date_to}")
        liczba_faktur, dir_name = self._czytaj_zbiorczo(
            K=K, data_od=date_from, data_do=date_to, subject=KSEFSDK.SUBJECT2
        )

        def _wynik(liczba_faktur: int) -> tuple[dict, str]:
            mess = (
                f"Znaleziono {liczba_faktur} nowych faktur "
                f"w okresie {date_from} - {date_to} dla subject {KSEFSDK.SUBJECT2}"
            )
            return {"liczba_faktur": liczba_faktur}, mess

        if liczba_faktur == 0:
            return _wynik(0)
        nlist = self.uaktualnij_faktury(self, alist, dir_name)
        return _wynik(len(nlist))

    @ksef_action(action=E.WEZ_FAKTURA_BUFOR, enable_session=False)
    def wez_bufor_faktura(self, _: KSEFSDK, ksef_number: str) -> tuple[dict, str]:
        faktura_path = self.daj_faktura_zakupowa_path(self, ksef_number)
        return {"faktura_path": faktura_path}, f"Faktura {ksef_number} z bufora zakupowego"
