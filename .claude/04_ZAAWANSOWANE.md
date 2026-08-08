# 04 — Faza zaawansowana

**Warunek wejścia:** ukończone [MVP](03_MVP_BACKEND.md) i przynajmniej dwa tygodnie
realnego używania na własnych paragonach.

Kolejność faz Z1-Z6 jest rekomendacją opartą o stosunek wartości do ryzyka, a nie sztywnym
harmonogramem. Po MVP będziesz mieć własne dane i własne obserwacje — one powinny
przeważyć nad tą listą.

---

## Z1 — Wdrożenie i przejście na AWS S3

**Kiedy:** zaraz po MVP · **Szacunek:** 2-3 dni

To domknięcie decyzji D2: MinIO był świadomym wyborem na czas pisania backendu,
teraz aplikacja musi być dostępna z zewnątrz.

### Przejście MinIO → AWS S3

Dzięki abstrakcji `IStorageRepository` to jest **zmiana konfiguracji, nie kodu**:

```dotenv
AWS_ENDPOINT_URL=                      # puste → AWS zamiast MinIO
AWS_ACCESS_KEY=AKIA...
AWS_ACCESS_KEY_SECRET=...
AWS_S3_BUCKET_NAME=coin-master-prod
AWS_REGION_NAME=eu-central-1           # Frankfurt — dane w UE (RODO)
```

Do zrobienia po stronie AWS:
- bucket z **zablokowanym dostępem publicznym** (Block Public Access — wszystkie cztery opcje),
- użytkownik IAM z polityką ograniczoną do `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`
  **na tym jednym buckecie** — nie `AdministratorAccess`,
- szyfrowanie w spoczynku (SSE-S3 wystarczy),
- wersjonowanie obiektów (ochrona przed przypadkowym usunięciem),
- reguła cyklu życia: przeniesienie do klasy Infrequent Access po 90 dniach — zdjęcia
  paragonów rzadko się ogląda, a taniej.

> **Free Tier:** 5 GB, 20 000 żądań GET i 2 000 PUT miesięcznie przez 12 miesięcy.
> Przy zdjęciu ~500 KB to około 10 000 paragonów. Na własny użytek wystarczy z nawiązką.
> **Ustaw alarm budżetowy** w AWS Billing na kwotę rzędu 5 USD — free tier wygasa po roku
> i lepiej dowiedzieć się o tym z alertu niż z faktury.

MinIO zostaje w `docker-compose.yml` jako środowisko deweloperskie i pod testy integracyjne.
To docelowy układ, nie tymczasowy.

### Wdrożenie

- Docker Compose na jednym VPS (Hetzner / DigitalOcean) — na tym etapie w zupełności wystarczy
- HTTPS przez Let's Encrypt (nginx jest już w kompozycji)
- Automatyczne kopie zapasowe PostgreSQL (`pg_dump` + wysyłka do S3, codziennie)
- `RUN_ENV=production` → aktywuje Sentry (`infrastructure/app.py:41`)
- Migracje uruchamiane przy starcie kontenera albo osobnym krokiem w pipelinie

---

## Z2 — OCR

**Kiedy:** gdy ręczne wprowadzanie zacznie męczyć · **Szacunek:** 5-10 dni (duża niepewność)

### Uczciwe ostrzeżenie

To najbardziej ryzykowna część projektu. Polskie paragony fiskalne to najtrudniejszy
możliwy materiał dla OCR: papier termiczny, wąska czcionka, nierówny druk, zagniecenia,
zdjęcia pod kątem, blaknięcie. **Tesseract na surowym zdjęciu paragonu z telefonu daje
wyniki na granicy użyteczności.**

Dlatego OCR jest zaplanowany jako **spike z twardym ograniczeniem czasu**, a nie jako
etap z terminem oddania.

### Etap 1 — rozpoznanie (2 dni, sztywny limit)

**Pełny plan tych dwóch dni: [06_OCR_SPIKE.md](06_OCR_SPIKE.md)** — osobny dokument roboczy
z listą zdjęć do zebrania, skryptem porównawczym, tabelą wyników i kryteriami decyzyjnymi
ustalonymi z góry.

W skrócie: 20 realnych zdjęć własnych paragonów przepuszczonych przez Tesseract, EasyOCR,
Google Cloud Vision i AWS Textract. Mierzone trzy pola — **kwota łączna**, **data**,
**nazwa sklepu**. Wynik: tabela z liczbami i decyzja, którego dostawcę wybieramy
(albo czy OCR w ogóle wchodzi do produktu).

> Zdjęcia do spike'u warto zbierać **już w trakcie MVP** — inaczej pierwszy dzień
> zejdzie na fotografowanie paragonów zamiast na badanie.

### Etap 2 — architektura

Zgodnie z istniejącym wzorcem w projekcie — interfejs, potem implementacje:

