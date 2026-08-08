# 03 — MVP (backend)

**Warunek wejścia:** ukończona [Faza 0](02_NAPRAWY_PRZED_MVP.md).
**Szacunek:** 8-12 dni roboczych.
**Zakres:** wyłącznie backend. Front (React Native) → [04_ZAAWANSOWANE.md](04_ZAAWANSOWANE.md).

---

## Co ma umieć MVP

> Robię zdjęcie paragonu albo wpisuję go ręcznie. Uzupełniam sklep, datę, kwotę i pozycje
> z kategoriami. Widzę listę swoich paragonów i mogę je filtrować. Widzę ile wydałam
> w danym miesiącu i na co. Widzę jak zmieniała się cena mleka we wszystkich sklepach,
> w których je kupowałam. Mogę wysłać paragon komuś linkiem albo mailem jako załącznik.

Czego MVP **nie** robi: OCR, gwarancje, powiadomienia, aplikacja mobilna.

---

## Kryterium sukcesu

MVP jest ukończone, gdy **przez 2 tygodnie realnie używasz go do wprowadzania własnych
paragonów** (przez Swagger / HTTP client) i nie natrafiasz na blokery. To jest ważniejsze
kryterium niż lista odhaczonych endpointów — dopiero prawdziwe dane pokazują, czego brakuje
w modelu.

---

## Model danych

### `Receipt` — zmiany

```python
class Receipt(Base):
    __tablename__ = "receipts"

    amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    purchase_date: Mapped[date] = mapped_column(sa.Date, nullable=False, index=True)   # NOWE
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)                  # NOWE

    # zdjęcie — opcjonalne (decyzja D5), przechowywany KLUCZ w buckecie, nie URL
    scan_file: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)       # ZMIANA
    thumbnail_file: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)  # NOWE

    company_id: Mapped[int | None] = mapped_column(                                    # ZMIANA
        sa.Integer, sa.ForeignKey("companies.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"), index=True)
```

**Dlaczego klucz, a nie URL:** przy prywatnym buckecie (D3) URL jest generowany na żądanie
i wygasa. Zapisywanie go w bazie nie miałoby sensu — po 15 minutach byłby bezużyteczny.
W bazie trzymamy `receipts/{user_uuid}/{receipt_uuid}/{losowy}.jpg`, a URL powstaje przy
każdym odczycie.

### `Item` — zmiany

```python
class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    normalized_name: Mapped[str] = mapped_column(sa.String(256), nullable=False, index=True)  # NOWE (D6)

    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)   # cena łączna pozycji
    quantity: Mapped[Decimal] = mapped_column(                                  # NOWE
        sa.Numeric(10, 3), nullable=False, server_default="1"
    )
    unit: Mapped[str] = mapped_column(sa.String(16), nullable=False, server_default="szt")  # NOWE
    unit_price: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2), nullable=True)    # NOWE

    category_id: Mapped[int | None] = mapped_column(                            # NOWE
        sa.Integer, sa.ForeignKey("categories.id"), nullable=True
    )
    receipt_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("receipts.id"), index=True)
```

**`price` vs `unit_price`:** `price` to kwota z paragonu za całą pozycję (2 kg jabłek = 12,00 zł),
`unit_price` to cena jednostkowa (6,00 zł/kg). Jeśli użytkownik poda tylko jedno,
drugie wyliczamy — reguła w tabeli walidacji niżej.

### `Category` — nowa encja

```python
class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)   # nazwa/emoji dla frontu
    color: Mapped[str | None] = mapped_column(sa.String(7), nullable=True)   # #RRGGBB

    parent_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("categories.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"), index=True)

    __table_args__ = (sa.UniqueConstraint("user_id", "name", "parent_id"),)
```

Hierarchia jest **jednopoziomowa w MVP** — `parent_id` istnieje w schemacie, ale walidacja
nie pozwala tworzyć wnuków. Pełne drzewo w fazie zaawansowanej.

**Kategorie domyślne** zakładane przy rejestracji użytkownika:

```
Spożywcze · Chemia i higiena · Dom i ogród · Odzież i obuwie · Elektronika
Zdrowie i leki · Transport i paliwo · Rozrywka · Restauracje · Dzieci
Zwierzęta · Prezenty · Inne
```

Lista jako stała w `app/domain/categories/defaults.py`. Użytkownik może je zmieniać i usuwać.

### `Company` — bez zmian strukturalnych

Zostaje `user_id` — zgodnie z decyzją D1 zakres jest jednoosobowy, więc „moja Biedronka"
w mojej bazie jest wystarczająca. Opcjonalnie `city: str | None`, jeśli okaże się przydatne
przy wielu sklepach tej samej sieci.

