import unittest

from ksef_cli import KSEFCLI
from ksef_cli.ksef_tokens import odczytaj_tokny

from helper import CO


class TestKSEFCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.C = CO()

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
