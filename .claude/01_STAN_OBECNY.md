# 01 — Stan obecny backendu

Analiza na dzień **2026-08-07**, gałąź `master`, ostatni commit `a631532`.
Wszystkie stwierdzenia zweryfikowane w kodzie — odwołania w formacie `plik:linia`.

---

## Podsumowanie w jednym akapicie

Repozytorium ma **bardzo dobrą architekturę i bardzo słaby stan wykonania**. Warstwy
(domain / application / infrastructure / presentation), wzorzec Command/Query, kontenery DI,
abstrakcja repozytoriów i storage'u — to wszystko jest przemyślane i warte zachowania.
Natomiast najważniejsza funkcjonalnie część API (`/v2/receipts/*`) **w ogóle nie działa**,
obsługa zdjęć nie jest podłączona do niczego, a testów jest zero. Fundament jest solidny,
ale trzeba go najpierw naprawić, zanim cokolwiek dobudujemy.

**Ocena gotowości do MVP: ~35%** — dużo napisanego kodu, mało kodu działającego.

---

## Stack (zweryfikowany)

| Element | Wersja / stan |
|---|---|
| Python | 3.12.7 |
| FastAPI | 0.115.4 |
| SQLAlchemy | 2.0.36 (async, `Mapped[]`, `mapper_registry`) |
| PostgreSQL | via `asyncpg`, obraz `postgis/postgis:16-3.4` |
| Alembic | 8 migracji, ostatnia `2024_12_04_2119` |
| DI | `dependency-injector` 4.43.0 |
| Storage | `boto3` — kod napisany, **niepodłączony** |
| Auth | własny backend tokenowy + `pwdlib[argon2]` |
| E-mail | `fastapi-mail` + szablony w bazie |
| Monitoring | `sentry-sdk` — aktywny tylko przy `RUN_ENV=production` |
| Lint | Black + isort + flake8 (+ bugbear, comprehensions, simplify), mypy |
| Testy | pytest — **0 testów** |
| Pakiety | Poetry (`poetry.lock` obecny) |

Rozmiar: **156 plików `.py`** w `app/`.

---

## Co działa i jest warte zachowania

- **Podział na warstwy** — czysty, konsekwentny, bez przecieków domeny do infrastruktury.
- **Command / Query separation** — 23 komendy i 12 zapytań w `app/application/`.
- **Repozytoria** — `GenericSQLAlchemyRepository` z interfejsem `IBaseRepository`.
  Metody generyczne (`get`, `get_by`, `get_list`, `commit`, `delete`) są napisane poprawnie.
- **Abstrakcja storage'u** — `IStorageRepository` (`storage/base.py`) z dwiema implementacjami:
  `S3StorageRepository` i `FakeS3StorageRepository`. To jest bardzo dobra decyzja —
  dzięki niej przełączenie MinIO ↔ AWS to zmiana jednej zmiennej środowiskowej.
- **Model bazowy** — `Base` (`domain/common/base.py`) daje `id`, `uuid`, `created`, `updated`
  automatycznie każdej encji.
- **Uwierzytelnianie** — token z nagłówka lub ciasteczka, dekorator `@requires_auth()`,
  scope `is_staff`.
- **Obsługa walidacji** — spójny handler `RequestValidationError` zwracający błędy per pole
  (`infrastructure/app.py:44-70`).
- **Sentry** — skonfigurowane z integracjami Starlette / FastAPI / SQLAlchemy / asyncpg.
- **Paginacja** — `PaginationService` jako zależność FastAPI.
- **Health check** — `/health/`, `/healthz/`.
- **Semantic release** — skonfigurowany w `pyproject.toml`.

---

## Błędy krytyczne — blokują MVP

### K1. Całe `/v2/receipts/*` rzuca `TypeError` przy pierwszym requeście

Komendy i zapytania paragonów są w kontenerze DI rejestrowane **bez wymaganych zależności**.

`app/infrastructure/di/containers/commands.py:139-141`:
```python
create_receipt: Provider[CreateReceiptCommand] = providers.Callable(
    CreateReceiptCommand, receipt_repository=repositories.receipt_repository
)
```

`app/application/commands/receipts/create_receipt.py:11`:
```python
def __init__(self, user_repository: IUserRepository, receipt_repository: IReceiptRepository):
```

Brakuje `user_repository` → `TypeError: missing 1 required positional argument`.

**Dotknięte providery:**

