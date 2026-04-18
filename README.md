## Opis

Jest to "command line" rozszerzenie rozwiązania: https://github.com/stanislawbartkowski/ksef_pyth. Umożliwia komunikację z systemem KSeF z poprzez wywołanie python3. Daje to możliwość integracji z systemami, które nie są oparte w Python.

Dodatkowe cechy rozwiązania:

* Konfiguracje metody autentykacji: token lub certyfikat na podstawie pliku konfiguracyjnego
* Tworzenie dziennika i logów, historii wykonywanych operacji.
* Możliwość wywołania funkcjonalności z poziomu bash lub bezpośrednio jako komenda python3

## Python

Testowane dla wersji: 3.10, 3.11 i 3.12

Testowane w testowym środowisku KSeF 2.0. Jest także wykorzystywane w produkcyjnym środowisku.

## Konfiguracja

Zmienne środowiskowe

* KSEFCONF - plik zawierający listę dopuszczalnych NIPów oraz tokenów związanych z NIPami. Zawiera także definicje obsługiwanego środowiska KSeF 2.0 - deweloperskie/testowe, przedprodukcyjne oraz produkcyjne.
* KSEFDIR - katalog na logi operacji

## Instalacja
> pip install git+https://github.com/stanislawbartkowski/ksef_cli.git<br>

lub

> pip install ksef2.0-cli


> python<br>
> import ksef_cli<br>

## Konfiguracja NIP oraz metody autentykacji

Plik jest wskazywany przez zmienną środowiskową *KSEFCONF*. Jest to plik w formacie YAML.

```
tokens:
  NIP{nip}:
    token: {token dla NIP}
    env: prod|demo|test  (produkcyjne, demo, testowe)
```

### Token

Przykład: <br>
NIP - 7497725064 <br>
Wartość tokena dostępowego dla NIP <br>
Środowisko testowe <br>

```YAML
  NIP7497725064:
    token: 20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370
    env: test
```

### Certyfikat

Przykład: <br>
NIP - 7497725064 <br>
Środowisko testowe <br>
Plik p12 z certyfikatami: keyStore.p12<br>
Hasło odczytu: 1234

```YAML
  NIP7497725064:
    env: test
    password: "1234"
    p12: keyStore.p12
```

Dodatkowa informacja dotycząca certyfikatów.

Testy były przeprowadzane tylko dla tylko dla testowych certyfikatów generowanych poprzez testowe środowisko KSeF 2.0

Parametr p12 wskazuje na plik w formacie P12 zawierający wygenerowany klucz i certyfikat.

Przykładowa komenda tworząca plik P12. Pliki CertyfikatKSEF zawierają pliki utworzone przez KSeF 2.0

> openssl pkcs12 -export -out keyStore.p12 -inkey CertyfikatKSEF.key  -in CertyfikatKSEF.crt

## NIP
NIP przekazywany jako parametr do wszystkich wywołań może przybierać dwie postacie:

* NIP
* NIP$podkatalog

W drugim przypadku po symbolu NIP są dodane separator $ oraz nazwa podkatalogu. Podkatalog ma znaczenie dla tworzenia struktury logów oraz miejsca składowania faktur/UPO. Bez podkatalogu miejscem jest zawsze symbol NIP. Z podkatalogiem do NIP jest dodawany podkatalog. 
Ten sam symbol NIP może być wywoływany z różnymi podkatalogami. Przykład:
* 7497725064, miejscem składowania jest NIP 7497725064
* 7497725064$ROK2025, miejscem składowania jest 7497725064/ROK2025  

## Struktura kodu w Python

* ksef_cli
  * ksef_cli.py Dostępna funkcjonalność
  * ksef_conf.py Wykorzystywany wewnętrznie, konfiguracja
  * ksef_log.py Wykorzystywany wewnętrznie, tworzenie dziennika
  * ksef_tokens.py Wykorzystywany wewnętrznie, tokeny i środowiska
* tests  Unit test suite

## Struktura katalogu z logami i dziennikiem

Katalog jest wskazywany przez zmienną środowiskową *KSEFDIR*. Dane są logowane na poziomie wspólnym i na poziomie NIP. Dodatkowo każda wysłana faktura tworzy podkatalog z numerem KSeF nadanym po wysłaniu, gdzie zawarty jest odczytany plik UPO oraz wysłana faktura. Zapamietywane są tylko faktury zaakceptowane w KSeF 2.0 i mające nadany numer KSeF.

