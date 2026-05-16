import json
import xml.etree.ElementTree as et

from ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import NIP

import helper as T
from ksef_test_base import (
    AbstractTestKSEFCLI,
    TestKsefCli,
    TestWsadowoKsefCli,
    TestWsadowoMainKsefCli,
    _run_main_res,
    _wez_res,
)


class TestKSEFCliCertNIPDIR(AbstractTestKSEFCLI):

    C = T.CO_CERT()
    AT = TestKsefCli()

    def _weryfikuj_konfiguracje(self, nip):
        output = T.temp_ojosn()
        res = self.AT.daj_konfiguracje(C=self.C, output=output, nip=nip)
        print(res)
        assert res[0]
        d = _wez_res(output)
        print(d)
        assert d["OK"]
        files = d["files"]
        assert d["env"] == "test"
        nip_N = NIP(nip)
        assert self.C.ksef_conf_path == files["ksef_conf"]
        assert self.C.work_nip_dir(nip_N) == files["work_dir"]
        assert self.C.get_nip_events_file(nip_N) == files["events_file"]
        assert self.C.get_nip_log_file(nip_N) == files["log_file"]
        assert T.NIP in files["events_file"]
        assert "YYYY" in files["events_file"]
        assert T.NIP in files["log_file"]
        assert "YYYY" in files["log_file"]

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
        self._test_faktury_wyslij_i_czytaj_zbiorczo(self.AT, nip=T.NIP_NABYWCADIR)


def _wyslij_bledna_wsadowo(self, AW):
    invoice_path = T.prepare_invoice(T.FAKTURA_WZORZEC)
    output = T.temp_ojosn()
    ok, _ = AW.wyslij_fakture(C=self.C, output=output, nip=T.NIP, invoice_path=invoice_path)
    assert ok
    ok, errmsg = AW.wyslij_fakture(C=self.C, output=output, nip=T.NIP, invoice_path=invoice_path)
    assert not ok
    assert "Duplikat faktury" in errmsg
    d = _wez_res(output)
    assert not d["OK"]
    assert "Duplikat faktury" in d["errmess"]


class TestKSEFWsadowe(AbstractTestKSEFCLI):

    C = T.CO()
    AW = TestWsadowoKsefCli()

    def test_wyslij_bledna_fakture(self):
        _wyslij_bledna_wsadowo(self, self.AW)

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.AW)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.AW)

    def test_faktura_zakupowa_blad(self):
        self._test_faktura_zakupowa_blad(self.AW)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AW)


class TestKSEFWsadowoMain(AbstractTestKSEFCLI):

    C = T.CO()
    AW = TestWsadowoMainKsefCli()

    def test_wyslij_bledna_fakture(self):
        _wyslij_bledna_wsadowo(self, self.AW)

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.AW)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.AW)

    def test_faktura_zakupowa_blad(self):
        self._test_faktura_zakupowa_blad(self.AW)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.AW)

    def test_wyslij_zduplikowana_fakture(self):
        self._test_wyslij_zduplikowana_fakture(self.AW)


class TestKSEFWsadowoDuzoFaktur:

    C = T.CO()
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
        assert ok
        with open(output, "r") as f:
            d = json.load(fp=f)

        invoices = d.get("invoices", [])
        assert len(invoices) == no
        cli = KSEFCLI(self.C, nip)
        for i in invoices:
            print(i)
            ok = i["ok"]
            invoiceNumber = i["invoiceNumber"]
            assert invoiceNumber in invoices_names
            ksefNumber = i["ksefNumber"]
            output = T.temp_ojosn()
            upo = cli.wez_upo(res_pathname=output, ksef_number=ksefNumber)
            d = _wez_res(output)
            upo = d["upo"]
            with open(upo, "r") as f:
                upo_xml = f.read()
                et.fromstring(upo_xml)
        return invoices_names

    def test_wysyla_wiele_zduplikowane(self):
        self.test_wysylka_wiele_faktur(no=1)
        nip = T.NIP
        tmp_dir = T.temp_dir()
        output = T.temp_ojosn()
        argv = ["", "wyslij_wsadowo", nip, output, tmp_dir]
        ok, errmsg = _run_main_res(argv, output)
        assert ok
        with open(output, "r") as f:
            d = json.load(fp=f)

        invoices = d.get("invoices", [])
        print(invoices)
        i = invoices[0]
        assert not i["ok"]
        assert "Duplikat faktury" in i["msg"]