| Plik | Linie | Provider | Brakuje |
|---|---|---|---|
| `commands.py` | 124-127 | `create_item` | `user_repository`, `receipt_repository` |
| `commands.py` | 129-132 | `update_item` | `user_repository`, `receipt_repository` |
| `commands.py` | 134-137 | `delete_item` | `user_repository`, `receipt_repository` |
| `commands.py` | 139-141 | `create_receipt` | `user_repository` |
| `commands.py` | 143-145 | `update_receipt` | `user_repository` |
| `commands.py` | 147-149 | `delete_receipt` | `user_repository` |
| `queries.py` | 64-66 | `get_item_list` | `user_repository` |
| `queries.py` | 68-70 | `get_receipt` | `user_repository` |
| `queries.py` | 72-74 | `get_receipt_list` | `user_repository` |

To znaczy, że **wszystkie 9 endpointów** paragonów i pozycji (`presentation/endpoints/receipts.py`)
jest niedziałających. Czyli rdzeń aplikacji.

### K1b. Trzy repozytoria w ogóle nie są zarejestrowane w kontenerze

Warstwa niżej jest jeszcze gorzej. `RepositoryContainer`
(`app/infrastructure/di/containers/repositories.py`) rejestruje **tylko pięć** repozytoriów:

```
user_repository · token_repository · email_token_repository
email_template_repository · company_repository
```

Natomiast te trzy klasy istnieją w kodzie, ale **nie ma ich w kontenerze**:

| Klasa | Plik |
|---|---|
| `SQLAlchemyReceiptRepository` | `infrastructure/repositories/receipt_repository.py:6` |
| `SQLAlchemyItemRepository` | `infrastructure/repositories/item_repository.py:6` |
| `SQLAlchemyTagRepository` | `infrastructure/repositories/tag_repository.py:6` |

Tymczasem `CommandContainer` i `QueryContainer` odwołują się do
`repositories.receipt_repository`, `repositories.item_repository` i `repositories.tag_repository`.
Ponieważ po drugiej stronie jest `providers.DependenciesContainer()`, odwołania te tworzą się
bez błędu przy imporcie, ale **rozsypują się dopiero przy próbie użycia**.

Konsekwencja: oprócz paragonów i pozycji martwe są też **wszystkie endpointy tagów**
(`/v2/tags/*`). Realnie działają tylko: użytkownicy, tokeny, szablony e-mail i firmy.

To wzmacnia wniosek z K1 — nie chodzi o jedną literówkę, tylko o to, że **cała ostatnia partia
pracy (paragony, pozycje, tagi) nigdy nie została uruchomiona**. Zgadza się to z historią
commitów: `CreateReceiptCommand`, `UpdateReceiptCommand`, `DeleteReceiptCommand` i `receipt_tags`
to pięć ostatnich commitów na `master`.

### K2. Usunięcie paragonu zawsze kończy się błędem 404 i wycofaniem zmian

`app/application/commands/receipts/delete_receipt.py:24-27`:
```python
if receipt := await self.receipt_repository.get_by(user_id=user_id, uuid=uuid):
    await self.receipt_repository.delete(receipt)
    await self.receipt_repository.commit()

raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
```

`raise` jest **poza** blokiem `if`, więc wykonuje się również po udanym usunięciu.
Wyjątek propaguje się przez `start_session`, gdzie łapie go `except` i robi `rollback()`
(`base_sqlalchemy_repository.py:39-42`). Efekt: paragon nie zostaje usunięty, użytkownik
dostaje 404. Brakuje `return` po `commit()`.

### K3. Import z wewnętrznego modułu testowego SQLAlchemy

`app/domain/receipt_tags/receipt_tag.py:6`:
```python
from sqlalchemy.testing.schema import mapped_column
```

`sqlalchemy.testing` to prywatny pakiet testowy biblioteki — nie jest częścią publicznego API,
może zniknąć przy aktualizacji i zachowuje się inaczej niż `sqlalchemy.orm.mapped_column`.
Powinno być `from sqlalchemy.orm import mapped_column`.

### K4. Granice transakcji nie działają

`app/application/commands/receipts/create_receipt.py:16-18`:
```python
async with self.user_repository.start_session() as session:
    self.receipt_repository.use_session(session)

user = await self.user_repository.get(user_id)   # ← poza blokiem!
```

`start_session` przy wyjściu z bloku robi `commit()` i `close()`
(`base_sqlalchemy_repository.py:35-45`). Cała praca komendy wykonuje się **po** zamknięciu
sesji. SQLAlchemy otworzy transakcję ponownie, więc wygląda to na działające, ale:

- `try/except/rollback` z `start_session` nie obejmuje żadnej operacji biznesowej,
- **nie ma atomowości** — błąd w połowie komendy zostawia bazę w stanie częściowym.

W pozostałych komendach (`update_receipt.py`, `delete_receipt.py`, `create_item.py`)
wcięcie jest poprawne — problem dotyczy `create_receipt`, ale wzorzec trzeba ujednolicić
i pokryć testem, bo łatwo go powielić.

### K5. Storage rzuci `AttributeError` przy pierwszym użyciu