* KSEFDIR
  * events.csv Plik w formacie tekstowym CSV z historią operacji. Pamiętane są operacje zakończone sukcesem oraz operacje, które nie zostały wykonane z opisem błędu.
  * ksef.log Zawiera dane logging z wykonywania
  * {nip}
    * events.csv Plik w formacie tekstowym CSV z historią operacji. Zawiera te same dane co plik event.csv w katalogu KSEFDIR, ale tylko dla danego NIP
    * ksef.log Zawiera dane logging z wykonywania, Zawiera te same dane co plik ksef.log w katalog KSEFDIR, ale tylko dla operacji związanych z danym NIP
    * {ksef_number} Dla każdej wysłanej i zaakceptowanej faktury z danego NIP
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

> python -m ksef_cli <akcja> \<nip\> <plik_na_wynik> <dodatkowe_parametry>

akcja, dopuszczalne wartości:
* wyslij_fakture Wysłanie faktury do system KSeF 2.0
* odczytaj_upo Odczytaj plik UPO do wysłanej i zaakceptowanej faktury
* pobierz_zakupowe Odczytaj nagłówki (metadata) faktur zakupowych
* odczytaj_fakture Odczytaj fakturę na podstawie nadanego numeru KSeF
* wyslij_wsadowo Wysyła paczkę faktur w sesji wsadowej

nip:
* Numer NIP użytkownika KSeF 2.0. Numer NIP musi być zawarty w pliku *KSEFCONF*. Z pliku konfiguracyjnego jest odczytywany odpowiedni token służący do autentykacji.

plik_na_wynik:
* Nazwa pliku, gdzie będzie zapisany wynik akcji. Wynik jest zapisany w formacie JSON.

Plik zawiera zawsze dwa pola oraz dodatkowe pola zależne od akcji
* OK: true/false Akcja zakończona sukcesem lub niepowodzeniem
* errmess: Jeśli akcja zakończona niepowodzeniem, to informacja o błędzie

Działanie:
* Odczytuje NIP oraz wyszukuje metodę autentykacji (token lub certyfikat) w pliku *KSEFCONF*
* Autentykacja z użyciem NIP oraz poprzez token lub certyfikat
* Wykonuje akcję na podstawie podanych paeametrów
* Uzupełnia dziennik oraz logging w katalogu *KSEFDIR*
* Zapisuje plik *plik_na_wynik* w formacie JSON z wynikiem akcji

Dodatkowa uwaga:

Wywołanie nie zwraca znaczącego *exit code*. Wynik akcji, także niepowodzenie, trzeba odczytać z pliku *plik_na_wynik*

## wyslij_fakture

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#wys%C5%82anie-faktury)

> python -m ksef_cli wyslij_fakture \<nip\> <plik_na_wynik> <plik XML z fakturą do wysłania>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* numer_ksef Jeśli faktura jest zaakceptowana w systemie KSeF 2.0, to nadany przez KSeF 2.0 numer

## wyslij_wsadowo
[link](https://github.com/stanislawbartkowski/ksef_pyth/tree/main?tab=readme-ov-file#wys%C5%82anie-paczki-faktur-w-trybie-wsadowym)

> python -m ksef_cli wyslij_wsadowo \<nip\> <plik_na_wynik> <katalog z paczką faktur>

* \<katalog z paczką faktur\>. Katalog w którym znajdują się faktury XML gotowe do wysłania do systemu KSeF. Wysyłane są tylko pliki z rozszerzeniem \.xml, inne pliki są ignorowane. UWAGA: w środowisku testowym akceptowanych jest tylko pierwsze 10 faktur, pozostałe są ignorowane bez sygnalizowania żadnego błędu.

Działanie:
* Faktury z katalogu są pakowane w formacie ZIP i wysyłane do systemu KSeF zgodnie ze specyfikacją API. Jeśli rozmiar po spakowaniu przekracza 100MB, to dane są odpowiednio dzielone na poszczególne paczki.

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* invoices Lista wysłanych faktur z nadanym numerem KSeF. Jeden element listy zawiera następujące informacje:
  * ok True/False True jeśli faktura została zaakceptowana w KSeF 2.0 i ma nadany numer KSeF
  * msg Jeśli ok=False, to komunikat o błędzie
  * ordinalNumber Numer kolejny faktury w paczce faktur (od 1)
  * invoiceNumber Numer faktury pobrany ze źródłowego pliku XML
  * ksefNumber Jeśli faktura jest zaakceptowana, to nadany numer KSeF
  

## odczytaj_upo

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-upo)

