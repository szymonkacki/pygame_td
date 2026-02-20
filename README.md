# 🏰 Pygame Tower Defense Game

*[Read this in English](README-en.md)*

W pełni funkcjonalna gra typu Tower Defense stworzona w języku Python z wykorzystaniem biblioteki Pygame. Celem gry jest obrona przed nadciągającymi falami przeciwników poprzez strategiczne rozmieszczanie i ulepszanie wież obronnych.

## Główne funkcje gry

* **System wież i ewolucji:** * Budowa podstawowych wież łuczniczych.
  * Ulepszanie wież (poziomy 1-3) zwiększające obrażenia i zasięg.
  * **Ewolucja** na maksymalnym 4. poziomie. Do wyboru:
    * 🔥 **FireTower** – obrażenia obszarowe.
    * ❄️ **IceTower** – spowalnianie trafionych celów.
    * ⚡ **SpeedyTower** – drastycznie zwiększona szybkostrzelność.
* **Różnorodni przeciwnicy:** Trzy klasy wrogów wymagające innej strategii (Zwykli, Szybcy, Wytrzymałe Tanki).
* **Zarządzanie ekonomią:** Otrzymujesz złoto za pokonywanie przeciwników. Pieniądze możesz inwestować w nowe budowle, ulepszenia lub odzyskać część kosztów sprzedając istniejące wieże.
* **Fale o rosnącym poziomie trudności:** Z każdą falą rośnie liczba przeciwników oraz szansa na pojawienie się silniejszych jednostek.
* **Pełny interfejs (UI):** Menu główne, wybór poziomu trudności (Normal/Hard), interaktywne menu ewolucji, suwak głośności i ekran końcowy.

## 🛠️ Wymagania

Projekt korzysta z pakietu `pygame`. 

* Python 3.x
* pygame>=2.0.0

## 📥 Instalacja i uruchomienie

1. Sklonuj repozytorium na swój komputer:
   ```bash
   git clone https://github.com/szymonkacki/pygame_td.git
   ```
2. Przejdź do folderu z projektem:
   ```bash
   cd pygame_td
   ```
3. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
4. Uruchom grę:
   ```bash
   python main.py
   ```
## 🎮 Sterowanie w grze
* LPM (Lewy Przycisk Myszy): Budowa wieży w wyznaczonym wolnym slocie oraz interakcja z przyciskami w menu.
* PPM (Prawy Przycisk Myszy): Kliknięcie na wieżę ulepsza ją. Jeśli wieża osiągnęła 3. poziom, PPM otwiera menu ewolucji.
* ŚPM (Środkowy Przycisk / Scroll): Kliknięcie na wieżę powoduje jej sprzedaż i zwrot części poniesionych kosztów.
* ESC: Otwarcie menu pauzy podczas rozgrywki.

## 💡 Informacje techniczne
Kod został zorganizowany zgodnie z paradygmatem programowania obiektowego (OOP) i podzielony na moduły strukturalne (m.in. game_manager.py, tower.py, enemy.py, bullet.py), co gwarantuje jego czytelność i ułatwia wprowadzanie nowych funkcji.
