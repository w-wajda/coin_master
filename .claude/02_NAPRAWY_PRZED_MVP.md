# 02 — Faza 0: naprawy przed MVP

Cel fazy: **doprowadzić repozytorium do stanu, w którym da się bezpiecznie dobudowywać funkcje.**
Żadnych nowych funkcjonalności — tylko naprawa tego, co jest zepsute, plus siatka bezpieczeństwa
w postaci testów.

Szacunek: **4-6 dni roboczych.** Kolejność ma znaczenie — każdy krok opiera się na poprzednim.

---

## Dlaczego akurat w tej kolejności

Naturalny odruch to „naprawmy najpierw ten `TypeError` w DI". Ale wtedy naprawiamy
na ślepo — nie ma jak sprawdzić, czy naprawa zadziałała. Dlatego:

1. **najpierw środowisko wstaje** (bez tego nie uruchomisz nawet jednego testu),
2. **potem fundament testów** (`conftest`, fabryki),
3. **potem testy, które udowadniają istnienie błędów** (czerwone),
4. **potem naprawy** (testy robią się zielone),
5. **na końcu CI**, żeby to się już nie zepsuło.

To jest klasyczne podejście „regression test first" — przy 4000 linii nieprzetestowanego
kodu jedyne, które nie kończy się zgadywaniem.

---

## Krok 1 — Środowisko wstaje (0.5 dnia)

### 1.1 Ustawienia AWS/S3 w konfiguracji

**Plik:** `app/infrastructure/conf.py`

Dodaj do klasy `Settings` (po `PAGINATION_DEFAULT_LIMIT`):

```python
# Storage (S3-compatible: MinIO lokalnie, AWS S3 na produkcji)
AWS_REGION_NAME: str = "us-east-1"
AWS_ACCESS_KEY: str = ""
AWS_ACCESS_KEY_SECRET: str = ""
AWS_S3_BUCKET_NAME: str = "coin-master"
AWS_S3_BUCKET_URL: str = ""
AWS_ENDPOINT_URL: str = ""          # puste = AWS; "http://minio:9000" = MinIO

# Czasy życia linków (sekundy)
SCAN_URL_EXPIRES_IN: int = 900      # 15 min — podgląd w aplikacji
SHARE_URL_EXPIRES_IN: int = 604800  # 7 dni — maksimum AWS SigV4
```

> **Uwaga:** `SHARE_URL_EXPIRES_IN` nie może przekroczyć `604800`. AWS odrzuca podpisy
> SigV4 z dłuższym czasem życia. Warto dodać walidator, który to pilnuje.

### 1.2 Plik `.env.example`

**Nowy plik:** `.env.example` (commitowany) — `.env` zostaje w `.gitignore`.

```dotenv
# Aplikacja
PORT=8000
HOST=0.0.0.0
DEBUG=true
RUN_ENV=dev

# Baza danych
DATABASE_URL=postgresql+asyncpg://coins:password@db:5432/coins
DB_DEBUG=false

# Storage — MinIO lokalnie
AWS_ENDPOINT_URL=http://minio:9000
AWS_ACCESS_KEY=minioadmin
AWS_ACCESS_KEY_SECRET=minioadmin
AWS_S3_BUCKET_NAME=coin-master
AWS_REGION_NAME=us-east-1
AWS_S3_BUCKET_URL=

# E-mail
EMAIL_URL=smtp+tls://login:password@smtp_server:25
EMAIL_FROM=info@coin-master.devsoft.pl
EMAIL_FROM_NAME=Coin Master
```

### 1.3 Naprawa `docker-compose.yml` + MinIO

Zmiany:
- `DATABASE_URL` → host `db` zamiast `postgres` (linia 23),
- dane logowania Postgresa spójne z `share/init.sql`,
- sieć bez `external: true` (żeby `docker compose up` działało od razu),
- usunięcie `version: "3.9"`,
- **dodanie MinIO** (decyzja D2),
- `depends_on` dla `api`.