`app/infrastructure/storage/s3.py:20-31` czyta sześć ustawień:

```python
settings.AWS_REGION_NAME
settings.AWS_ACCESS_KEY
settings.AWS_ACCESS_KEY_SECRET
settings.AWS_ENDPOINT_URL
settings.AWS_S3_BUCKET_NAME
settings.AWS_S3_BUCKET_URL
```

**Żadne z nich nie istnieje** w `app/infrastructure/conf.py`. Klasa `Settings` kończy się
na `PAGINATION_DEFAULT_LIMIT`. Błąd nie ujawnił się tylko dlatego, że
`S3StorageRepository` jest zarejestrowany jako `providers.Callable`
(`di/containers/services.py:17`) i nigdy nie jest wywoływany — patrz K6.

### K6. Obsługa zdjęć nie istnieje jako funkcjonalność

- Nie ma endpointu przyjmującego plik (`UploadFile`) — w `presentation/endpoints/receipts.py`
  wszystkie operacje przyjmują JSON.
- `CreateReceiptSchema` (`domain/receipts/receipt_schemas.py:19-21`) przyjmuje
  `scan_file: str` — czyli **string podany przez klienta**, nie plik.
- `ThumbnailGenerator` (`infrastructure/image_processing/thumbnail_generator.py`) jest
  napisany i **nigdzie nie używany**.
- `storage` z kontenera DI nie jest wstrzykiwany do żadnej komendy.

Czyli funkcja, która jest sensem produktu — „zrób zdjęcie paragonu" — jest w **0%**,
mimo że `plan_dzialnia.txt` opisuje ją jako gotową.

### K7. `Receipt.company_id` jest `NOT NULL`, ale schema go nie przyjmuje

`domain/receipts/receipt.py:21`:
```python
company_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("companies.id"))
```

`Mapped[int]` bez `Optional` → kolumna `NOT NULL`. Tymczasem `CreateReceiptSchema`
zawiera tylko `amount` i `scan_file`, a `CreateReceiptCommand` nie ustawia `company_id`.
Po naprawie K1 pierwszy `POST /v2/receipts/` skończy się `IntegrityError`.

---

## Problemy infrastrukturalne

### I1. `docker-compose.yml` nie wstanie

- **Linia 23:** `DATABASE_URL: "postgresql+asyncpg://coins:password@postgres:5432/coins"` —
  host `postgres`, a serwis nazywa się `db` (linia 3). Brak aliasu sieciowego → nazwa się nie rozwiąże.
- **Linie 5-7 vs `share/init.sql`:** kontener startuje z `postgres/postgres/postgres`,
  a `init.sql` tworzy rolę `coins` i bazę `coins`. Konfiguracja jest rozjechana z URL-em.
- **Linia 48:** `external: true` — sieć trzeba stworzyć ręcznie (`docker network create coins-network`),
  inaczej `docker compose up` kończy się błędem.
- **Brak MinIO** — mimo że `plan_dzialnia.txt` twierdzi inaczej.
- **Brak Redis** — jw.
- `version: "3.9"` jest przestarzałe w nowym Docker Compose (ostrzeżenie).

### I2. CI nigdy nie uruchomiło testów

`.github/workflows/default.yml`:
```yaml
run: |
  poetry run black --check .
  poetry run flake8 .
  poetry run isort --check-only .
  poetry run python manage.py test     # ← komenda Django, nie istnieje w tym repo
```

Do tego `DATABASE_URL: "sqlite://test.db"` przy stacku opartym o `asyncpg` i migracje
PostgreSQL-owe. Job testowy nie mógł nigdy przejść.

### I3. Brak `.env` i `.env.example`

`conf.py:48` ładuje `.env` z katalogu głównego. Pliku nie ma, nie ma też szablonu.
Nowa osoba (albo Ty za dwa miesiące) nie wie, co ustawić.

### I4. Publiczny endpoint celowo rzucający wyjątek

`infrastructure/router.py:25-28`:
```python
@router.get("/sentry-debug/")
async def trigger_error():
    division_by_zero = 1 / 0
```

Bez autoryzacji. Każdy może generować błędy 500 i zaśmiecać Sentry.

### I5. `TrustedHostMiddleware` zablokuje wywołania wewnątrz Dockera

`infrastructure/app.py:26` dopuszcza tylko `coin-master.devsoft.pl` i `localhost`.
Żądania kierowane na `api` (nazwa serwisu) lub adres IP kontenera dostaną 400.

---

## Braki w modelu danych (względem MVP)

