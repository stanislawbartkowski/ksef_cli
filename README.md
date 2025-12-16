## Opis

Jest to "command line" rozszerzenie rozwiązania: https://github.com/stanislawbartkowski/ksef_pyth. Umożliwia komunikację z systemem KSeF z poziomu poleceń systemu Linux oraz integrację z innymi systemami.

Dodatkowe cechy rozwiązania:

* Konfiguracja tokena (tokenów) z pliku tekstowego.
* Tworzenie logów, historii wykonywanych operacji.
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
 * dssdf 
