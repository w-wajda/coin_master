# 06 — Spike OCR (2 dni, twardy limit)

Dokument roboczy do wykonania **w całości w ciągu dwóch dni**.
Należy do fazy [Z2](04_ZAAWANSOWANE.md#z2--ocr), ale jest wydzielony, bo rządzi się
innymi regułami niż reszta planu.

---

## Czym jest spike i dlaczego OCR go dostaje

**Spike to krótkie zadanie badawcze, którego produktem jest decyzja, a nie działający kod.**

| Zwykłe zadanie | Spike |
|---|---|
| „Zaimplementuj OCR" | „W 2 dni ustal, który OCR wybrać" |
| Skończone, gdy działa | Skończone, gdy minie czas |
| Efekt: kod na produkcji | Efekt: tabela z liczbami + decyzja |
| Nie wiadomo, ile zajmie | Wiadomo dokładnie: 2 dni |

**Twardy limit** oznacza, że po upływie dwóch dni przerywasz — niezależnie od tego,
czy jesteś zadowolona z wyniku.

### Dlaczego akurat tu

OCR na polskich paragonach fiskalnych to podręcznikowa pułapka „jeszcze jedna poprawka
i zadziała". Poprawiasz kontrast — z 7/20 robi się 9/20. Dodajesz prostowanie perspektywy —
11/20. Wycinanie tła — 12/20. Każdy krok daje poprawę, więc każdy wygląda na sensowny,
i po trzech tygodniach masz 14/20 — nadal za mało, żeby zaufać, a trzy tygodnie przepadły.

**Limit czasu jest zabezpieczeniem przed własnym optymizmem, nie przed brakiem umiejętności.**
Ustawiasz go, zanim zaczniesz, właśnie dlatego, że w trakcie nie będziesz chciała przerwać.

---

## Przygotowanie (zrób zawczasu, poza limitem 2 dni)

Zbieraj zdjęcia paragonów **już teraz**, w trakcie MVP — do spike'u wchodzisz z gotowym
materiałem, inaczej pierwszy dzień zejdzie na fotografowanie.

**Potrzebujesz 20 zdjęć**, w tym celowo trudne:

| Ile | Rodzaj |
|---|---|
| 8 | Dobre warunki — prosto, ostro, dobre światło |
| 4 | Pod kątem, perspektywa |
| 3 | Zagniecione lub pogięte |
| 2 | Wyblakłe (paragon sprzed kilku miesięcy) |
| 2 | Długie (kilkanaście pozycji, paragon się zwija) |
| 1 | Kiepskie światło / cień |

Do tego **arkusz z prawdą** — dla każdego zdjęcia wpisujesz ręcznie, co jest na paragonie:

```csv
# tests/ocr_samples/ground_truth.csv
file,amount,purchase_date,company
001.jpg,127.45,2026-07-15,Biedronka
002.jpg,38.90,2026-07-18,Lidl
...
```

Bez tego arkusza nie da się nic zmierzyć — a mierzenie jest całym sensem spike'u.

> **Uwaga:** te zdjęcia i CSV **nie wchodzą do repozytorium** — to Twoje realne paragony
> z danymi osobowymi. Trzymaj je lokalnie, dopisz katalog do `.gitignore`.

---

## Co mierzymy

Tylko **trzy pola**, bo tylko one realnie oszczędzają czas przy wprowadzaniu:

1. **Kwota łączna** — najważniejsza, bez niej paragon jest bezużyteczny
2. **Data zakupu**
3. **Nazwa sklepu**

Ocena binarna: zgadza się / nie zgadza. Bez punktów cząstkowych, bez „prawie dobrze".

**Pozycji paragonu celowo nie mierzymy** w spike'u — są znacznie trudniejsze i nie zmienią
decyzji o wyborze dostawcy. Jeśli któreś rozwiązanie dobrze radzi sobie z trzema polami,
z pozycjami też będzie najlepsze.

---

## Dzień 1 — rozwiązania darmowe

### Rano: przygotowanie stanowiska

```bash
# Tesseract z modelem polskim
brew install tesseract tesseract-lang
uv pip install pytesseract easyocr opencv-python pillow-heif

# sprawdzenie, że model 'pol' jest dostępny
tesseract --list-langs | grep pol
```

`pillow-heif` jest potrzebny, jeśli zdjęcia pochodzą z iPhone'a — to ten sam problem,
który czeka nas przy miniaturach w [MVP](03_MVP_BACKEND.md#miniatury).

### Skrypt porównawczy

Jeden plik, uruchamiany dla każdego dostawcy. Nie buduj tu architektury — to kod
do wyrzucenia po spike'u.

```python
# scripts/ocr_spike/run.py
"""Przepuszcza 20 zdjęć przez wybranego dostawcę i zapisuje wynik do CSV."""

def extract_amount(text: str) -> Decimal | None:
    """Największa kwota w tekście albo linia po 'SUMA' / 'RAZEM' / 'PLN'."""

def extract_date(text: str) -> date | None:
    """Wzorce: DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD."""

def extract_company(text: str) -> str | None:
    """Zwykle w pierwszych 3 liniach paragonu."""

# wynik → results_{provider}.csv: file,amount,date,company,seconds
```

Parsowanie ma być **proste i takie samo dla wszystkich dostawców** — porównujemy jakość
rozpoznania tekstu, nie sprytność regexów. Nierówne parsery unieważniłyby porównanie.

### Po południu: Tesseract i EasyOCR

**Tesseract** — jedno standardowe przygotowanie obrazu, **i ani kroku dalej**:

```python
# skala szarości → wyrównanie kontrastu → progowanie adaptacyjne
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.createCLAHE(clipLimit=2.0).apply(img)
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
text = pytesseract.image_to_string(img, lang="pol", config="--psm 6")
```

> ⚠️ **Tu jest pułapka.** Będziesz mieć pokusę, żeby dokładać kolejne filtry.
> **Nie rób tego.** Jeden przebieg, wynik do tabeli, idziesz dalej.

**EasyOCR** — działa lepiej na krzywych zdjęciach, bez przygotowania obrazu:

```python
reader = easyocr.Reader(["pl"], gpu=False)
text = " ".join(reader.readtext(path, detail=0))
```

Pierwsze uruchomienie pobiera model (~100 MB) i jest wolne — to normalne.

**Koniec dnia 1:** dwa pliki `results_tesseract.csv` i `results_easyocr.csv`.

---

## Dzień 2 — rozwiązania płatne

### Uwaga o prywatności — przeczytaj przed rozpoczęciem

Wysyłasz **własne paragony do zewnętrznej firmy**. Paragony bywają powiązane z kartą płatniczą
i lokalizacją. Do świadomej decyzji:

- Google i AWS deklarują, że nie używają danych z API do trenowania modeli
- Można wskazać region UE (Frankfurt) — dane nie opuszczają Unii
- Przy aplikacji na własny użytek to zwykle akceptowalne, ale **to Twoja decyzja**, nie oczywistość
- Gdyby aplikacja miała kiedyś obsługiwać innych użytkowników — potrzebna byłaby ich zgoda
  i wpis w polityce prywatności

Jeśli to dla Ciebie zaporowe — zostajesz przy rozwiązaniach z dnia 1 i spike kończy się
wcześniej. To pełnoprawny wynik.

### Google Cloud Vision

```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()
response = client.document_text_detection(image=vision.Image(content=data))
text = response.full_text_annotation.text
```

Limit darmowy: około **1000 zdjęć miesięcznie**, potem rzędu 1,50 USD za 1000.
Konto Google Cloud + włączenie Vision API + klucz konta usługowego.

### AWS Textract

Ma dwa tryby i **warto sprawdzić oba** — różnią się ceną o rząd wielkości:

| Tryb | Co robi | Koszt orientacyjny |
|---|---|---|
| `DetectDocumentText` | Surowy tekst | ~1,50 USD / 1000 |
| `AnalyzeExpense` | Tryb dedykowany paragonom — sam zwraca `TOTAL`, `INVOICE_RECEIPT_DATE`, `VENDOR_NAME` | ~10 USD / 1000 |

`AnalyzeExpense` jest ciekawy, bo **zwraca gotowe pola bez własnego parsowania** — czyli
dokładnie te trzy, które mierzymy. Przy 50 paragonach miesięcznie droższy wariant to
około 2 zł miesięcznie.

> Ceny sprawdź w aktualnym cenniku — podane wartości są orientacyjne i mogą się zmienić.
> Konto AWS przyda się i tak przy [Z1](04_ZAAWANSOWANE.md#z1--wdrożenie-i-przejście-na-aws-s3).

**Koniec dnia 2:** cztery lub pięć plików CSV z wynikami.

---

## Tabela wynikowa

Zsumuj trafienia i wypełnij:

```
                        kwota    data    sklep   |  śr. czas  |  koszt/1000
Tesseract (pol)          __/20   __/20   __/20   |    __ s    |     0 zł
EasyOCR                  __/20   __/20   __/20   |    __ s    |     0 zł
Google Vision            __/20   __/20   __/20   |    __ s    |    ~6 zł
AWS DetectDocumentText   __/20   __/20   __/20   |    __ s    |    ~6 zł
AWS AnalyzeExpense       __/20   __/20   __/20   |    __ s    |   ~40 zł
```

---

## Kryteria decyzyjne

Ustalone **z góry**, żeby wynik nie podlegał negocjacjom po fakcie:

| Warunek | Decyzja |
|---|---|
| Darmowe rozwiązanie ma **≥ 16/20 na kwocie** (80%) | Bierzemy darmowe. Wystarczająco dobre |
| Darmowe ma **12-15/20** | Bierzemy płatne, ale zostawiamy darmowe jako zapasowe w interfejsie `IOcrProvider` |
| Darmowe ma **< 12/20** (60%) | Bierzemy płatne. Darmowe nie wchodzi do kodu w ogóle |
| Żadne nie przekracza 12/20 | **OCR wypada z planu.** Wracamy do tematu za rok, gdy modele będą lepsze |

Ostatni wiersz jest równie ważny jak pozostałe. „Nie robimy tego" to legalny wynik spike'u
i lepszy niż wleczenie funkcji, która nie działa.

**Przy kwocie 30 groszy miesięcznie za płatne API nie ma sensu walczyć o darmowe rozwiązanie
przez trzy tygodnie własnej pracy.** Ta arytmetyka powinna przeważyć nad odruchem
„ale przecież da się za darmo".

---

## Raport końcowy

Po dwóch dniach dopisz tutaj wynik — dokument zostaje w repo jako uzasadnienie decyzji:

```markdown
## WYNIK SPIKE'U

Data wykonania:
Liczba zdjęć testowych:

| Rozwiązanie | kwota | data | sklep | czas | koszt/1000 |
|---|---|---|---|---|---|
| ... | | | | | |

**Decyzja:**
**Uzasadnienie:**
**Zaskoczenia / obserwacje:**
**Szacunek właściwej implementacji:** ___ dni
```

---

## Poza zakresem spike'u

Świadomie **nie** robimy tych dwóch dni:

- interfejsu `IOcrProvider` ani integracji z kontenerem DI
- przetwarzania w tle (Redis, `arq`)
- rozpoznawania pozycji paragonu
- interfejsu „OCR proponuje, użytkownik zatwierdza"
- testów jednostkowych skryptu porównawczego
- podpowiadania kategorii

To wszystko należy do właściwej implementacji Z2 — i można ją sensownie oszacować
**dopiero po tym, jak spike da odpowiedź**.

Kod ze spike'u (`scripts/ocr_spike/`) jest jednorazowy. Nie refaktoryzuj go, nie testuj,
nie wciągaj do `app/`. Po wpisaniu wyniku do raportu można go usunąć.
