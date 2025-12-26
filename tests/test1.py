import datetime

import json

import unittest

import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import CONF
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
    print(d)
    return d["OK"], d["errmess"]


class AKsefCli:

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


class AbstractTestKSEFCLI(unittest.TestCase):

    # -------------
    # test fixture
    # -------------
    @classmethod
    def setUpClass(cls):
        cls.C = T.CO()

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

    def _test_pobierz_faktury_zakupowe(self, A: AKsefCli):
        d2 = datetime.datetime.now() + datetime.timedelta(days=2)
        d1 = d2 - datetime.timedelta(days=7)
        d_from = d1.strftime("%Y-%m-%d")
        d_to = d2.strftime("%Y-%m-%d")
        print(d_from, d_to)
        nip = T.NIP
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

    def _test_wyslij_bledna_fakture(self, A: AKsefCli):
        nip = T.NIP
        fa = T.NIEPOPRAWNA_FAKTURA
        invoice_path = T.testdatadir(fa)
        output = T.temp_ojosn()
        res = A.wyslij_fakture(C=self.C, output=output,
                               nip=nip, invoice_path=invoice_path)
        print(res)
        self.assertFalse(res[0])
        self.assertIn("Błąd", res[1])
        # sprawdz, czy jest utworzony output
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        self.assertFalse(d["OK"])
        self.assertIn("Błąd", d["errmess"])

    def _test_wyslij_fakture_sprzedazy(self, A: AKsefCli):
        nip = T.NIP
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
        upo = self.C.get_invoice_upo(nip, f_ksef)
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

    def _test_wez_upo_dla_faktury(self, A: AKsefCli):
        _, f_ksef, nip = self._test_wyslij_fakture_sprzedazy(A)
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

    def _test_faktura_zakupowa(self, A: AKsefCli):
        nip = T.NIP_NABYWCA
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


class TestKSEFCli(AbstractTestKSEFCLI):

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
        self._test_wyslij_bledna_fakture(self.AT)

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


class TestKSEFCliMain(AbstractTestKSEFCLI):

    AM = TestKsefCliMain()

    def test_main_odczytaj_faktury_zakupowe_brak_nip(self):
        self._test_odczytaj_faktury_zakupowe_brak_nip(self.AM)

    def test_main_odczytaj_faktury_zakupowe_bledy_token(self):
        self._test_odczytaj_faktury_zakupowe_bledy_token(self.AM)

    def test_main_wyslij_bledna_fakture(self):
        self._test_wyslij_bledna_fakture(self.AM)

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


class TestKSEFWsadowe(AbstractTestKSEFCLI):

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


class TestKSEFWsadowoMain(AbstractTestKSEFCLI):

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

    # wygląda, że w wersji testowej można maksymalnie wysłać 10 faktury
    NO = 10

    def _przygotuj_paczke(self):
        T.temp_dir_remove_xml()
        invoices = []
        fa = T.FAKTURA_WZORZEC
        for i in range(self.NO):
            faktura = f'faktura{i}.xml'
            _, invoice = T.prepare_invoice_faktur(patt=fa, faktura=faktura)
            invoices.append(invoice)
        return invoices

    def test_wysylka_wiele_faktur(self):
        invoices_names = self._przygotuj_paczke()
        nip = T.NIP
        tmp_dir = T.temp_dir()
        output = T.temp_ojosn()
        argv = ["", "wyslij_wsadowo", nip, output, tmp_dir]
        ok, errmsg = _run_main_res(argv, output)
        self.assertTrue(ok)
        with open(output, "r") as f:
            d = json.load(fp=f)

        invoices = d.get("invoices", [])
        self.assertEqual(self.NO, len(invoices))
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
                

                





