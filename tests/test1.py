import json

import unittest

import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_tokens import odczytaj_tokny

import helper as T


class TestKSEFCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.C = T.CO()

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
            "xxxxxx", "2023-01-01", "2023-12-31")
        self.assertFalse(res)
        print(msg)
        self.assertIn("Nie można odczytać tokena KSeF dla NIP", msg)

    def test_odczytaj_faktury_zakupowe_bledy_token(self):
        nip = "888888887"
        cli = KSEFCLI(self.C, nip)
        res, msg = cli.czytaj_faktury_zakupowe(
            "xxxxxx", "2023-01-01", "2023-12-31")
        self.assertFalse(res)
        print(msg)

    def test_wyslij_bledna_fakture(self):
        nip = T.NIP
        fa = T.NIEPOPRAWNA_FAKTURA
        invoice_path = T.testdatadir(fa)
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        res = cli.wyslij_fakture_do_ksef(
            res_pathname=output, invoice_path=invoice_path)
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
            res_pathname=output, invoice_path=invoice_path)
        print(res)
        self.assertTrue(res[0])
        with open(output, "r") as f:
            d = json.load(fp=f)
        print(d)
        self.assertTrue(d["OK"])
        f_ksef = d["numer_ksef"]
        print(f_ksef)
        # sprawsz, czy odczytane upo
        upo = self.C.get_invoice_upo(nip, f_ksef)
        with open(upo, "r") as f:
            upo_xml = f.read()
            et.fromstring(upo_xml)