```python
# app/domain/ocr/base.py
class IOcrProvider:
    async def extract(self, image_data: bytes) -> OcrResult: ...
```

Implementacje: `TesseractOcrProvider`, `GoogleVisionOcrProvider`, `FakeOcrProvider` (testy).
Wybór przez konfigurację, rejestracja w `ServiceContainer` — dokładnie tak jak storage.
Dzięki temu zmiana dostawcy nie dotyka reszty aplikacji.

### Etap 3 — przetwarzanie w tle

OCR trwa kilka sekund, więc nie może blokować odpowiedzi HTTP:

```
POST /v2/receipts/{uuid}/scan/    → 202 Accepted, ocr_status="pending"
GET  /v2/receipts/{uuid}/         → ocr_status="done" + ocr_suggestions
```

Tu wchodzi **Redis** (zależność już jest w `pyproject.toml:18`, dotąd nieużywana) jako broker
dla kolejki. Rekomendacja: `arq` — lżejszy i natywnie asynchroniczny, lepiej pasuje do tego
stacku niż Celery.

### Etap 4 — degradacja z godnością

Zgodnie z pierwotnym założeniem z `plan_dzialnia.txt`:

- OCR **proponuje**, użytkownik **zatwierdza** — nic nie zapisuje się automatycznie
- Każde pole ma poziom pewności; niepewne są wyróżnione do sprawdzenia
- Kompletna porażka OCR = zwykłe wprowadzanie ręczne, żadnego błędu w twarz
- Sugestia kategorii na podstawie `normalized_name` i wcześniejszych wyborów użytkownika
  (zwykłe dopasowanie po historii — bez uczenia maszynowego)

---

## Z3 — Gwarancje i przypomnienia

**Kiedy:** po Z1 · **Szacunek:** 3-4 dni

```python
class Warranty(Base):
    __tablename__ = "warranties"

    item_id: Mapped[int] = mapped_column(sa.ForeignKey("items.id"))
    months: Mapped[int]                              # 24, 12, 60...
    expires_at: Mapped[date] = mapped_column(index=True)
    notify_days_before: Mapped[int] = mapped_column(server_default="14")
    notified_at: Mapped[datetime | None]
    notes: Mapped[str | None]
```

`expires_at` wyliczane z `receipt.purchase_date + months`, ale **edytowalne** — gwarancja
producenta bywa liczona od innej daty.

Zakres:
- `POST /v2/items/{uuid}/warranty/`, `GET /v2/warranties/?active=true`
- Zadanie cykliczne raz dziennie: znajdź wygasające, wyślij maila, zapisz `notified_at`
  (`notified_at` chroni przed wysłaniem tego samego przypomnienia dwa razy)
- Szablon e-mail w bazie — infrastruktura już istnieje
- Zgoda użytkownika wymagana (RODO): nowa encja `UserPreferences` z `warranty_notifications: bool`
- W mailu przypominającym: **link do paragonu presigned na 7 dni** — dokładnie ten mechanizm
  z MVP, w praktycznym zastosowaniu

Scheduler: `arq` z zadaniami cyklicznymi (jeśli wszedł przy Z2) albo systemowy `cron`
wywołujący komendę CLI — `asyncclick` jest już w projekcie i są gotowe komendy w `presentation/cli/`.

---

## Z4 — Analityka rozszerzona i eksport

**Kiedy:** gdy uzbierasz kilka miesięcy danych · **Szacunek:** 4-5 dni

Wcześniej nie ma sensu — analityka na dwóch tygodniach danych nic nie pokazuje.

- Porównanie okresów („ten miesiąc vs poprzedni", „ten rok vs zeszły")
- Trend cen z linią regresji — ile realnie zdrożało mleko przez rok
- Budżety miesięczne per kategoria + alert po przekroczeniu
- Wykrywanie nietypowych wydatków (odchylenie od Twojej własnej normy)
- Eksport CSV — do arkusza kalkulacyjnego
- Eksport PDF — zestawienie miesięczne (`weasyprint` albo `reportlab`)
- Cache w Redisie dla ciężkich agregacji, unieważniany przy zmianie paragonu
- Materializowane widoki w PostgreSQL, jeśli zapytania zaczną zwalniać
- Pełne drzewo kategorii (wielopoziomowe — w MVO celowo ograniczone do jednego poziomu)
- Ręczne scalanie produktów, jeśli auto-normalizacja (D6) okaże się za mało dokładna

---

## Z5 — Aplikacja mobilna

**Kiedy:** dopiero po ustabilizowaniu API · **Szacunek:** 15-20 dni

Zgodnie z decyzją D7 front powstaje na końcu. Powód jest praktyczny: przepisywanie ekranów
pod zmieniające się API kosztuje więcej niż poczekanie, aż API przestanie się zmieniać.

