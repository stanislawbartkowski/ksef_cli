import unittest

from ksef_cli.ksef_conf import CONF
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
        # Test with a non existing NIP number
        self.assertRaises(
            ValueError, lambda: odczytaj_tokny(self.C, "9999999997"))