### Podsumowanie migracji

Jedna migracja Alembica obejmująca:
1. `receipts`: + `purchase_date`, + `notes`, + `thumbnail_file`, `scan_file` → nullable, `company_id` → nullable
2. `items`: + `normalized_name`, + `quantity`, + `unit`, + `unit_price`, + `category_id`
3. `categories`: nowa tabela
4. indeksy: `receipts.purchase_date`, `receipts.user_id`, `items.normalized_name`, `items.receipt_id`

> **Uwaga przy `purchase_date NOT NULL`:** jeśli w bazie są już jakiekolwiek paragony,
> migracja musi najpierw dodać kolumnę jako nullable, wypełnić ją wartością `created`,
> a dopiero potem nałożyć `NOT NULL`.

---

## Normalizacja nazw produktów (D6)

Sercem historii cen jest funkcja czysta, łatwa do przetestowania:

**Plik:** `app/domain/items/normalization.py`

```python
def normalize_product_name(name: str) -> str:
    """
    "Mleko UHT 3,2% 1L"  →  "mleko uht 32 1l"
    "MLEKO  uht 3.2%"    →  "mleko uht 32"
    """
```

Kroki: małe litery → usunięcie znaków interpunkcyjnych i symboli (`%`, `,`, `.`, `-`) →
redukcja wielokrotnych spacji → `strip()`.

Wywoływana w `CreateItemCommand` i `UpdateItemCommand` przy każdym zapisie.
**Nie** jako `@property` — musi być kolumną w bazie, żeby dało się po niej grupować i indeksować.

**Świadome ograniczenie:** normalizacja czasem połączy różne produkty albo rozdzieli te same
(„Mleko 3,2% Łaciate" ≠ „Łaciate mleko 3,2%"). To akceptowalne w MVP. Jeśli okaże się
uciążliwe przy realnym używaniu — w fazie zaawansowanej dochodzi ręczne scalanie produktów.

---

## Warstwa storage

### Rozszerzenie interfejsu

**Plik:** `app/infrastructure/storage/base.py`

```python
class IStorageRepository:
    async def save(self, file_data, file_name: str) -> str: ...
    async def delete(self, file_name: str) -> None: ...                       # NOWE
    def get_path(self) -> Path: ...
    def get_url(self, file_name: str) -> str: ...
    def get_presigned_url(self, file_name: str, expires_in: int) -> str: ...  # NOWE
```

Wszystkie trzy implementacje (`S3StorageRepository`, `FakeS3StorageRepository`
oraz interfejs) muszą dostać nowe metody.

### `generate_presigned_url` w boto3

```python
def get_presigned_url(self, file_name: str, expires_in: int) -> str:
    return self.s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": self.bucket_name, "Key": file_name},
        ExpiresIn=min(expires_in, 604800),   # twardy limit AWS SigV4
    )
```

`min(..., 604800)` to zabezpieczenie: AWS odrzuca dłuższe podpisy, a błąd byłby mylący.

### Nazewnictwo plików w buckecie

```
receipts/{user_uuid}/{receipt_uuid}/{uuid4}.jpg
receipts/{user_uuid}/{receipt_uuid}/{uuid4}_thumb.jpg
```

`uuid4` w nazwie sprawia, że klucza nie da się zgadnąć nawet znając identyfikator paragonu.
Podział po `user_uuid` ułatwia późniejsze usunięcie wszystkich danych użytkownika (RODO).

### Miniatury

`ThumbnailGenerator` jest już napisany (`infrastructure/image_processing/thumbnail_generator.py`)
i wystarczy go podpiąć. Rozmiar: **400×400, jakość 85**. Miniatura idzie do tego samego bucketa
w tym samym momencie co oryginał.

> **Uwaga:** obecna implementacja zapisuje w `image.format` — dla HEIC z iPhone'a to się nie uda
> bez `pillow-heif`. Do rozważenia: wymuszenie konwersji do JPEG na wejściu.

### Walidacja pliku

| Reguła | Wartość |
|---|---|
| Maksymalny rozmiar | 10 MB |
| Dozwolone formaty | JPEG, PNG, HEIC |
| Weryfikacja typu | **`Image.open()` z Pillow**, nie `content-type` z nagłówka |
| Zachowanie przy błędzie | 400 z czytelnym komunikatem, brak zapisu w buckecie |

Sprawdzanie samego `content-type` jest bezwartościowe — klient może wysłać cokolwiek.

---

## Endpointy

Legenda: 🆕 nowy · 🔧 istnieje, wymaga zmian · ✅ istnieje, działa po Fazie 0

### Paragony