```yaml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - ./share/init.sql:/docker-entrypoint-initdb.d/init.sql
      - .datastore/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
    networks: [coins-network]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"   # API S3
      - "9001:9001"   # panel WWW
    volumes:
      - .datastore/minio:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 5s
      retries: 10
    networks: [coins-network]

  # jednorazowo tworzy bucket i ustawia go jako PRYWATNY (decyzja D3)
  minio-init:
    image: minio/mc:latest
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin minioadmin &&
      mc mb --ignore-existing local/coin-master &&
      mc anonymous set none local/coin-master
      "
    networks: [coins-network]

  api:
    build:
      context: .
      dockerfile: deployment/Dockerfile
    command: dev
    env_file: .env
    environment:
      DATABASE_URL: "postgresql+asyncpg://coins:password@db:5432/coins"
      AWS_ENDPOINT_URL: "http://minio:9000"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      minio:
        condition: service_healthy
    volumes:
      - .:/app
    networks: [coins-network]

networks:
  coins-network:
    name: coins-network
```

Panel MinIO: **http://localhost:9001** (`minioadmin` / `minioadmin`) — widać w nim wgrane pliki,
co bardzo ułatwia debugowanie uploadu.

### 1.4 `TrustedHostMiddleware`

**Plik:** `app/infrastructure/app.py:26`

Lista hostów do przeniesienia do konfiguracji, z `"api"` i `"127.0.0.1"` dopisanymi
dla środowiska deweloperskiego. Inaczej wywołania wewnątrz Dockera dostaną 400.

### 1.5 Endpoint `/sentry-debug/`

**Plik:** `app/infrastructure/router.py:25-28`

Do usunięcia albo do schowania za `if settings.DEBUG:`. Publicznie dostępny generator
błędów 500 nie powinien trafić na produkcję.

**Weryfikacja kroku 1:**
```bash
docker compose up -d
curl http://localhost:8000/health/     # → {"status":"ok"}
open http://localhost:9001             # panel MinIO, bucket coin-master widoczny
```

---

## Krok 2 — Fundament testów (1 dzień)

Bez tego kroku dalsze naprawy są zgadywaniem. Pełny opis w [05_TESTY.md](05_TESTY.md),
tutaj minimum niezbędne do ruszenia dalej.

### 2.1 `tests/conftest.py`

Obecnie plik ma 0 bajtów. Musi dostarczyć:

- `event_loop` / konfigurację `pytest-asyncio` (tryb `auto` jest już ustawiony),
- silnik i sesję do testowej bazy PostgreSQL,
- czyszczenie danych między testami (transakcja z rollbackiem),
- `app` z **podmienionym kontenerem DI**,
- `client` (`httpx.AsyncClient`) z `ASGITransport`,
- nadpisanie storage'u na `FakeS3StorageRepository`,
- fixture `authenticated_client` z gotowym tokenem.

Kluczowe: `initialize_app()` przyjmuje `di_container` (`infrastructure/app.py:22`) —
podmiana zależności w testach jest więc możliwa bez hacków.

### 2.2 Fabryki

**Katalog:** `tests/factories/` — `factory-boy` jest już w zależnościach.

Potrzebne: `UserFactory`, `TokenFactory`, `CompanyFactory`, `ReceiptFactory`, `ItemFactory`,
`TagFactory`.

### 2.3 Pierwsze testy — mają być CZERWONE

Zanim cokolwiek naprawisz, napisz testy opisujące **oczekiwane** zachowanie:

```python
# tests/integration/test_receipts.py
async def test_create_receipt(authenticated_client, company):
    response = await authenticated_client.post("/v2/receipts/", json={...})
    assert response.status_code == 201          # ← teraz: TypeError (K1)

async def test_delete_receipt(authenticated_client, receipt):
    response = await authenticated_client.delete(f"/v2/receipts/{receipt.uuid}/")
    assert response.status_code == 204          # ← teraz: 404 (K2)
```

Te dwa testy są dowodem, że błędy K1 i K2 istnieją — i za chwilę dowodem, że zniknęły.

---

## Krok 3 — Naprawa błędów krytycznych (1-1.5 dnia)

### 3.0 Rejestracja brakujących repozytoriów  *(błąd K1b)*

**Musi być pierwsze** — bez tego naprawa 3.1 nie ma się do czego podpiąć.

**Plik:** `app/infrastructure/di/containers/repositories.py`

Dopisz trzy brakujące providery (klasy już istnieją, nikt ich nie zarejestrował):

```python
from app.infrastructure.repositories.item_repository import SQLAlchemyItemRepository
from app.infrastructure.repositories.receipt_repository import SQLAlchemyReceiptRepository
from app.infrastructure.repositories.tag_repository import SQLAlchemyTagRepository

    receipt_repository: Provider[SQLAlchemyReceiptRepository] = providers.Callable(
        SQLAlchemyReceiptRepository,
        session=session,
    )

    item_repository: Provider[SQLAlchemyItemRepository] = providers.Callable(
        SQLAlchemyItemRepository,
        session=session,
    )

    tag_repository: Provider[SQLAlchemyTagRepository] = providers.Callable(
        SQLAlchemyTagRepository,
        session=session,
    )
```

