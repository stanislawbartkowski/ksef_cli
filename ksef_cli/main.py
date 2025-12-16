import os

WYSLIJ_FAKTURE = "wyslij_fakture"
ODCZYTAJ_UPO = "odczytaj_upo"
POBIERZ_ZAKUPOWE = "pobierz_zakupowe"
ODCZYTAJ_FAKTURE = "odczytaj_fakture"

HELP = "help"


def printhelp():
    help_file = os.path.join(os.path.dirname(__file__), 'help.txt')
    with open(help_file, "r") as f:
        help_txt = f.read()
        print(help_txt)


def main():
    printhelp()
