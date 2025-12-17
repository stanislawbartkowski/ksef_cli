## Opis

Jest to "command line" rozszerzenie rozwiązania: https://github.com/stanislawbartkowski/ksef_pyth. Umożliwia komunikację z systemem KSeF z poziomu poleceń systemu Linux oraz integrację z innymi systemami.

Dodatkowe cechy rozwiązania:

* Konfiguracja tokena (tokenów) z pliku tekstowego.
* Tworzenie dziennika i logów, historii wykonywanych operacji.
* Możliwość wywołania funkcjonalności z poziomu bash lub bezpośrednio jako komenda Python3

## Konfiguracja

Zmienne środowiskowe

* KSEFCONF - plik zawierający listę dopuszczalnych NIPów oraz tokenów związanych z NIPami. Zawiera także definicje obsługiwanego środowiska KSeF 2.0 - deweloperskie/testowe, przedprodukcyjne/demo oraz produkcyjne.
* KSEFDIR - katalog na logi operacji

## Konfiguracja NIP i token

Plik jest wskazywany przez zmienną środowiskową *KSEFCONF*. Jest to plik w formacie YAML.

```
tokens:
  NIP{nip}:
    token: {token dla NIP}
    env: prod|demo|test  (produkcyjne, demo, testowe)
```

Przykład: <br>
NIP - 7497725064 <br>
Wartość tokena dostępowego dla NIP <br>
Środowisko testowe <br>

```YAML
  NIP7497725064:
    token: 20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370
    env: test
```

## Struktura kodu w Python

* ksef_cli
  * ksef_cli.py Dostępna funkcjonalność
  * ksef_conf.py Wykorzystywany wewnętrznie, konfiguracja
  * ksef_log.py Wykorzystywany wewnętrznie, tworzenie dziennika
  * ksef_tokens.py Wykorzystywany wewnętrznie, tokeny i środowiska
* tests  Unit test suite

## Struktura katalogu z logami i dziennikiem

Katalog jest wskazywany przez zmienną środowiskową *KSEFDIR*. Dane są logowane na poziomie wspólnym i na poziomie NIP. Dodatkowo każda wysłana faktura tworzy podakatalog z numerem KSeF nadanym po wysłaniu, gdzie zawarty jest odczytany plikm UPO oraz wysłana faktura.

* KSEFDIR
  * events.csv Plik z formacie tekstowym CSV z historią operacji. Pamiętane są operacje zakończone sukcesem oraz operacje które nie zostały wykonany z opisem błędu.
  * ksef.log Zawiera dane logging z wykonywania
  * {nip}
    * events.csv Plik w formacie tekstowym CSV z historią operacji. Zawiera te same dane co plik event.csv w katalogu KSEFDIR, ale tylko dla danego NIP
    * ksef.log Zawiera dane logging z wykonywania, Zawiera te same dane co plik ksef.log w katalog KSEFDIR, ale tylko dla operacji związanych z danym NIP
    * {ksef_number} Dla każdej wysłanej faktury z danego NIP
      * upo.xml Plik UPO
      * faktura.xml Wysłana faktura

Przykładowy fragment pliku events.csv
```csv
2025-12-16T20:49:42.166316,2025-12-16T20:49:42.917164,0.75,1,Czytanie faktur zakupowych,FAIL,KSEFCLI._czytaj_faktury_zakupe_action() got an unexpected keyword argument 'run_func',7497725064,
2025-12-16T20:50:30.552768,2025-12-16T20:50:31.310412,0.76,1,Czytanie faktur zakupowych,FAIL,KSEFCLI._czytaj_faktury_zakupe_action() got an unexpected keyword argument 'run_func',7497725064,
2025-12-16T20:53:06.316936,2025-12-16T20:53:07.139957,0.82,1,Czytanie faktur zakupowych,FAIL,KSEFCLI._czytaj_faktury_zakupe_action() missing 1 required positional argument: 'K',7497725064,
2025-12-16T20:54:07.355882,2025-12-16T20:54:08.150260,0.79,1,Czytanie faktur zakupowych,FAIL,KSEFCLI._czytaj_faktury_zakupe_action() missing 1 required positional argument: 'K',7497725064,
2025-12-16T20:54:08.754346,2025-12-16T20:54:09.493529,0.74,1,Czytanie faktur zakupowych,FAIL,KSEFCLI._czytaj_faktury_zakupe_action() missing 1 required positional argument: 'K',7497725064,
2025-12-16T20:54:54.710717,2025-12-16T20:54:55.807550,1.10,1,Czytanie faktur zakupowych,OK,,7497725064,2025-12-11 - 2025-12-18
2025-12-16T20:54:55.809410,2025-12-16T20:54:56.915264,1.11,4,Weź fakturę z KSeF,OK,,7497725064,
2025-12-16T20:58:32.052180,2025-12-16T20:58:35.711541,3.66,2,Wyślij fakture do KSeF,FAIL,Nieprawidłowy zakres uprawnień Kontekst 7497725064 nie jest uprawniony do wystawienia faktury w imieniu sprzedawcy (NIP: 7952809480),7497725064,
2025-12-16T20:58:36.123971,2025-12-16T20:58:38.096498,1.97,1,Czytanie faktur zakupowych,OK,,7497725064,2025-12-11 - 2025-12-18
```
## Operacje

