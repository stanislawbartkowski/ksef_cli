import json

import os
import unittest

import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import CONF, NIP
from ksef_cli.ksef_tokens import odczytaj_tokny
from ksef_cli.main import run_main

import helper as T


def _wez_res(output: str) -> dict:
    with open(output, "r") as f:
        d = json.load(fp=f)
        return d


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
    def odczytaj_faktury_zbiorczo(C: CONF, output: str, nip: str, data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
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
        return cli.czytaj_faktury_zakupowe(
            output=output, data_od=data_od, data_do=data_do)

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
        return cli.czytaj_faktury_sprzedazy(
            output=output, data_od=data_od, data_do=data_do)

    @staticmethod
    def odczytaj_faktury_zbiorczo(C: CONF, output: str, nip: str, data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
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
    with open(output, "w") as f:
        json.dump(d, f)
    return ok, errmsg


class TestWsadowoKsefCli(TestKsefCli):

    @staticmethod
    def wyslij_fakture(C: CONF, output: str, nip: str, invoice_path: str) -> tuple[bool, str]:
        cli = KSEFCLI(C, nip)
        tmp_dir = T.temp_dir()
        ok, errmsg = cli.wyslij_wsadowo_do_ksef(
            output=output, faktury_dir=tmp_dir)
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
    def odczytaj_faktury_zbiorczo(C: CONF, output: str, nip: str, data_od: str, data_do: str, subject: str) -> tuple[bool, str]:
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


class TokenKsefCO(unittest.TestCase):

    # -------------
    # test fixture
    # -------------
    @classmethod
    def setUpClass(cls):
        cls.C = T.CO()


class CertKsefCO(unittest.TestCase):

    # -------------
    # test fixture
    # -------------
    @classmethod
    def setUpClass(cls):
        cls.C = T.CO_CERT()


class AbstractTestKSEFCLI(unittest.TestCase):

    # -----------------
    # abstract testy
    # -----------------
    def _test_odczytaj_faktury_zakupowe_brak_nip(self, A: AKsefCli):
        nip = "xxxxxxxxxxxx"
        res, msg = A.odczytaj_faktury_zakupowe(
            C=self.C, nip=nip, output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        self.assertFalse(res)
        print(msg)
        self.assertIn("Nie można odczytać tokena KSeF dla NIP", msg)

    def _test_odczytaj_faktury_zakupowe_bledy_token(self, A: AKsefCli):
        nip = "888888887"
        res, msg = A.odczytaj_faktury_zakupowe(
            C=self.C, nip=nip, output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        self.assertFalse(res)
        print(msg)

    def _test_pobierz_faktury_zakupowe(self, A: AKsefCli, nip=T.NIP):
        d_from, d_to = T.daj_przedzial()
        print(d_from, d_to)
        output = T.temp_ojosn()
        res = A.odczytaj_faktury_zakupowe(
            C=self.C, output=output, nip=nip, data_od=d_from, data_do=d_to)
        print(res)
        self.assertTrue(res[0])
        # sprawdz wynik
        d = _wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        faktury = d["faktury"]
        # wez ostatnią
        invoice_meta = faktury[-1]
        ksef_number = invoice_meta["ksefNumber"]
        print(ksef_number)

        seller = invoice_meta["seller"]["nip"]
        # czy na pewno nip sprzedawcy
        self.assertEqual(T.NIP_NABYWCA, seller)

        res = A.wez_fakture(C=self.C, output=output,
                            nip=nip, ksef_number=ksef_number)
        print(res)
        d = _wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        # odczytaj invoice
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
        self.assertTrue(res[0])
        # teraz sprawdz wynik
        d = _wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        faktury = d["faktury"]
        invoice_meta = faktury[-1]
        print(invoice_meta)
        seller = invoice_meta["seller"]["nip"]
        # czy na pewno nip sprzedawcy
        self.assertEqual(T.NIP, seller)

    def _test_wyslij_bledna_fakture(self, A: AKsefCli, errmess_contains="Błąd"):
        nip = T.NIP
        fa = T.NIEPOPRAWNA_FAKTURA
        invoice_path = T.testdatadir(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        self.assertFalse(res[0])
        self.assertIn(errmess_contains, res[1])
        # sprawdz, czy jest utworzony output
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        self.assertFalse(d["OK"])
        self.assertIn(errmess_contains, d["errmess"])

    def _test_wyslij_fakture_sprzedazy(self, A: AKsefCli, nip=T.NIP):
        fa = T.FAKTURA_WZORZEC
        invoice_path = T.prepare_invoice(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        self.assertTrue(res[0])
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        self.assertTrue(d["OK"])
        f_ksef = d["numer_ksef"]
        print(f_ksef)
        # sprawdz, czy odczytane upo
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
        self.assertFalse(res[0])
        d = _wez_res(output)
        print(d)
        self.assertFalse(d["OK"])

    def _test_wez_upo_dla_faktury(self, A: AKsefCli, nip=T.NIP):
        _, f_ksef, nip = self._test_wyslij_fakture_sprzedazy(A, nip=nip)
        # teraz wez upo
        output = T.temp_ojosn()
        res = A.wez_upo(C=self.C, output=output, nip=nip, ksef_numer=f_ksef)
        print(res)
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        # teraz sprawdz upo
        upo = d["upo"]
        # sprobuj odczytac
        with open(upo, "r") as f:
            _ = f.read()

    def _test_faktura_zakupowa_blad(self, A: AKsefCli):
        nip = T.NIP
        fa = T.FAKTURA_ZAKUP
        # faktura, z zamienionym nipem nabywcy i sprzedawcy
        # NIP - nabywca, NIP_NABYWCA - sprzedawca
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        # tutaj jest błąd, gdy próba wystawienia faktury w cudzym imieniu
        self.assertFalse(res[0])
        errmess = res[1]
        if 'Błąd weryfikacji, brak poprawnych faktur' not in errmess:
            self.assertIn(
                "nie jest uprawniony do wystawienia faktury w imieniu", errmess)

    def _test_faktura_zakupowa(self, A: AKsefCli, nip=T.NIP_NABYWCA):
        fa = T.FAKTURA_ZAKUP
        # faktura, z zamienionym nipem nabywcy i sprzedawcy
        # NIP - nabywca, NIP_NABYWCA - sprzedawca
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        # tutaj jest błąd, gdy próba wystawienia faktury w cudzym imieniu
        self.assertTrue(res[0])

    def _test_faktury_czytaj_zbiorcz_za_duzy_zakres(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2023-01-01"
        date_to = "2024-12-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        # tutaj jest błąd, za duży zakres dat
        self.assertFalse(res[0])
        self.assertIn("must not exceed 3 months", res[1])

    def _test_faktury_czytaj_zbiorczo_brak_faktur(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2025-01-01"
        date_to = "2025-01-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        # brak faktur, ale OK
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        self.assertEqual(0, liczba_faktur)

    def _test_faktury_czytaj_zbiorczo_duzo_faktur(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        date_from = "2025-12-01"
        date_to = "2025-12-31"
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        # brak faktur, ale OK
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        self.assertLess(0, liczba_faktur)
        katalog = d["katalog"]
        self.assertTrue(os.path.exists(katalog))
        # sprawdz, czy jest tam faktura
        faktury = os.listdir(katalog)
        is_metadata = False
        for f in faktury:
            f_path = os.path.join(katalog, f)
            print(f_path)
            with open(f_path, "r") as f:
                _ = f.read()
            if f_path.endswith("_metadata.json"):
                is_metadata = True
        self.assertTrue(is_metadata)

    def _test_faktury_wyslij_i_czytaj_zbiorczo(self, A: AKsefCli, nip=T.NIP_NABYWCA):
        fa = T.FAKTURA_ZAKUP
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        numer_ksef = d["numer_ksef"]
        # teraz odczytaj zbiorczo
        date_from, date_to = T.daj_przedzial()
        subject = "Subject1"
        res = A.odczytaj_faktury_zbiorczo(
            C=self.C, output=output, nip=nip, data_od=date_from, data_do=date_to, subject=subject)
        print(res)
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        liczba_faktur = d["liczba_faktur"]
        self.assertLess(0, liczba_faktur)
        katalog = d["katalog"]
        self.assertTrue(os.path.exists(katalog))
        # sprawdz, czy jest tam faktura
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
        self.assertTrue(is_faktura_ksef)
        self.assertTrue(is_metadata)

    def _test_sprawdz_konfiguracje(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
        output = T.temp_ojosn()
        res = A.daj_konfiguracje(C=self.C, output=output, nip=nip)
        print(res)
        self.assertTrue(res[0])

        res = A.daj_konfiguracje(C=self.C, output=output, nip=T.NIPDIR)
        print(res)
        self.assertTrue(res[0])

        res = A.daj_konfiguracje(C=self.C, output=output, nip="XXXX")
        print(res)
        self.assertFalse(res[0])

    def _test_wez_bufor_zakupowe(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)

    def _test_uaktualnij_bufor_zakupowe_zero(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        # wyczysc dane
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        # jeszcze raz - powinno być 0
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        self.assertIn("0 nowych faktur", res[1])

    def _test_uaktualnij_bufor_zakupowe(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        # wyczysc dane
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        # we zakupowe powinny być puste
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        print(d)
        invoices = d["invoices"]
        self.assertEqual(0, len(invoices))

        # teraz uaktualnij
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)

        # teraz odczytaj ponownie zakupowe, powinny być faktury
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices = d["invoices"]

        # teraz odczytaj drugi raz
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        # nic nie odczytano
        self.assertIn("0 nowych faktur", res[1])
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices1 = d["invoices"]
        self.assertEqual(len(invoices), len(invoices1))

        # teraz odczytak faktura z bufora
        # tylko pierwsze 100
        no = 0
        for e in invoices:
            if no > 100:
                break
            no += 1
            ksef_number = e["ksefNumber"]
            res = A.wez_faktura_bufor(
                C=self.C, output=output, nip=nip, ksef_number=ksef_number)
            print(res)
            self.assertTrue(res[0])
            d = _wez_res(output)
            print(d)
            invoice = d["faktura_path"]
            with open(invoice, "r") as f:
                invoice_xml = f.read()
                et.fromstring(invoice_xml)

    def _test_bufor_zakupowe_wez_jeden(self, A: AKsefCli):
        nip = T.NIP_NABYWCADIR
        output = T.temp_ojosn()
        # wyczysc dane
        A.wyczysc_dane(C=self.C, output=output, nip=nip)
        # teraz uaktualnij
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        d = _wez_res(output)
        invoices = d["invoices"]

        # teraz wystaw fakture sprzedazy
        fa = T.FAKTURA_WZORZEC
        invoice_path, invoice_num = T.prepare_invoice_faktur(fa, "faktura.xml")

        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=T.NIPDIR, invoice_path=invoice_path)
        print(res)

        # teraz uaktualnij
        res = A.uaktualnij_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        self.assertTrue(res[0])
        self.assertIn("1 nowych faktur", res[1])
        # teraz odczytaj ponownie zakupowe, powinny być faktury
        res = A.daj_bufor_zakupowe(C=self.C, output=output, nip=nip)
        print(res)
        d = _wez_res(output)
        invoices1 = d["invoices"]
        # jedna więcej
        self.assertEqual(len(invoices) + 1, len(invoices1))

        # wyszukaj nową fakturę
        faktura = next(
            f for f in invoices1 if f["invoiceNumber"] == invoice_num)
        print(faktura)

    def _test_wyslij_zduplikowana_fakture(self, A: AKsefCli):
        nip = T.NIPDIR
        fa = T.FAKTURA_WZORZEC
        invoice_path = T.prepare_invoice(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        numer_ksef = d["numer_ksef"]
        print(numer_ksef)

        # teraz wysylam drugi raz
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        ok = res[0]
        msg = res[1]
        if not ok:
            self.assertIn("Duplikat faktury", msg)
        else:
            self.assertIn("błędnych 1", msg)
        d = _wez_res(output)
        print(d)
        self.assertFalse(d["OK"])
        self.assertIn("Duplikat faktury", d["errmess"])


class TestKSEFCli(TokenKsefCO, AbstractTestKSEFCLI):

    AT = TestKsefCli()

    # ------------
    # test suite
    # ------------

    def test_token_nip_no(self):
        # Test with a non existing NIP number
        self.assertRaises(
            KeyError, lambda: odczytaj_tokny(self.C, "1234567890"))

    def test_token_nip_wrong_env(self):
        # Test with a not correcrt environment for the NIP number
        self.assertRaises(
            ValueError, lambda: odczytaj_tokny(self.C, "9999999997"))

    def test_token_nip_end_env(self):
        # Test with a not correcrt environment for the NIP number
        token = odczytaj_tokny(self.C, "888888887")
        print(token)
        self.assertEqual(token.env, 0)
        self.assertEqual(token.token, 'xxxxxxxxxxxx')

    def test_usun_katalog_roboczy(self):
        nip = "777777776"
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        cli.clean_nip_dir(res_pathname=output)

    def test_odczytaj_faktury_zakupowe_brak_nip(self):
        self._test_odczytaj_faktury_zakupowe_brak_nip(self.AT)

    def test_odczytaj_faktury_zakupowe_bledy_token(self):
        self._test_odczytaj_faktury_zakupowe_bledy_token(self.AT)

    def test_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(
            self.AT, errmess_contains="nie jest uprawniony do wystawienia faktury w imieniu")

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.AT)

    def test_wez_upo_nie_istnieje(self):
        self._test_wez_upo_nie_istnieje(self.AT)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.AT)

    def test_faktura_zakupowa_blad(self):
        self._test_faktura_zakupowa_blad(self.AT)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AT)

    def test_pobierz_faktury_zakupowe(self):
        self._test_pobierz_faktury_zakupowe(self.AT)

    def test_pobierz_faktury_sprzedazy(self):
        self._test_pobierz_faktury_sprzedazy(self.AT)

    # -------------------------------

    def test_faktury_czytaj_zbiorcz_za_duzy_zakres(self):
        self._test_faktury_czytaj_zbiorcz_za_duzy_zakres(self.AT)

    def test_faktury_czytaj_zbiorczo_brak_faktur(self):
        return super()._test_faktury_czytaj_zbiorczo_brak_faktur(self.AT)

    def test_faktury_czytaj_zbiorczo_duzo_faktur(self):
        return super()._test_faktury_czytaj_zbiorczo_duzo_faktur(self.AT)

    def test_faktury_wyslij_i_czytaj_zbiorczo(self):
        return super()._test_faktury_wyslij_i_czytaj_zbiorczo(self.AT)

    def test_sprawdz_konfiguracje(self):
        self._test_sprawdz_konfiguracje(self.AT)


class TestKSEFCliCert(CertKsefCO, AbstractTestKSEFCLI):

    AT = TestKsefCli()

    # ------------
    # test suite
    # ------------

    def test_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(
            self.AT, errmess_contains="Nieprawidłowy zakres uprawnień Kontekst")

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.AT)

    def test_wez_upo_nie_istnieje(self):
        self._test_wez_upo_nie_istnieje(self.AT)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.AT)

    def test_faktura_zakupowa_blad(self):
        self._test_faktura_zakupowa_blad(self.AT)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AT)

    def test_pobierz_faktury_zakupowe(self):
        self._test_pobierz_faktury_zakupowe(self.AT)

    def test_pobierz_faktury_sprzedazy(self):
        self._test_pobierz_faktury_sprzedazy(self.AT)


class TestKSEFCliCertNIPDIR(CertKsefCO, AbstractTestKSEFCLI):

    AT = TestKsefCli()

    def _weryfikuj_konfiguracje(self, nip):
        output = T.temp_ojosn()
        res = self.AT.daj_konfiguracje(C=self.C, output=output, nip=nip)
        print(res)
        self.assertTrue(res[0])
        d = _wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        files = d["files"]
        self.assertEqual("test", d["env"])
        nip_N = NIP(nip)
        self.assertEqual(self.C.ksef_conf_path, files["ksef_conf"])
        self.assertEqual(self.C.work_nip_dir(nip_N), files["work_dir"])
        self.assertEqual(self.C.get_nip_events_file(
            nip_N), files["events_file"])
        self.assertEqual(self.C.get_nip_log_file(nip_N), files["log_file"])
        # sprawdz, czy w ściece jest nip i YYYY
        self.assertIn(T.NIP, files["events_file"])
        self.assertIn("YYYY", files["events_file"])
        self.assertIn(T.NIP, files["log_file"])
        self.assertIn("YYYY", files["log_file"])

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.AT, nip=T.NIPDIR)
        self._weryfikuj_konfiguracje(T.NIPDIR)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.AT, nip=T.NIPDIR)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AT, nip=T.NIP_NABYWCADIR)

    def test_pobierz_faktury_zakupowe(self):
        self._test_pobierz_faktury_zakupowe(self.AT, nip=T.NIPDIR)

    def test_faktury_wyslij_i_czytaj_zbiorczo(self):
        return super()._test_faktury_wyslij_i_czytaj_zbiorczo(self.AT, nip=T.NIP_NABYWCADIR)


class TestKSEFCliMain(TokenKsefCO, AbstractTestKSEFCLI):

    AM = TestKsefCliMain()

    def test_main_odczytaj_faktury_zakupowe_brak_nip(self):
        self._test_odczytaj_faktury_zakupowe_brak_nip(self.AM)

    def test_main_odczytaj_faktury_zakupowe_bledy_token(self):
        self._test_odczytaj_faktury_zakupowe_bledy_token(self.AM)

    def test_main_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(
            self.AM, errmess_contains="nie jest uprawniony do wystawienia faktury w imieniu")

    def test_main_pobierz_faktury_zakupowe(self):
        self._test_pobierz_faktury_zakupowe(self.AM)

    def test_main_wyslij_fakture_sprzedazy(self):
        return self._test_wyslij_fakture_sprzedazy(self.AM)

    def test_main_wez_upo_nie_istnieje(self):
        return self._test_wez_upo_nie_istnieje(self.AM)

    def test_main_wez_upo_dla_faktury(self):
        return self._test_wez_upo_dla_faktury(self.AM)

    def test_main_faktura_zakupowa_blad(self):
        return self._test_faktura_zakupowa_blad(self.AM)

    def test_main_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AM)

    def test_pobierz_faktury_sprzedazy(self):
        self._test_pobierz_faktury_sprzedazy(self.AM)

    def test_faktury_czytaj_zbiorcz_za_duzy_zakres(self):
        self._test_faktury_czytaj_zbiorcz_za_duzy_zakres(self.AM)

    def test_faktury_czytaj_zbiorczo_brak_faktur(self):
        return super()._test_faktury_czytaj_zbiorczo_brak_faktur(self.AM)

    def test_faktury_czytaj_zbiorczo_duzo_faktur(self):
        return super()._test_faktury_czytaj_zbiorczo_duzo_faktur(self.AM)

    def test_faktury_wyslij_i_czytaj_zbiorczo(self):
        return super()._test_faktury_wyslij_i_czytaj_zbiorczo(self.AM)

    def test_sprawdz_konfiguracje(self):
        self._test_sprawdz_konfiguracje(self.AM)

    def test_wez_bufor_zakupowe(self):
        self._test_wez_bufor_zakupowe(self.AM)

    def test_uaktualnij_bufor_zakupowe_zero(self):
        self._test_uaktualnij_bufor_zakupowe_zero(self.AM)

    def test_uaktualnij_bufor_zakupowe(self):
        self._test_uaktualnij_bufor_zakupowe(self.AM)

    def test_bufor_zakupowe_wez_jeden(self):
        self._test_bufor_zakupowe_wez_jeden(self.AM)

    def test_wyslij_zduplikowana_fakture(self):
        self._test_wyslij_zduplikowana_fakture(self.AM)


class TestKSEFWsadowe(TokenKsefCO, AbstractTestKSEFCLI):

    AW = TestWsadowoKsefCli()

    def test_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(self.AW)

    def test_wyslij_fakture_sprzedazy(self):
        return self._test_wyslij_fakture_sprzedazy(self.AW)

    def test_wez_upo_dla_faktury(self):
        return self._test_wez_upo_dla_faktury(self.AW)

    def test_faktura_zakupowa_blad(self):
        return self._test_faktura_zakupowa_blad(self.AW)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AW)


