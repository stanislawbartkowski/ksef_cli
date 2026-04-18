import os
import sys

from ksef_cli import KSEFCLI

WYSLIJ_FAKTURE = "wyslij_fakture"
ODCZYTAJ_UPO = "odczytaj_upo"
POBIERZ_ZAKUPOWE = "pobierz_zakupowe"
ODCZYTAJ_FAKTURE = "odczytaj_fakture"
WYCZYSC_DANE = "wyczysc_dane"
WYSLIJ_WSADOWO = "wyslij_wsadowo"
POBIERZ_SPRZEDAZOWE = "pobierz_sprzedazowe"
POBIERZ_ZBIORCZO = "pobierz_zbiorczo"
DAJ_KONFIGURACJE = "daj_konfiguracje"
DAJ_BUFOR_ZAKUPOWE = "daj_zakupowe_bufor"

HELP = "help"

_actions = {
    WYSLIJ_FAKTURE: (3, KSEFCLI.wyslij_fakture_do_ksef, ('invoice_path',)),
    ODCZYTAJ_UPO: (3, KSEFCLI.wez_upo, ('ksef_number',)),
    POBIERZ_ZAKUPOWE: (4, KSEFCLI.czytaj_faktury_zakupowe, ('data_od', 'data_do')),
    ODCZYTAJ_FAKTURE: (3, KSEFCLI.wez_fakture, ('ksef_number',)),
    WYCZYSC_DANE: (2, KSEFCLI.clean_nip_dir, ()),
    WYSLIJ_WSADOWO: (3, KSEFCLI.wyslij_wsadowo_do_ksef, ('faktury_dir',)),
    POBIERZ_SPRZEDAZOWE: (4, KSEFCLI.czytaj_faktury_sprzedazy, ('data_od', 'data_do')),
    POBIERZ_ZBIORCZO: (5, KSEFCLI.czytaj_faktury_zbiorczo, ('data_od', 'data_do', 'subject')),
    DAJ_KONFIGURACJE: (2, KSEFCLI.daj_konfiguracje, ()),
    DAJ_BUFOR_ZAKUPOWE: (2, KSEFCLI.daj_bufor_zakupowe, ())
}


def printhelp():
    help_file = os.path.join(os.path.dirname(__file__), 'help.txt')
    with open(help_file, "r") as f:
        help_txt = f.read()
        print(help_txt)


def run_main(argv):
    if len(argv) <= 1:
        printhelp()
        return
    action = argv[1]
    action_def = _actions.get(action)
    if action_def is None:
        print(f"Niepoprawna akcja {action} ")
        print()
        printhelp()
        return
    l_pars = action_def[0]
    k_action = action_def[1]
    names = action_def[2]
    if len(argv) - 2 < l_pars:
        print(
            f"Niepoprawna liczba argumentów dla akcji {action}. Powinno być {l_pars}, wprowadzono {len(argv)-2}")
        return
    nip = argv[2]
    output = argv[3]
    K = KSEFCLI.from_os_env(nip)
    kwargs = {n: argv[4+i] for i, n in enumerate(names)}
    k_action(K, output, **kwargs)


def main():
    run_main(argv=sys.argv)