| Encja | Jest | Brakuje do MVP |
|---|---|---|
| `Receipt` | `amount`, `scan_file`, `company_id`, `user_id` | `purchase_date`, `notes`; `scan_file` musi być nullable (D5); `company_id` musi być nullable |
| `Item` | `name`, `price`, `receipt_id` | `quantity`, `unit`, `unit_price`, `category_id`, `normalized_name` (D6) |
| `Company` | `name`, `address`, `user_id` | `city`, `store_type` (opcjonalnie) |
| `Category` | — | **cała encja** + kategorie domyślne |
| `Tag` | `name`, `user_id` | ✅ gotowe |
| `ReceiptTag` | `tag_id`, `receipt_id` | ✅ gotowe (migracja `2024_12_04_2119`) |
| `User` | `email`, `password`, `is_staff` | ✅ wystarcza na MVP |

**Uwaga:** `plan_dzialnia.txt` wymienia brak `created_at` / `updated_at` — to nieaktualne.
`Base` (`domain/common/base.py:35-36`) daje `created` i `updated` każdej encji.

---

## Testy — stan zerowy

```
tests/
├── __init__.py
├── conftest.py          ← 0 bajtów
├── factories/__init__.py ← pusty
├── integration/__init__.py
└── units/
    ├── __init__.py
    └── test_main.http   ← plik PyCharma, nie test
```

**Zero testów przy ~4000 linii kodu.** To bezpośrednia przyczyna tego, że błędy K1 i K2
przeszły niezauważone — jeden test integracyjny `POST /v2/receipts/` wykryłby oba.

Dodatkowo w `pyproject.toml:68` próg pokrycia jest zakomentowany:
```toml
# --cov=app/ --cov-report=term-missing ... --cov-fail-under=100 --durations=10
addopts = "--no-header -v --new-first --showlocals"
```

Szczegółowy plan dojścia do 100% → [05_TESTY.md](05_TESTY.md).

---

## Drobiazgi do decyzji

- **Ruff jest już zainstalowany** (`pyproject.toml:52`), ale bez sekcji `[tool.ruff]` i nieużywany.
  Trzeba go albo skonfigurować, albo usunąć — obecnie to martwa zależność.
- **`PaginatedSchema`** (`services/pagination.py:23-27`) nie zwraca `total` ani `pages`.
  Front nie zbuduje z tego poprawnego paginatora — do rozszerzenia w MVP.
- **`Receipt.amount` vs suma `Item.price`** — dwa źródła prawdy bez pilnowania spójności.
  Decyzja w [03_MVP_BACKEND.md](03_MVP_BACKEND.md).
- **`locust`** w zależnościach deweloperskich bez żadnego scenariusza — martwa zależność.
- **`redis`** w zależnościach produkcyjnych (`pyproject.toml:18`) bez użycia w kodzie
  i bez serwisu w Dockerze.
- **`psycopg` i `psycopg2-binary`** obok `asyncpg` — prawdopodobnie tylko dla Alembica,
  warto potwierdzić i ewentualnie ograniczyć.

---

## Sprostowania do `plan_dzialnia.txt`

| Twierdzenie w planie | Stan faktyczny |
|---|---|
| „Docker setup (PostgreSQL, **Redis, MinIO**)" | Tylko `db`, `api`, `nginx`. Redis i MinIO nie istnieją |
| „S3-compatible storage (Boto3/MinIO)" | Kod jest, ale rzuca `AttributeError` (K5) i nikt go nie woła (K6) |
| „PyTest + Factory Boy (testing setup)" | 0 testów, pusty `conftest.py`, puste `factories/` |
| „Pre-commit hooks, testing setup" | `pre-commit` jest w zależnościach; job testowy w CI jest zepsuty (I2) |
| „Receipt — brakuje `created_at`, `updated_at`" | Nieaktualne — są w `Base` jako `created` / `updated` |
| „Nowe entities potrzebne: **Tag**" | Już zaimplementowane wraz z `ReceiptTag` i migracją |
| „Redis (caching, message broker)" | Zależność zainstalowana, ale zero użycia w kodzie |

---

## Wnioski dla planu prac

1. **Nie da się zacząć MVP od nowych funkcji** — rdzeń API nie działa (K1, K1b).
   Działające endpointy to obecnie tylko użytkownicy, tokeny, szablony e-mail i firmy.
2. **Testy nie są etapem „na koniec"** — ich brak jest przyczyną obecnego stanu.
   Muszą powstać razem z naprawami, jako siatka bezpieczeństwa.
3. **Architektura jest dobra** — nie przepisujemy, naprawiamy i uzupełniamy.
4. **Obsługa zdjęć to realna praca**, nie „podpięcie gotowego" — trzeba napisać endpoint,
   miniatury, presigned URL-e i konfigurację (K5, K6).

→ Konkretna lista napraw w kolejności: [02_NAPRAWY_PRZED_MVP.md](02_NAPRAWY_PRZED_MVP.md)
