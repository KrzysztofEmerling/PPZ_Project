# Sudoku-sweeper
Aplikacja webowa do gry w Sudoku, zbudowana w technologii Flask i SQLAlchemy.

## Instalacja
Sklonowanie repozytorium:
~~~
git clone https://github.com/KrzysztofEmerling/PPZ_Project.git
~~~

utworzenie flaskEnv z pliku requirements.txt:
~~~
python3 -m venv flaskEnv
./flaskEnv/bin/activate           (Unix)
/flaskEnv/Scripts/activate        (Windows)
source /flaskEnv/bin/activate     (MacOS)
pip install -r requirements.txt
~~~

Pobranie bazy zagadek sudoku do folderu vendor:
~~~
git clone https://github.com/grantm/sudoku-exchange-puzzle-bank.git
~~~

Uruchomienie aplikacji:
~~~
python3 ./app/app.py
~~~

## Opis Projektu
Projekt Sudoku-sweeper umożliwia użytkownikom grę w Sudoku jako gość lub po zalogowaniu się. Zalogowani użytkownicy mogą śledzić swoje wyniki i historię gier. Aplikacja oferuje różne poziomy trudności, funkcje cofania i resetowania planszy oraz pomiar czasu gry.

### Funkcjonalności
#### Gra w Sudoku:
Wczytywanie planszy z różnymi poziomami trudności, wpisywanie liczb, opcjonalna nawigacja klawiaturą, sprawdzanie poprawności rozwiązania, funkcje cofania i resetowania, pomiar czasu gry.

#### Rejestracja i Logowanie:
Formularz rejestracyjny z walidacją, logowanie z hashowaniem i soleniem haseł, logowanie administratora, możliwość wylogowania.
#### Baza Danych:
Przechowywanie kont użytkowników, zapisywanie wyników gier, wyświetlanie historii gier i bazy użytkowników dla administratora.
#### Panel Admina:
Lista użytkowników, możliwość usuwania kont.

### Wymagania Niefunkcjonalne
Interfejs Użytkownika: Intuicyjny i responsywny.
Wydajność: Szybkie ładowanie strony (< 1.5 sekundy).

### Wymagania Bezpieczeństwa
Ochrona przed SQL Injection
Hasła: Solone hasła przechowywane jako hashe, wymóg silnych haseł, walidacja formularzy wejściowych.

### Technologie
Backend: Python, Flask
Frontend: HTML, CSS, JavaScript, Bootstrap
Baza Danych: SQLAlchemy

### Struktura Aplikacji
~~~
/project 
├── /app
│   ├── /static
│   │   ├── style.css
│   │   └── script.js
│   ├── /templates
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── game.html
│   │   ├── history.html
│   │   └── admin.html
│   ├── /vendor
│   │   └── /sudoku-exchange-puzzle-bank
│   ├── models.py
│   ├── routes.py
│   ├── app.py
│   └── database.db
└── requirements.txt
~~~

### Harmonogram
Dostępny na stronie: https://github.com/users/KrzysztofEmerling/projects/2

### Zespół Projektowy:
Agnieszka Głowacka
Martyna Trębacz
Oliwia Skucha
Jakub Rogoża
Krzysztof Emerling
Szymon Duda