class TestKSEFWsadowoMain(TokenKsefCO, AbstractTestKSEFCLI):

    AW = TestWsadowoMainKsefCli()

    def test_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(self.AW)

    def test_wyslij_fakture_sprzedazy(self):
        return self._test_wyslij_fakture_sprzedazy(self.AW)

    def test_wez_upo_dla_faktury(self):
        return self._test_wez_upo_dla_faktury(self.AW)

    def test_faktura_zakupowa_blad(self):
        return self._test_faktura_zakupowa_blad(self.AW)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AW)

    def test_wyslij_zduplikowana_fakture(self):
        self._test_wyslij_zduplikowana_fakture(self.AW)


class TestKSEFWsadowoDuzoFaktur(unittest.TestCase):

    # -------------
    # test fixture
    # -------------
    @classmethod
    def setUpClass(cls):
        cls.C = T.CO()

    # -------------
    # test suite
    # -------------

    # wygląda, że w wersji testowej można maksymalnie wysłać 10 faktur
    NO = 10

    def _przygotuj_paczke(self, no):
        T.temp_dir_remove_xml()
        invoices = []
        fa = T.FAKTURA_WZORZEC
        for i in range(no):
            faktura = f'faktura{i}.xml'
            _, invoice = T.prepare_invoice_faktur(patt=fa, faktura=faktura)
            invoices.append(invoice)
        return invoices

    def test_wysylka_wiele_faktur(self, no=NO):
        invoices_names = self._przygotuj_paczke(no)
        nip = T.NIP
        tmp_dir = T.temp_dir()
        output = T.temp_ojosn()
        argv = ["", "wyslij_wsadowo", nip, output, tmp_dir]
        ok, errmsg = _run_main_res(argv, output)
        self.assertTrue(ok)
        with open(output, "r") as f:
            d = json.load(fp=f)

        invoices = d.get("invoices", [])
        self.assertEqual(no, len(invoices))
        cli = KSEFCLI(self.C, nip)
        for i in invoices:
            print(i)
            ok = i["ok"]
            invoiceNumber = i["invoiceNumber"]
            self.assertIn(invoiceNumber, invoices_names)
            ksefNumber = i["ksefNumber"]
            # wez upo
            output = T.temp_ojosn()
            upo = cli.wez_upo(res_pathname=output, ksef_number=ksefNumber)
            d = _wez_res(output)
            upo = d["upo"]
            # sprobuj odczytac
            with open(upo, "r") as f:
                upo_xml = f.read()
                et.fromstring(upo_xml)
        return invoices_names

    def test_wysyla_wiele_zduplikowane(self):
        self.test_wysylka_wiele_faktur(no=1)
        # wyslij drugi raz
        nip = T.NIP
        tmp_dir = T.temp_dir()
        output = T.temp_ojosn()
        argv = ["", "wyslij_wsadowo", nip, output, tmp_dir]
        ok, errmsg = _run_main_res(argv, output)
        self.assertTrue(ok)
        with open(output, "r") as f:
            d = json.load(fp=f)

        invoices = d.get("invoices", [])
        print(invoices)
        i = invoices[0]
        self.assertFalse(i["ok"])
        self.assertIn("Duplikat faktury", i["msg"])