| | Metoda i ścieżka | Opis |
|---|---|---|
| ✅ | `GET /v2/receipts/` | Lista z paginacją |
| 🔧 | `GET /v2/receipts/` | + filtry: `date_from`, `date_to`, `company_uuid`, `category_uuid`, `tag_uuid`, `q` |
| ✅ | `GET /v2/receipts/{uuid}/` | Szczegóły + pozycje + `scan_url` (presigned 15 min) |
| 🔧 | `POST /v2/receipts/` | + `purchase_date`, `notes`, `company_uuid`; bez zdjęcia |
| ✅ | `PATCH /v2/receipts/{uuid}/` | Edycja |
| ✅ | `DELETE /v2/receipts/{uuid}/` | Usuwa też pliki z bucketa |
| 🆕 | `POST /v2/receipts/{uuid}/scan/` | Upload zdjęcia (`multipart/form-data`) + miniatura |
| 🆕 | `DELETE /v2/receipts/{uuid}/scan/` | Usunięcie zdjęcia (paragon zostaje — D5) |
| 🆕 | `POST /v2/receipts/{uuid}/share/` | Link presigned na 7 dni (D3) |
| 🆕 | `POST /v2/receipts/{uuid}/send-email/` | Wysyłka mailem z **załącznikiem** (D4) |

### Pozycje

| | Metoda i ścieżka |
|---|---|
| ✅ | `GET /v2/receipts/{receipt_uuid}/items/` |
| 🔧 | `POST /v2/receipts/{receipt_uuid}/items/` — + `quantity`, `unit`, `unit_price`, `category_uuid` |
| 🔧 | `PATCH /v2/receipts/{receipt_uuid}/items/{uuid}/` |
| ✅ | `DELETE /v2/receipts/{receipt_uuid}/items/{uuid}/` |
| 🆕 | `POST /v2/receipts/{receipt_uuid}/items/bulk/` | Dodanie wielu pozycji jednym requestem |

`bulk` jest ważny: wprowadzanie 20-pozycyjnego paragonu po jednym requeście to droga przez mękę,
a przy OCR (faza zaawansowana) i tak będzie potrzebny.

### Kategorie 🆕

`GET` / `POST /v2/categories/`, `PATCH` / `DELETE /v2/categories/{uuid}/`

Usunięcie kategorii używanej przez pozycje → `category_id` ustawiane na `NULL`, pozycje zostają.

### Analityka 🆕

| Ścieżka | Zwraca |
|---|---|
| `GET /v2/analytics/summary?date_from&date_to` | Suma wydatków, liczba paragonów, średni paragon |
| `GET /v2/analytics/by-category?date_from&date_to` | Wydatki w rozbiciu na kategorie + udział % |
| `GET /v2/analytics/by-period?granularity=day\|week\|month\|year` | Szereg czasowy wydatków |
| `GET /v2/analytics/top-products?limit=10` | Najczęściej kupowane wg `normalized_name` |

Wszystko liczone **agregacją w SQL** (`func.sum`, `func.date_trunc`, `group_by`),
nie w Pythonie po pobraniu wszystkich rekordów.

### Produkty i historia cen 🆕

| Ścieżka | Zwraca |
|---|---|
| `GET /v2/products/?q=mleko` | Unikalne `normalized_name` + ostatnia cena + liczba zakupów |
| `GET /v2/products/{normalized_name}/price-history` | Punkty `(purchase_date, unit_price, sklep)` posortowane w czasie |

To jest realizacja Twojego wymagania „ile ogólnie kosztowało mleko we wszystkich sklepach" —
w obrębie własnych paragonów (D1). Odpowiedź zawiera też `min`, `max` i `avg` ceny jednostkowej.

---

## Reguły walidacji i logiki

| Reguła | Zachowanie |
|---|---|
| `amount` | > 0, maksymalnie 2 miejsca po przecinku |
| `purchase_date` | Nie może być w przyszłości |
| `quantity` | > 0 |
| `unit_price` | Jeśli podano `quantity` i `price` a brak `unit_price` → wyliczane jako `price / quantity` |
| `price` | Jeśli podano `quantity` i `unit_price` a brak `price` → wyliczane jako `quantity * unit_price` |
| `unit` | Zbiór zamknięty: `szt`, `kg`, `g`, `l`, `ml`, `m`, `opak` |
| Suma pozycji vs `amount` | **Nie blokuje zapisu.** `amount` z paragonu jest źródłem prawdy |
| Własność zasobu | Każde zapytanie filtruje po `user_id` — także przed wygenerowaniem presigned URL |