Naprawia to również martwe endpointy tagów (`/v2/tags/*`).

### 3.1 Okablowanie DI  *(błąd K1)*

**Plik:** `app/infrastructure/di/containers/commands.py`

```python
create_receipt: Provider[CreateReceiptCommand] = providers.Callable(
    CreateReceiptCommand,
    user_repository=repositories.user_repository,        # ← dodane
    receipt_repository=repositories.receipt_repository,
)
```

Analogicznie dla `update_receipt` (143-145) i `delete_receipt` (147-149).

Dla pozycji (124-137) trzeba dodać **dwie** zależności:
```python
create_item: Provider[CreateItemCommand] = providers.Callable(
    CreateItemCommand,
    user_repository=repositories.user_repository,        # ← dodane
    item_repository=repositories.item_repository,
    receipt_repository=repositories.receipt_repository,  # ← dodane
)
```

**Plik:** `app/infrastructure/di/containers/queries.py` — to samo dla `get_item_list` (64-66),
`get_receipt` (68-70), `get_receipt_list` (72-74).

> **Zabezpieczenie na przyszłość:** dopisz test, który przechodzi po wszystkich providerach
> kontenera i próbuje je zainicjalizować. Wyłapie każde przyszłe rozjechanie sygnatury
> z okablowaniem — patrz [05_TESTY.md](05_TESTY.md).

### 3.2 Usuwanie paragonu  *(błąd K2)*

**Plik:** `app/application/commands/receipts/delete_receipt.py:24-27`

```python
if receipt := await self.receipt_repository.get_by(user_id=user_id, uuid=uuid):
    await self.receipt_repository.delete(receipt)
    await self.receipt_repository.commit()
    return                                      # ← brakujące

raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
```

Sprawdź ten sam wzorzec w `delete_item.py`, `delete_tag.py`, `delete_company.py`.

### 3.3 Import z `sqlalchemy.testing`  *(błąd K3)*

**Plik:** `app/domain/receipt_tags/receipt_tag.py:6`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

### 3.4 Granice transakcji  *(błąd K4)*

**Plik:** `app/application/commands/receipts/create_receipt.py:16-27`

Cała logika musi znaleźć się **wewnątrz** bloku `async with`:

```python
async def __call__(self, user_id: int, receipt_data: CreateReceiptSchema) -> Receipt:
    async with self.user_repository.start_session() as session:
        self.receipt_repository.use_session(session)

        user = await self.user_repository.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        receipt = Receipt(**receipt_data.model_dump())
        receipt.user_id = user_id
        self.receipt_repository.add(receipt)
        await self.receipt_repository.commit()
        return receipt
```

Następnie **przejrzyj wszystkie 23 komendy i 12 zapytań** pod kątem tego samego wcięcia.
Warto dopisać test sprawdzający, że błąd w połowie komendy nie zostawia zapisu w bazie.

### 3.5 `company_id` na paragonie  *(błąd K7)*

**Plik:** `app/domain/receipts/receipt.py:21`

```python
company_id: Mapped[int | None] = mapped_column(sa.Integer, sa.ForeignKey("companies.id"), nullable=True)
```

Uzasadnienie: nie zawsze wiadomo, w którym sklepie był zakup (paragon wyblakł, zakup online).
Wymaganie sklepu blokowałoby dodanie paragonu. Migracja Alembica.

**Weryfikacja kroku 3:** testy z punktu 2.3 przechodzą na zielono.

---

## Krok 4 — Pokrycie istniejącego kodu testami (1.5-2 dni)

Zanim dołożymy nowe funkcje, to co już jest musi być przetestowane — inaczej za miesiąc
znajdziemy kolejne K1.

Kolejność (od największego ryzyka):

| # | Obszar | Dlaczego priorytet |
|---|---|---|
| 1 | Test inicjalizacji wszystkich providerów DI | Wyłapuje całą klasę błędów typu K1 |
| 2 | Komendy i zapytania paragonów + pozycji | Rdzeń produktu, najświeższy kod |
| 3 | Uwierzytelnianie (`auth.py`, `requires_auth`) | Brama do wszystkiego |
| 4 | `GenericSQLAlchemyRepository` | Używane przez każdą komendę |
| 5 | Firmy, tagi | Prostsze, ale wchodzą do MVP |
| 6 | Użytkownicy, tokeny, reset hasła | Działa, ale nieudowodnione |
| 7 | Szablony e-mail, wysyłka | Potrzebne pod D4 |

