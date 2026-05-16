import json
import os
import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import CONF, NIP
from ksef_cli.main import run_main

import helper as T


def _wez_res(output: str) -> dict:
    with open(output, "r") as f:
        return json.load(fp=f)


def _run_main_res(argv: list[str], output: str) -> tuple[bool, str]:
    T.ustaw_E()
    run_main(argv)
    d = _wez_res(output)
    return d["OK"], d["errmess"]


class AKsefCli:

    @staticmethod
    def wyczysc_dane(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def odczytaj_faktury_zakupowe(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def wez_fakture(C: CONF, output: str, nip: str, ksef_number: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def wez_upo(C: CONF, output: str, nip: str, ksef_numer: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def odczytaj_faktury_sprzedazy(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def odczytaj_faktury_zbiorczo(
            C: CONF, output: str, nip: str,
            data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def daj_konfiguracje(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def daj_bufor_zakupowe(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def uaktualnij_bufor_zakupowe(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        raise NotImplementedError

    @staticmethod
    def wez_faktura_bufor(C: CONF, output: str, nip: str, ksef_number: str) -> tuple[bool, str]:
        raise NotImplementedError


class TestKsefCli(AKsefCli):

    @staticmethod
    def odczytaj_faktury_zakupowe(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.czytaj_faktury_zakupowe(output=output, data_od=data_od, data_do=data_do)

    @staticmethod
    def wez_fakture(C: CONF, output: str, nip: str, ksef_number: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.wez_fakture(output=output, ksef_number=ksef_number)

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.wyslij_fakture_do_ksef(output=output, invoice_path=invoice_path)

    @staticmethod
    def wez_upo(C: CONF, output: str, nip: str, ksef_numer: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.wez_upo(res_pathname=output, ksef_number=ksef_numer)

    @staticmethod
    def odczytaj_faktury_sprzedazy(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.czytaj_faktury_sprzedazy(output=output, data_od=data_od, data_do=data_do)

    @staticmethod
    def odczytaj_faktury_zbiorczo(
            C: CONF, output: str, nip: str,
            data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.czytaj_faktury_zbiorczo(
            output=output, data_od=data_od, data_do=data_do, subject=subject)

    @staticmethod
    def daj_konfiguracje(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        return cli.daj_konfiguracje(output=output)


def _wynik_wsadowo(output, ok, errmsg) -> tuple[bool, str]:
    with open(output, "r") as f:
        d = json.load(fp=f)

    invoices = d.get("invoices", [])
    if len(invoices) == 0:
        return ok, errmsg
    assert 1 == len(invoices)
    i = invoices[0]
    d = {
        "OK": i["ok"],
        "errmess": i["msg"],
        "numer_ksef": i["ksefNumber"]
    }
    ok = i["ok"]
    if not ok:
        errmsg = i["msg"]
    with open(output, "w") as f:
        json.dump(d, f)
    return ok, errmsg


class TestWsadowoKsefCli(TestKsefCli):

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        tmp_dir = T.temp_dir()
        ok, errmsg = cli.wyslij_wsadowo_do_ksef(output=output, faktury_dir=tmp_dir)
        return _wynik_wsadowo(output, ok, errmsg)


class TestWsadowoMainKsefCli(TestKsefCli):

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        tmp_dir = T.temp_dir()
        argv = ["", "wyslij_wsadowo", nip, output, tmp_dir]
        ok, errmsg = _run_main_res(argv, output)
        return _wynik_wsadowo(output, ok, errmsg)


class TestKsefCliMain(AKsefCli):

    @staticmethod
    def wyczysc_dane(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        argv = ["", "wyczysc_dane", nip, output]
        return _run_main_res(argv, output)

    @staticmethod
    def odczytaj_faktury_zakupowe(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        argv = ["", "pobierz_zakupowe", nip, output, data_od, data_do]
        return _run_main_res(argv, output)

    @staticmethod
    def wez_fakture(C: CONF, output: str, nip: str, ksef_number: str) -> tuple[bool, str]:
        argv = ["", "odczytaj_fakture", nip, output, ksef_number]
        return _run_main_res(argv, output)

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        argv = ["", "wyslij_fakture", nip, output, invoice_path]
        return _run_main_res(argv, output)

    @staticmethod
    def wez_upo(C: CONF, output: str, nip: str, ksef_numer: str) -> tuple[bool, str]:
        argv = ["", "odczytaj_upo", nip, output, ksef_numer]
        return _run_main_res(argv, output)

    @staticmethod
    def odczytaj_faktury_sprzedazy(C: CONF, output: str, nip: str, data_od: str, data_do: str) -> tuple[bool, str]:
        argv = ["", "pobierz_sprzedazowe", nip, output, data_od, data_do]
        return _run_main_res(argv, output)

    @staticmethod
    def odczytaj_faktury_zbiorczo(
            C: CONF, output: str, nip: str,
            data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
        argv = ["", "pobierz_zbiorczo", nip, output, data_od, data_do, subject]
        return _run_main_res(argv, output)

    @staticmethod
    def daj_konfiguracje(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        argv = ["", "daj_konfiguracje", nip, output]
        return _run_main_res(argv, output)

    @staticmethod
    def daj_bufor_zakupowe(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        argv = ["", "daj_zakupowe_bufor", nip, output]
        return _run_main_res(argv, output)

    @staticmethod
    def uaktualnij_bufor_zakupowe(C: CONF, output: str, nip: str) -> tuple[bool, str]:
        argv = ["", "uaktualnij_zakupowe_bufor", nip, output]
        return _run_main_res(argv, output)

    @staticmethod
    def wez_faktura_bufor(C: CONF, output: str, nip: str, ksef_number: str) -> tuple[bool, str]:
        argv = ["", "wez_faktura_bufor", nip, output, ksef_number]
        return _run_main_res(argv, output)


class AbstractTestKSEFCLI:

    C: CONF

    def _test_odczytaj_faktury_zakupowe_brak_nip(self, A: AKsefCli):
        nip = "xxxxxxxxxxxx"
        res, msg = A.odczytaj_faktury_zakupowe(
            C=self.C, nip=nip, output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        assert not res
        print(msg)
        assert "Nie można odczytać tokena KSeF dla NIP" in msg

    def _test_odczytaj_faktury_zakupowe_bledy_token(self, A: AKsefCli):
        nip = "888888887"
        res, msg = A.odczytaj_faktury_zakupowe(
            C=self.C, nip=nip, output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        assert not res
        print(msg)

    def _test_pobierz_faktury_zakupowe(self, A: AKsefCli, nip=T.NIP):
        d_from, d_to = T.daj_przedzial()
        print(d_from, d_to)
        output = T.temp_ojosn()
        res = A.odczytaj_faktury_zakupowe(
            C=self.C, output=output, nip=nip, data_od=d_from, data_do=d_to)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        assert d["OK"]
        faktury = d["faktury"]
        invoice_meta = faktury[-1]
        ksef_number = invoice_meta["ksefNumber"]
        print(ksef_number)
        seller = invoice_meta["seller"]["nip"]
        assert T.NIP_NABYWCA == seller
        res = A.wez_fakture(C=self.C, output=output, nip=nip, ksef_number=ksef_number)
        print(res)
        d = _wez_res(output)
        print(d)
        assert d["OK"]
        invoice = d['invoice']
        with open(invoice, mode="r") as f:
            invoice_xml = f.read()
            print(invoice_xml)
            et.fromstring(invoice_xml)

    def _test_pobierz_faktury_sprzedazy(self, A: AKsefCli):
        d_from, d_to = T.daj_przedzial()
        print(d_from, d_to)
        nip = T.NIP
        output = T.temp_ojosn()
        res = A.odczytaj_faktury_sprzedazy(
            C=self.C, output=output, nip=nip, data_od=d_from, data_do=d_to)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        assert d["OK"]
        faktury = d["faktury"]
        invoice_meta = faktury[-1]
        print(invoice_meta)
        seller = invoice_meta["seller"]["nip"]
        assert T.NIP == seller

    def _test_wyslij_bledna_fakture(self, A: AKsefCli, errmess_contains="Błąd"):
        nip = T.NIP
        fa = T.NIEPOPRAWNA_FAKTURA
        invoice_path = T.testdatadir(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert not res[0]
        assert errmess_contains in res[1]
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        assert not d["OK"]
        assert errmess_contains in d["errmess"]

    def _test_wyslij_fakture_sprzedazy(self, A: AKsefCli, nip=T.NIP):
        fa = T.FAKTURA_WZORZEC
        invoice_path = T.prepare_invoice(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert res[0]
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        assert d["OK"]
        f_ksef = d["numer_ksef"]
        print(f_ksef)
        upo = self.C.get_invoice_upo(NIP(nip), f_ksef)
        with open(upo, "r") as f:
            upo_xml = f.read()
            et.fromstring(upo_xml)
        return cli, f_ksef, nip

    def _test_wez_upo_nie_istnieje(self, A: AKsefCli):
        nip = "aaaaaaaaaa"
        output = T.temp_ojosn()
        res = A.wez_upo(C=self.C, output=output, nip=nip, ksef_numer="bbbbbbb")
        print(res)
        assert not res[0]
        d = _wez_res(output)
        print(d)
        assert not d["OK"]

    def _test_wez_upo_dla_faktury(self, A: AKsefCli, nip=T.NIP):
        _, f_ksef, nip = self._test_wyslij_fakture_sprzedazy(A, nip=nip)
        output = T.temp_ojosn()
        res = A.wez_upo(C=self.C, output=output, nip=nip, ksef_numer=f_ksef)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        assert d["OK"]
        upo = d["upo"]
        with open(upo, "r") as f:
            _ = f.read()

    def _test_faktura_zakupowa_blad(self, A: AKsefCli):
        nip = T.NIP
        fa = T.FAKTURA_ZAKUP
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert not res[0]
        errmess = res[1]
        if 'Błąd weryfikacji, brak poprawnych faktur' not in errmess:
            assert "nie jest uprawniony do wystawienia faktury w imieniu" in errmess

    def _test_faktura_zakupowa(self, A: AKsefCli, nip=T.NIP_NABYWCA):
        fa = T.FAKTURA_ZAKUP
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert res[0]

    def _test_faktury_czytaj_zbiorcz_za_duzy_zakres(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2023-01-01"
        date_to = "2024-12-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        assert not res[0]
        assert "must not exceed 3 months" in res[1]

    def _test_faktury_czytaj_zbiorczo_brak_faktur(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2025-01-01"
        date_to = "2025-01-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        assert liczba_faktur == 0

    def _test_faktury_czytaj_zbiorczo_duzo_faktur(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2025-12-01"
        date_to = "2025-12-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        assert 0 < liczba_faktur
        katalog = d["katalog"]
        assert os.path.exists(katalog)
        faktury = os.listdir(katalog)
        is_metadata = False
        for f in faktury:
            f_path = os.path.join(katalog, f)
            print(f_path)
            with open(f_path, "r") as f:
                _ = f.read()
            if f_path.endswith("_metadata.json"):
                is_metadata = True
        assert is_metadata

    def _test_faktury_wyslij_i_czytaj_zbiorczo(self, A: AKsefCli, nip=T.NIP_NABYWCA):
        fa = T.FAKTURA_ZAKUP
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        numer_ksef = d["numer_ksef"]
        date_from, date_to = T.daj_przedzial()
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        assert 0 < liczba_faktur
        katalog = d["katalog"]
        assert os.path.exists(katalog)
        faktury = os.listdir(katalog)
        is_metadata = False
        is_faktura_ksef = False
        for f in faktury:
            f_path = os.path.join(katalog, f)
            print(f_path)
            with open(f_path, "r") as f:
                _ = f.read()
            if f_path.endswith("_metadata.json"):
                is_metadata = True
            if numer_ksef in f_path:
                is_faktura_ksef = True
        assert is_faktura_ksef
        assert is_metadata

    def _test_sprawdz_konfiguracje(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        res = A.daj_konfiguracje(C=self.C, output=output, nip=nip)
        print(res)
        assert res[0]
        res = A.daj_konfiguracje(C=self.C, output=output, nip=T.NIPDIR)
        print(res)
        assert res[0]
        res = A.daj_konfiguracje(C=self.C, output=output, nip="XXXX")
        print(res)
        assert not res[0]

    def _test_wez_bufor_zakupowe(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)

    def _test_uaktualnij_bufor_zakupowe_zero(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        assert "0 nowych faktur" in res[1]

    def _test_uaktualnij_bufor_zakupowe(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        print(d)
        invoices = d["invoices"]
        assert len(invoices) == 0

        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)

        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices = d["invoices"]

        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        assert "0 nowych faktur" in res[1]
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices1 = d["invoices"]
        assert len(invoices) == len(invoices1)

        no = 0
        for e in invoices:
            if no > 100:
                break
            no += 1
            ksef_number = e["ksefNumber"]
            res = A.wez_faktura_bufor(C=self.C, output=output, nip=nip, ksef_number=ksef_number)
            print(res)
            assert res[0]
            d = _wez_res(output)
            print(d)
            invoice = d["faktura_path"]
            with open(invoice, "r") as f:
                invoice_xml = f.read()
                et.fromstring(invoice_xml)

    def _test_bufor_zakupowe_wez_jeden(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        d = _wez_res(output)
        invoices = d["invoices"]

        fa = T.FAKTURA_WZORZEC
        invoice_path, invoice_num = T.prepare_invoice_faktur(fa, "faktura.xml")

        res = A.wyslij_fakture(C=self.C, output=output, nip=T.NIPDIR, invoice_path=invoice_path)
        print(res)

        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        assert res[0]
        assert "1 nowych faktur" in res[1]
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices1 = d["invoices"]
        assert len(invoices1) == len(invoices) + 1

        faktura = next(f for f in invoices1 if f["invoiceNumber"] == invoice_num)
        print(faktura)

    def _test_wyslij_zduplikowana_fakture(self, A: AKsefCli):
        nip = T.NIPDIR
        fa = T.FAKTURA_WZORZEC
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        numer_ksef = d["numer_ksef"]
        print(numer_ksef)

        res = A.wyslij_fakture(C=self.C, output=output, nip=nip, invoice_path=invoice_path)
        print(res)
        ok = res[0]
        msg = res[1]
        if not ok:
            assert "Duplikat faktury" in msg
        else:
            assert "błędnych 1" in msg
        d = _wez_res(output)
        print(d)
        assert not d["OK"]
        assert "Duplikat faktury" in d["errmess"]