> python -m ksef_cli odczytaj_upo  \<nip\> <plik_na_wynik> <numer_ksef>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* upo Nazwa pliku zawierającego UPO w formacie XML

UWAGA: UPO jest odczytywane bezpośrednio po wysłaniu faktury *wyslij_fakture* i zapamiętane w katalogu *KSEFDIR*/nip/numer_ksef. Wywołanie *odczytaj_upo* zwraca link do tego pliku, nie jest uruchamiana komunikacja z KSeF.

## odczytaj_fakture

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-faktury-wed%C5%82ug-numeru-ksef)

> python -m ksef_cli odczytaj_fakture  \<nip\> <plik_na_wynik> <numer_ksef>

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* invoice Nazwa plik z odczytaną fakturą w formacie XML

## pobierz_zakupowe

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-nag%C5%82%C3%B3wk%C3%B3w-faktur-zakupowych-na-podstawie-dat)

> python -m ksef_cli pobierz_zakupowe  \<nip\> <plik_na_wynik> <data_od> <data_do>

Odczytuje faktury zakupowe w przedziale dat. Daty muszą być w formacie YYYY-MM-DD

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* faktury Lista zawierająca odczytane nagłówki faktur zakupowych z podanego zakresu dat.

## pobierz_sprzedazowe

[link](https://github.com/stanislawbartkowski/ksef_pyth/tree/main?tab=readme-ov-file#odczytanie-nag%C5%82%C3%B3wk%C3%B3w-faktur-na-podstawie-dat)

> python -m ksef_cli pobierz_sprzedazowe  \<nip\> <plik_na_wynik> <data_od> <data_do>

Odczytuje faktury sprzedażowe w przedziale dat. Daty muszą być w formacie YYYY-MM-DD

Zwracana wartość w pliku *plik_na_wynik*
* OK
* errmess
* faktury Lista zawierająca odczytane nagłówki faktur sprzedażowych z podanego zakresu dat.

## pobierz_zbiorczo

[link](https://github.com/stanislawbartkowski/ksef_pyth?tab=readme-ov-file#odczytanie-paczki-faktur)

> python -m ksef_cli pobierz_zbiorczo  \<nip\> <plik_na_wynik> <data_od> <data_do> \<subject\>


Zwraca w plik_na_wynik
  * OK: true/false
  * errmess
  * katalog: Katalog tymczasowy, gdzie znajdują się odczytane faktury lub None, jeśli nic nie odczytano. Jeśli odczytano faktury, to w katalogu pojawi się także plik _metadata.json zawierający zbiorczą informację o odczytanych fakturach.
  * liczba_faktur: Liczba odczytanych faktur. Liczba może być 0, wówczas katalog jest None
  * subject:
    * Subject1	Podmiot 1 - sprzedawca
    * Subject2	Podmiot 2 - nabywca
    * Subject3	Podmiot 3
    * SubjectAuthorized	Podmiot upoważniony

## daj_konfiguracje

Pozwala sprawdzić, czy NIP jest skonfigurowany do komunikacji z systemem KSeF 2.0

> python -m ksef_cli daj_konfiguracje  \<nip\> <plik_na_wynik>

Zwraca w plik_na_wynik
  * OK: true/false
  * errmess
  * mess, Dodatkowy komunikat
  * auth, Dwa wartości, token lub certyfikat
  * env, Środowisko: prod, demo lub test. Wartość z pliku kseftoken
  * files:
    * ksef_conf, wartość zmiennej konfiguracyjnej KSEFCONF
    * work_dir, ścieżka katalogu z danymi dla NIP. Jest to podkatalog WORKDIR dla danego NIP
    * log_file, ścieżka do pliku z logami tworzonymi w trakcie wykonywania operacji
    * events_file, ścieżka do pliku z dziennikiem operacji dla danego NIP


## Przykładowe wywołanie
> export KSEFCONF=/ścieżka/ <br>
> export KSEFDIR=/ścieżka/ <br>
> python -m ksef_cli /parametry/ <br>

## Dev environment, happy coding
> source .venv/bin/activate<br>
> git clone https://github.com/stanislawbartkowski/ksef_cli.git<br>
> pip install -r requirements.txt<br>
> code .<br>
