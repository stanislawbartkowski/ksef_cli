## Wersja 1.2.0 Data: 2026/05/25
* Refactoring autentykacji: zastąpienie ksef_tokens.py pluggable systemem CredentialsProvider (credentials.py + credentials_yaml.py)
* Dodanie akcji dodaj_token oraz dodaj_certyfikat — rejestracja nowego NIP w pliku konfiguracyjnym z linii poleceń
* Cicha nadpisywanie istniejących wpisów, walidacja środowiska przed zapisem
* Dodanie akcji pobierz_tokeny — pobranie listy tokenów zarejestrowanych w KSeF dla danego NIP (wrapper na KSEFSDK.get_list_of_tokens)
* Dodanie akcji sprawdz_token — walidacja tokena bez zapisu do konfiguracji (próba autoryzacji w KSeF z parametrów wywołania)
* Dodanie akcji sprawdz_certyfikat — walidacja certyfikatu bez zapisu do konfiguracji (próba autoryzacji w KSeF z parametrów wywołania)
* Dodanie modułu testowego tests/test3.py pokrywającego nowe API offline (12 testów, bez wymogu połączenia z KSeF)
* Rozszerzenie tests/test1.py o testy dla nowych akcji w trzech wariantach adapterów (token, cert, main)

## Wersja 1.1.6r1 Data: 2026/05/18
* Dodanie testu z zamianą linii dla KSeF

## Wersja 1.1.6 Data: 2026/05/17
* Refactoring: zastąpienie flake8 ruff
* Zamiana unittest na pytest

## Wersja 1.1.5r4 Data: 2026/05/01
* Small refactoring after Claude review

## Wersja 1.1.5r2 Data: 2026/04/27
* Python 3.10 - zastąpienie datetime.fromisoformat(s) przez parse(s) to zachować kompatybilność z Python 3.10

## Wersja 1.1.5r1 Data: 2026/04/22
* Tomorrow - jest tworzone przez dodanie 2 dni, może być problem z różnymi strefami czasowymi

## Wersja 1.1.5 Data: 2026/04/21
* Dodanie przyrostowego odczytywania faktur zakupowych

## Wersja 1.1.4 Data: 2026/04/04
* Dodanie środowiska do daj_konfiguracje

## Wersja 1.1.3 Data: 2026/04/02
* Poprawienie ścieżki do logowania zdarzeń dla nip kwalifikowanego podkatalogiem
* Więcej informacje zwracanych w wez_konfiguracje

## Wersja 1.1.2 Data: 2026/04/01
* Poprawienie drobnego błędu dotyczącego logowania zdarzeń
  
## Wersja 1.1.1 Data: 2026/03/21
* Możliwość kwalifikacji symbolu NIP podkatalogiem
* wez_konfiguracje, sprawdzenie, czy NIP jest skonfigurowany do komunikacji z systemem KSeF 2.0

## Wersja 1.1.0  Data: 2026/03/13
* Dodanie exportu paczki faktury /invoices/exports, pobierz_zbiorczo