Wywołanie:

> python -m ksef_cli <akcja> <nip> <plik_na_wynik> <dodatkowe_parametry>

akcja:
* wyslij_fakture Wysłanie faktury do system KSeF 2.0
* odczytaj_upo Odczytaj plik UPO do wysłanej i zaakceptowanej faktury
* pobierz_zakupowe Odczytaj nagłówki (metadata) faktur zakupowych
* odczytaj_fakture Odczytaj fakturę na podstawie nadanego numeru KSeF

nip:
* Numer NIP użytkownika KSeF 2.0. Numer NIP musi być zawarty w plik *KSEFCONF*

plik_na_wynik:
* Nazwa pliku gdzie będzie zapisany wynik akcji. Wynik jest zapisany w formacie JSON.

Plik zawiera zawsze dwa pola oraz dodatkowe pola zależne od akcji
* OK: true/false Akcja zakońćzona sukcesem lub niepowodzeniem
* errmess: Jeśli akcja zakończona niepowodzeniem, to informacja o błędzie

Działanie:
* Odczytuje NIP oraz wyszukuje NIP w pliku *KSEFCONF*
* Wykonuje akcję na podstawie podanych patametrów
* Uzupełnia dziennik oraz logging w katalogu *KSEFDIR*
* Zapisuje plik *plik_na_wynik* w formacie JSON z wynikiem akcji

Dodatkowa uwaga:
Wywołanie nie zwraca znaczącego *exit code*. Wynik akcji, także niepowodzenie, trzeba odczytać z pliku *plik_na_wynik*

## wyslij_faktura

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#wys%C5%82anie-faktury)

> python -m ksef_cli wyslij_fakture <nip> <plik_na_wynik> <plik XML z fakturą do wysłania>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* numer_ksef Jeśli faktura jest zaakceptowana w systemie KSeF 2.0, to nadany przez KSeF numer

## odczytaj_upo

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-upo)

> python -m ksef_cli odczytaj_upo  <nip> <plik_na_wynik> <numer_ksef>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* upo Nazwa pliku zawierającego UPO w formacie XML

UWAGA: UPO jest odczytywane bezpośrednio po wysłaniu faktury *wyslij_fakture* i zapamiętane w katalogu *KSEFDIR*/nip/numer_ksef. Wywołanie *odczytaj_upo* zwraca link do tego pliku, nie jest uruchamiana komunikacja z KSeF.

## odczytaj_fakture

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-faktury-wed%C5%82ug-numeru-ksef)

> python -m ksef_cli odczytaj_fakture  <nip> <plik_na_wynik> <numer_ksef>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* invoice Nazwa plik z odczytaną fakturą w formacie XML

## pobierz_zakupowe

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-nag%C5%82%C3%B3wk%C3%B3w-faktur-zakupowych-na-podstawie-dat)

> python -m ksef_cli pobierz_zakupoe  <nip> <plik_na_wynik> <data_od> <data_do>

Odczytuje faktury zakupowe w przedziale dat. Daty muszą być w formacie YYYY-MM-DD

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* faktury Lista zawierająca odczytane nagłówki faktur zakupowych z podanego zakresu dat.

## Dev environment, happy coding
> source .venv/bin/activate
> git clone https://github.com/stanislawbartkowski/ksef_cli.git
> pip install -r requirements.txt
> code .
