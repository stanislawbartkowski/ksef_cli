import unittest
from ksef_cli.ksef_conf import CONF


class TestKSEFCLI_ERROR(unittest.TestCase):

    def test_initialization_error(self):

        # Variable KSEFCONF is not set, should raise ValueError
        self.assertRaises(ValueError, CONF.get_ksef_conf_path)
