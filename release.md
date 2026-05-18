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