React Native + Expo. Ekrany:
1. Logowanie i rejestracja
2. **Aparat** — zdjęcie paragonu, kadrowanie, podgląd
3. Formularz paragonu (wypełniony sugestiami OCR, jeśli Z2 gotowe)
4. Lista paragonów z filtrami i wyszukiwaniem
5. Szczegóły paragonu + pozycje + podgląd zdjęcia
6. Pulpit analityczny z wykresami
7. Historia cen produktu
8. Gwarancje z odznaką liczby wygasających
9. Ustawienia i profil — awatar, zgody na powiadomienia

Elementy interfejsu z Twojej pierwotnej wizji (sekcja profilu z awatarem, zgoda na
przypomnienia o gwarancjach, odznaka z alertami w ustawieniach) wchodzą właśnie tutaj.

Techniczne:
- Tryb offline — paragon dodany bez zasięgu synchronizuje się później
- Bezpieczne przechowywanie tokenu (`expo-secure-store`, nie `AsyncStorage`)
- Kompresja zdjęć **przed** wysyłką — oszczędza transfer i miejsce w S3
- Powiadomienia push (`expo-notifications`) jako uzupełnienie e-maili z Z3

---

## Z6 — Dojrzałość infrastruktury

**Kiedy:** gdy zaczną boleć konkretne rzeczy · bez sztywnego szacunku

### Narzędzia deweloperskie

- **Ruff** — jest już zainstalowany (`pyproject.toml:52`) i nieużywany. Zastępuje flake8
  i isort, jest kilkadziesiąt razy szybszy. Migracja: dodać `[tool.ruff]` z `line-length = 120`,
  włączyć reguły odpowiadające obecnym wtyczkom flake8 (`B` — bugbear, `C4` — comprehensions,
  `SIM` — simplify), usunąć flake8 i isort z zależności oraz z `.pre-commit-config.yaml`.
  Black może zostać albo ustąpić `ruff format`.
- **UV** — jeśli nie zrobione w [Fazie 0](02_NAPRAWY_PRZED_MVP.md#krok-6--migracja-poetry--uv-05-dnia-opcjonalnie)
- **mypy w trybie ścisłym** — obecnie `strict` jest zakomentowany (`pyproject.toml:131`).
  Włączać modułami, nie wszystko naraz
- Testy mutacyjne (`mutmut`) — sprawdzają, czy 100% pokrycia oznacza faktycznie
  sensowne asercje, czy tylko wywołanie każdej linijki

### Skalowanie — dopiero gdy będzie potrzebne

**Kubernetes ma sens dopiero przy realnym ruchu i zespole.** Przy aplikacji na własny użytek
to koszt bez zysku. Zanim tam pójdziesz, przejdź kolejno:

1. Jeden VPS z Docker Compose ← **tu wystarczy być bardzo długo**
2. Osobny zarządzany PostgreSQL (RDS / DigitalOcean Managed)
3. Wiele instancji API za load balancerem
4. Dopiero teraz Kubernetes, jeśli w ogóle

Gdy już — potrzebne będą: Helm chart, sondy `liveness` i `readiness` (endpoint `/healthz/`
jest gotowy), `HorizontalPodAutoscaler`, sekrety przez External Secrets Operator.

### Obserwowalność

- Sentry jest skonfigurowane — dodać `traces_sample_rate` dla śledzenia wydajności
- Logi strukturalne w JSON zamiast tekstu (`LogConfig` w `infrastructure/logger.py`)
- Prometheus + Grafana, gdy pojawi się realny ruch
- Testy obciążeniowe — `locust` jest w zależnościach (`pyproject.toml:53`), brak scenariuszy

### Bezpieczeństwo i RODO

- Ograniczanie liczby żądań (rate limiting) na endpointach logowania i uploadu
- Rotacja kluczy AWS
- `POST /v2/users/me/export/` — eksport wszystkich danych użytkownika (RODO, prawo do przenoszenia)
- `DELETE /v2/users/me/` — usunięcie konta wraz z plikami z bucketa (prawo do bycia zapomnianym).
  Podział kluczy po `user_uuid` z MVP został zaprojektowany właśnie pod to
- Skanowanie zależności (`pip-audit`, Dependabot)

---

## Czego świadomie nie planujemy

| Pomysł | Dlaczego nie |
|---|---|
| Współdzielenie paragonów między kontami | Sprzeczne z decyzją D1. Do przemyślenia jako „konto rodzinne", ale to inny produkt |
| Porównywanie cen między użytkownikami | Wykluczone decyzją D1 |
| Integracje z bankami | Ogromny nakład prawny i techniczny, mała wartość dla tego produktu |
| Własny model ML do rozpoznawania paragonów | Gotowe API kosztują grosze i są lepsze |
| Monetyzacja | Zgodnie z `plan_dzialnia.txt` — dopiero po potwierdzeniu, że produkt jest komuś potrzebny |