**Rozstrzygnięcie sporu `amount` vs suma pozycji:** paragon bywa niekompletnie wprowadzony
(wpisujesz 3 najważniejsze pozycje z 20), więc wymuszanie zgodności byłoby uciążliwe.
Zamiast blokady API zwraca w odpowiedzi pola informacyjne:

```json
{
  "amount": "127.45",
  "items_total": "89.20",
  "is_balanced": false
}
```

Front zdecyduje, czy pokazać ostrzeżenie.

---

## Wysyłka mailem z załącznikiem (D4)

Przypadek użycia: **reklamacja w sklepie po trzech tygodniach** — odbiorca otwiera maila
i widzi paragon, niezależnie od tego czy jakikolwiek link jeszcze żyje.

```
POST /v2/receipts/{uuid}/send-email/
{
  "to": "sklep@example.com",
  "message": "W załączeniu paragon do reklamacji z dnia 2026-07-15"
}
```

Przebieg: sprawdzenie właściciela → pobranie oryginału z bucketa → załącznik w `fastapi-mail` →
szablon z bazy (`email_template_repository` już istnieje) → wysyłka.

Ograniczenia: maksymalnie 5 wysyłek na paragon dziennie (ochrona przed użyciem konta do spamu),
odbiorca musi być poprawnym adresem e-mail.

---

## Kolejność prac

| Etap | Zakres | Dni |
|---|---|---|
| 1 | Migracje + zmiany modeli + normalizacja nazw | 1.5 |
| 2 | `Category` — encja, CRUD, kategorie domyślne | 1 |
| 3 | Rozszerzenie storage'u (presigned, delete) + testy | 1 |
| 4 | Upload zdjęcia + miniatury + walidacja | 2 |
| 5 | Rozszerzenie schematów paragonów i pozycji + `bulk` | 1.5 |
| 6 | Filtry na liście paragonów | 1 |
| 7 | Analityka (4 endpointy) | 1.5 |
| 8 | Produkty i historia cen | 1 |
| 9 | Udostępnianie linkiem + wysyłka mailem | 1 |
| 10 | Dociągnięcie pokrycia do 100%, dokumentacja API | 1.5 |

Testy pisane **równolegle z każdym etapem**, nie w etapie 10 — tam zostaje tylko domykanie
brakujących gałęzi.

---

## Zadanie w tle na czas MVP

Podczas dwóch tygodni realnego używania **zbieraj zdjęcia paragonów do spike'u OCR** —
docelowo 20 sztuk, w tym celowo kiepskie (zagniecione, pod kątem, wyblakłe).
Lista i uzasadnienie: [06_OCR_SPIKE.md](06_OCR_SPIKE.md#przygotowanie-zrób-zawczasu-poza-limitem-2-dni).

Zero dodatkowej pracy teraz, a oszczędza cały pierwszy dzień spike'u później.

---

## Definicja ukończenia MVP

- [ ] Migracje przechodzą w obie strony (`upgrade head` i `downgrade`)
- [ ] Paragon da się dodać ręcznie bez zdjęcia (D5)
- [ ] Zdjęcie da się dograć później, miniatura powstaje automatycznie
- [ ] `GET /v2/receipts/{uuid}/` zwraca działający `scan_url` ważny 15 minut (D3)
- [ ] `POST /v2/receipts/{uuid}/share/` zwraca link działający w przeglądarce przez 7 dni
- [ ] Link po wygaśnięciu przestaje działać — **pokryte testem**
- [ ] Paragon wysłany mailem dociera z załącznikiem (D4)
- [ ] Bucket jest prywatny — próba wejścia bez podpisu zwraca 403, **pokryte testem**
- [ ] Kategorie domyślne zakładają się przy rejestracji
- [ ] Historia cen produktu grupuje zakupy z różnych sklepów (D6)
- [ ] Analityka zgadza się z ręcznym wyliczeniem na danych testowych
- [ ] Użytkownik nie ma dostępu do cudzych paragonów — **pokryte testem dla każdego endpointu**
- [ ] Usunięcie paragonu usuwa też pliki z bucketa
- [ ] **Pokrycie testami 100%**, próg `--cov-fail-under=100` włączony w `pyproject.toml`
- [ ] Swagger (`/docs`) opisuje wszystkie endpointy z przykładami
- [ ] Przez 2 tygodnie realnego używania nie pojawił się bloker

---

## Poza zakresem MVP

Świadomie odłożone → [04_ZAAWANSOWANE.md](04_ZAAWANSOWANE.md):

OCR · gwarancje i przypomnienia · aplikacja mobilna · eksport PDF/CSV · budżety i limity ·
współdzielenie z innymi użytkownikami · cache w Redisie · AWS S3 na produkcji ·
tagi w interfejsie (model gotowy, API nie) · powiadomienia push · wielowalutowość
