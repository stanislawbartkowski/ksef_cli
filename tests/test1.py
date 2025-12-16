import datetime

import json

import unittest

import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_tokens import odczytaj_tokny

import helper as T


class TestKSEFCLI(unittest.TestCase):

    # -------------
    # helpers
    # -------------

    @staticmethod
    def _wez_res(output: str) -> dict:
        with open(output, "r") as f:
            d = json.load(fp=f)
        return d

    # -------------
    # test fixture
    # -------------
    @classmethod
    def setUpClass(cls):
        cls.C = T.CO()

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
        cli.clean_nip_dir()

    def test_odczytaj_faktury_zakupowe_brak_nip(self):
        nip = "xxxxxxxxxxxx"
        cli = KSEFCLI(self.C, nip)
        res, msg = cli.czytaj_faktury_zakupowe(
            output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        self.assertFalse(res)
        print(msg)
        self.assertIn("Nie można odczytać tokena KSeF dla NIP", msg)

    def test_odczytaj_faktury_zakupowe_bledy_token(self):
        nip = "888888887"
        cli = KSEFCLI(self.C, nip)
        res, msg = cli.czytaj_faktury_zakupowe(
            output="xxxxxx", data_od="2023-01-01", data_do="2023-12-31")
        self.assertFalse(res)
        print(msg)

    def test_wyslij_bledna_fakture(self):
        nip = T.NIP
        fa = T.NIEPOPRAWNA_FAKTURA
        invoice_path = T.testdatadir(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wyslij_fakture_do_ksef(
            output=output, invoice_path=invoice_path)
        print(res)
        self.assertFalse(res[0])
        self.assertIn("Błąd", res[1])
        # sprawdz, czy jest utworzony output
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        self.assertFalse(d["OK"])
        self.assertIn("Błąd", d["errmess"])

    def test_wyslij_fakture_sprzedazy(self):
        nip = T.NIP
        fa = T.FAKTURA_WZORZEC
        invoice_path = T.prepare_invoice(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wyslij_fakture_do_ksef(
            output=output, invoice_path=invoice_path)
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
        return cli, f_ksef

    def test_wez_upo_nie_istnieje(self):
        nip = "aaaaaaaaaa"
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wez_upo(res_pathname=output, ksef_number="bbbbbbb")
        print(res)
        self.assertFalse(res[0])
        d = self._wez_res(output)
        print(d)
        self.assertFalse(d["OK"])

    def test_wez_upo_dla_faktury(self):
        cli, f_ksef = self.test_wyslij_fakture_sprzedazy()
        # teraz wez upo
        output = T.temp_ojosn()
        res = cli.wez_upo(res_pathname=output, ksef_number=f_ksef)
        print(res)
        self.assertTrue(res[0])
        d = self._wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        # teraz sprawdz upo
        upo = d["upo"]
        # sprobuj odczytac
        with open(upo, "r") as f:
            _ = f.read()

    def test_faktura_zakupowa_blad(self):
        nip = T.NIP
        fa = T.FAKTURA_ZAKUP
        # faktura, z zamienionym nipem nabywcy i sprzedawcy
        # NIP - nabywca, NIP_NABYWCA - sprzedawca
        invoice_path = T.prepare_invoice(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wyslij_fakture_do_ksef(
            output=output, invoice_path=invoice_path)
        print(res)
        # tutaj jest błąd, gdy próba wystawienia faktury w cudzym imieniu
        self.assertFalse(res[0])
        errmess = res[1]
        self.assertIn(
            "nie jest uprawniony do wystawienia faktury w imieniu", errmess)

    def test_faktura_zakupowa(self):
        nip = T.NIP_NABYWCA
        fa = T.FAKTURA_ZAKUP
        # faktura, z zamienionym nipem nabywcy i sprzedawcy
        # NIP - nabywca, NIP_NABYWCA - sprzedawca
        invoice_path = T.prepare_invoice(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wyslij_fakture_do_ksef(
            output=output, invoice_path=invoice_path)
        print(res)
        # tutaj jest błąd, gdy próba wystawienia faktury w cudzym imieniu
        self.assertTrue(res[0])

    def test_pobierz_faktury_zakupowe(self):
        d2 = datetime.datetime.now() + datetime.timedelta(days=2)
        d1 = d2 - datetime.timedelta(days=7)
        d_from = d1.strftime("%Y-%m-%d")
        d_to = d2.strftime("%Y-%m-%d")
        print(d_from, d_to)
        nip = T.NIP
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.czytaj_faktury_zakupowe(
            output=output, data_od=d_from, data_do=d_to)
        print(res)
        self.assertTrue(res[0])
        # sprawdz wynik
        d = self._wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        faktury = d["faktury"]
        # wez ostatnią
        invoice_meta = faktury[-1]
        ksef_number = invoice_meta["ksefNumber"]
        print(ksef_number)
        res = cli.wez_fakture(output=output, ksef_number=ksef_number)
        print(res)
        d = self._wez_res(output)
        print(d)
        self.assertTrue(d["OK"])
        # odczytaj invoice
        invoice = d['invoice']
        with open(invoice, mode="r") as f:
            invoice_xml = f.read()
            print(invoice_xml)
            et.fromstring(invoice_xml)
