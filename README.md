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


