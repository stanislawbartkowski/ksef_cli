import unittest
from ksef_cli.ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import CONF
import helper as T
from ksef_cli.ksef_tokens import odczytaj_tokny


class TestKSEFCLI_ERROR(unittest.TestCase):

    def test_initialization_error(self):

        # Variable KSEFCONF is not set, should raise ValueError
        self.assertRaises(ValueError, lambda: CONF.from_os_env())

    def test_nip_no_cert(self):
        C = T.CO_CERT()
        self.assertRaises(
            ValueError, lambda: odczytaj_tokny(C, "1234567"))

    def test_autentykacja_cert(self):
        C = T.CO_CERT()
        cli = KSEFCLI(C, T.NIP)
        d_from, d_to = T.daj_przedzial()
        output = T.temp_ojosn()
        res = cli.czytaj_faktury_zakupowe(output=output, data_od=d_from, data_do=d_to)
        print(res)
        self.assertTrue(res[0])  # Expecting success
        