Cel na koniec Fazy 0: **pokrycie ≥ 90%**, próg 100% włączamy razem z zamknięciem MVP
(uzasadnienie w [05_TESTY.md](05_TESTY.md)).

---

## Krok 5 — CI (0.5 dnia)

**Plik:** `.github/workflows/default.yml`

Do naprawy:
- `poetry run python manage.py test` → `poetry run pytest --cov=app --cov-report=term-missing`,
- usunięcie `DATABASE_URL: "sqlite://test.db"`,
- dodanie serwisu PostgreSQL (`services: postgres:`) z healthcheckiem,
- dodanie MinIO jako serwisu **albo** oparcie testów o `FakeS3StorageRepository`
  (rekomendacja: testy jednostkowe na `FakeS3`, jeden zestaw integracyjnych na MinIO),
- `mypy` na razie **poza** blokiem blokującym (`continue-on-error: true`) — obecny kod go nie przejdzie.

Kryterium: **PR nie może się zmergować przy czerwonych testach.**

---

## Krok 6 — Migracja Poetry → UV (0.5 dnia, opcjonalnie)

Świadomie **na końcu** Fazy 0, nie na początku: najpierw chcemy mieć działający,
przetestowany punkt odniesienia. Zmiana menedżera pakietów przy czerwonych testach
oznacza, że nie wiadomo, co właściwie się zepsuło.

Zakres:
1. `uv init` / przepisanie `[tool.poetry]` na `[project]` (PEP 621),
2. `uv lock` → `uv.lock`, usunięcie `poetry.lock`,
3. aktualizacja `deployment/Dockerfile`,
4. aktualizacja obu workflowów w `.github/`,
5. aktualizacja `Makefile`.

Sekcje `[tool.pytest.ini_options]`, `[tool.black]`, `[tool.isort]`, `[tool.coverage]`,
`[tool.mypy]` i `[tool.semantic_release]` zostają bez zmian.

> Jeśli terminowo robi się ciasno — ten krok można przenieść za MVP bez żadnej szkody.
> Poetry działa poprawnie, to optymalizacja wygody, nie naprawa.

---

## Sprzątanie przy okazji

Drobiazgi do zrobienia gdzieś w trakcie Fazy 0:

- [x] `PaginatedSchema` — dodać `total` i `pages` (`services/pagination.py:23-27`);
      bez tego front nie zbuduje paginatora
- [x] `locust` — usunąć z zależności albo dopisać pierwszy scenariusz
- [x] `redis` — usunąć z zależności produkcyjnych do czasu realnego użycia
      (wraca w [04_ZAAWANSOWANE.md](04_ZAAWANSOWANE.md))
- [x] `ruff` — skonfigurować albo usunąć; decyzja odłożona do fazy zaawansowanej
- [x] `README.md` jest pusty — minimalna instrukcja uruchomienia
- [x] Sprawdzić, czy `psycopg` i `psycopg2-binary` są potrzebne obok `asyncpg`

---

## Definicja ukończenia Fazy 0

- [ ] `docker compose up` podnosi całość jedną komendą, `/health/` odpowiada
- [ ] Panel MinIO działa, bucket `coin-master` istnieje i jest **prywatny**
- [ ] Wszystkie repozytoria są zarejestrowane w kontenerze (K1b zamknięty)
- [ ] Wszystkie endpointy `/v2/receipts/*` i `/v2/tags/*` odpowiadają poprawnie (K1 zamknięty)
- [ ] `DELETE /v2/receipts/{uuid}/` zwraca 204 i realnie usuwa (K2 zamknięty)
- [ ] Brak importów z `sqlalchemy.testing` (K3 zamknięty)
- [ ] Każda komenda wykonuje się w jednej transakcji (K4 zamknięty)
- [ ] `Settings` zawiera konfigurację storage'u, `.env.example` w repo (K5 zamknięty)
- [ ] Pokrycie testami ≥ 90%, testy przechodzą lokalnie i w CI
- [ ] CI blokuje merge przy czerwonych testach

**Dopiero po odhaczeniu wszystkiego** → [03_MVP_BACKEND.md](03_MVP_BACKEND.md)
