from dataclasses import dataclass
import pytest

from ksef_cli import KSEFCLI
from ksef_cli.ksef_conf import CONF
from ksef_cli.ksef_tokens import odczytaj_tokny

import helper as T
from ksef_test_base import (
    AbstractTestKSEFCLI,
    AKsefCli,
    TestKsefCli,
    TestKsefCliMain,
)


@dataclass
class _KSEFConf:
    C: CONF
    A: AKsefCli
    errmess_bledna: str
    is_token: bool = False
    is_main: bool = False
    has_zbiorowy: bool = False


_ADAPTERS = [
    pytest.param(
        _KSEFConf(
            C=T.CO(),
            A=TestKsefCli(),
            errmess_bledna="nie jest uprawniony do wystawienia faktury w imieniu",
            is_token=True,
            has_zbiorowy=True,
        ),
        id="token",
    ),
    pytest.param(
        _KSEFConf(
            C=T.CO_CERT(),
            A=TestKsefCli(),
            errmess_bledna="Nieprawidłowy zakres uprawnień Kontekst",
        ),
        id="cert",
    ),
    pytest.param(
        _KSEFConf(
            C=T.CO(),
            A=TestKsefCliMain(),
            errmess_bledna="nie jest uprawniony do wystawienia faktury w imieniu",
            is_main=True,
            has_zbiorowy=True,
        ),
        id="main",
    ),
]


@pytest.mark.parametrize("cfg", _ADAPTERS)
class TestKSEFCombined(AbstractTestKSEFCLI):
    @pytest.fixture(autouse=True)
    def _setup(self, cfg):
        self.C = cfg.C
        self.A = cfg.A

    def test_token_nip_no(self, cfg):
        if not cfg.is_token:
            pytest.skip("token-only")
        with pytest.raises(KeyError):
            odczytaj_tokny(self.C, "1234567890")

    def test_token_nip_wrong_env(self, cfg):
        if not cfg.is_token:
            pytest.skip("token-only")
        with pytest.raises(ValueError):
            odczytaj_tokny(self.C, "9999999997")

    def test_token_nip_end_env(self, cfg):
        if not cfg.is_token:
            pytest.skip("token-only")
        token = odczytaj_tokny(self.C, "888888887")
        print(token)
        assert token.env == 0
        assert token.token == "xxxxxxxxxxxx"

    def test_usun_katalog_roboczy(self, cfg):
        if not cfg.is_token:
            pytest.skip("token-only")
        nip = "777777776"
        cli = KSEFCLI(self.C, nip)
        output = T.temp_ojosn()
        cli.clean_nip_dir(res_pathname=output)

    def test_odczytaj_faktury_zakupowe_brak_nip(self):
        self._test_odczytaj_faktury_zakupowe_brak_nip(self.A)

    def test_odczytaj_faktury_zakupowe_bledy_token(self):
        self._test_odczytaj_faktury_zakupowe_bledy_token(self.A)

    def test_wyslij_bledna_fakture(self, cfg):
        self._test_wyslij_bledna_fakture(self.A, errmess_contains=cfg.errmess_bledna)

    def test_wyslij_fakture_sprzedazy(self):
        self._test_wyslij_fakture_sprzedazy(self.A)

    def test_wez_upo_nie_istnieje(self):
        self._test_wez_upo_nie_istnieje(self.A)

    def test_wez_upo_dla_faktury(self):
        self._test_wez_upo_dla_faktury(self.A)

    def test_faktura_zakupowa_blad(self):
        self._test_faktura_zakupowa_blad(self.A)

    def test_faktura_zakupowa(self):
        self._test_faktura_zakupowa(self.A)

    def test_pobierz_faktury_zakupowe(self):
        self._test_pobierz_faktury_zakupowe(self.A)

    def test_pobierz_faktury_sprzedazy(self):
        self._test_pobierz_faktury_sprzedazy(self.A)

    def test_faktury_czytaj_zbiorcz_za_duzy_zakres(self, cfg):
        if not cfg.has_zbiorowy:
            pytest.skip("not applicable for cert auth")
        self._test_faktury_czytaj_zbiorcz_za_duzy_zakres(self.A)

    def test_faktury_czytaj_zbiorczo_brak_faktur(self, cfg):
        if not cfg.has_zbiorowy:
            pytest.skip("not applicable for cert auth")
        self._test_faktury_czytaj_zbiorczo_brak_faktur(self.A)

    def test_faktury_czytaj_zbiorczo_duzo_faktur(self, cfg):
        if not cfg.has_zbiorowy:
            pytest.skip("not applicable for cert auth")
        self._test_faktury_czytaj_zbiorczo_duzo_faktur(self.A)

    def test_faktury_wyslij_i_czytaj_zbiorczo(self, cfg):
        if not cfg.has_zbiorowy:
            pytest.skip("not applicable for cert auth")
        self._test_faktury_wyslij_i_czytaj_zbiorczo(self.A)

    def test_sprawdz_konfiguracje(self, cfg):
        if not cfg.has_zbiorowy:
            pytest.skip("not applicable for cert auth")
        self._test_sprawdz_konfiguracje(self.A)

    def test_wez_bufor_zakupowe(self, cfg):
        if not cfg.is_main:
            pytest.skip("main adapter only")
        self._test_wez_bufor_zakupowe(self.A)

    def test_uaktualnij_bufor_zakupowe_zero(self, cfg):
        if not cfg.is_main:
            pytest.skip("main adapter only")
        self._test_uaktualnij_bufor_zakupowe_zero(self.A)

    def test_uaktualnij_bufor_zakupowe(self, cfg):
        if not cfg.is_main:
            pytest.skip("main adapter only")
        self._test_uaktualnij_bufor_zakupowe(self.A)

    def test_bufor_zakupowe_wez_jeden(self, cfg):
        if not cfg.is_main:
            pytest.skip("main adapter only")
        self._test_bufor_zakupowe_wez_jeden(self.A)

    def test_wyslij_zduplikowana_fakture(self, cfg):
        if not cfg.is_main:
            pytest.skip("main adapter only")
        self._test_wyslij_zduplikowana_fakture(self.A)

    def test_wyslij_z_wierszami(self, cfg):
        self._test_wyslij_z_wierszami(self.A)
