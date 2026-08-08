# 05 — Strategia testów

**Cel:** 100% pokrycia kodu, mierzone przez `pytest-cov`, wymuszone w CI.
**Punkt startowy:** 0 testów przy ~4000 linii kodu.

---

## Dlaczego to jest najważniejszy dokument z całego zestawu

Błędy K1, K1b i K2 opisane w [01_STAN_OBECNY.md](01_STAN_OBECNY.md) nie są przypadkiem.
Rdzeń aplikacji — paragony, pozycje, tagi — **nigdy nie został uruchomiony**, mimo że kod
został napisany i scommitowany. Jeden test integracyjny wykrywa wszystkie trzy błędy naraz:

```python
async def test_create_receipt(authenticated_client):
    response = await authenticated_client.post("/v2/receipts/", json={...})
    assert response.status_code == 201
```

To dokładnie ta sytuacja, przed którą chronią testy. Dlatego w planie prac są one **przed**
nowymi funkcjami, a nie po nich.

---

## Uczciwa uwaga o „100%"

100% pokrycia oznacza, że każda linia została **wykonana** — nie że została **sprawdzona**.
Można mieć 100% i zero wartości, jeśli testy nie mają sensownych asercji.

Traktuj ten próg jako:
- ✅ **dobrą dyscyplinę** — wymusza świadome decyzje przy każdym `if` i `except`
- ✅ **siatkę bezpieczeństwa** przy refaktorze
- ❌ **nie** jako dowód poprawności

Realna weryfikacja jakości testów to testy mutacyjne (`mutmut`) — w
[04_ZAAWANSOWANE.md](04_ZAAWANSOWANE.md), nie teraz.

---

## Baza danych w testach: PostgreSQL, nie SQLite

W zależnościach jest `aiosqlite` (`pyproject.toml:36`), a stary workflow CI ustawiał
`DATABASE_URL: "sqlite://test.db"`. **To była zła droga** i nie należy do niej wracać.

| Powód | Szczegół |
|---|---|
| Sterownik | Produkcja używa `asyncpg` — inny dialekt, inne zachowanie przy typach |
| Migracje | Pisane pod PostgreSQL, jest `alembic-postgresql-enum` |
| Analityka | MVP używa `date_trunc` i window functions — SQLite ich nie ma |
| Typy | `sa.UUID`, `sa.Numeric`, `sa.DateTime(timezone=True)` zachowują się inaczej |
| Więzy | SQLite domyślnie nie egzekwuje kluczy obcych — testy przechodzą, produkcja pada |

Testowanie na SQLite dałoby **fałszywe poczucie bezpieczeństwa** — dokładnie to, czego chcemy
uniknąć. `aiosqlite` do usunięcia z zależności.

Baza testowa: `coins_test` na tej samej instancji PostgreSQL co deweloperska
(w CI — serwis `postgres` w workflow).

---

## Struktura katalogów

```
tests/
├── conftest.py               # fixtures współdzielone
├── factories/
│   ├── user.py               # UserFactory, TokenFactory
│   ├── company.py
│   ├── receipt.py            # ReceiptFactory, ItemFactory
│   ├── category.py
│   └── tag.py
├── units/                    # bez bazy i bez HTTP — szybkie
│   ├── domain/
│   │   ├── test_normalization.py     # normalize_product_name (D6)
│   │   ├── test_validators.py
│   │   └── test_base_model.py
│   ├── application/
│   │   ├── commands/         # komendy z podstawionymi repozytoriami
│   │   └── queries/
│   ├── infrastructure/
│   │   ├── test_storage_fake.py
│   │   ├── test_thumbnail_generator.py
│   │   └── test_pagination.py
│   └── test_di_container.py  # ← strażnik przed K1/K1b
└── integration/              # z bazą i przez HTTP
    ├── test_auth.py
    ├── test_receipts.py
    ├── test_receipt_scan.py  # upload, presigned, share
    ├── test_items.py
    ├── test_categories.py
    ├── test_companies.py
    ├── test_tags.py
    ├── test_analytics.py
    ├── test_products.py      # historia cen
    ├── test_users.py
    └── test_storage_minio.py # jedyny zestaw uderzający w prawdziwe S3
```

Katalog `tests/units/` istnieje już dziś (jest w nim tylko plik `test_main.http` od PyCharma —
do usunięcia albo przeniesienia poza `tests/`).

---

## `conftest.py`

Obecnie plik ma 0 bajtów. Poniżej szkielet dopasowany do **rzeczywistej** struktury DI
w tym projekcie (`AppContainer` z `app/infrastructure/di/app_container.py`).

```python
import pytest
from dependency_injector import providers
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.common.base import Base
from app.infrastructure.app import initialize_app
from app.infrastructure.di.app_container import init_di
from app.infrastructure.storage.fake_s3 import FakeS3StorageRepository

# WAŻNE: wszystkie modele muszą być zaimportowane, żeby Base.metadata je znała
import app.domain.companies.company      # noqa
import app.domain.items.item             # noqa
import app.domain.receipts.receipt       # noqa
import app.domain.receipt_tags.receipt_tag  # noqa
import app.domain.tags.tag               # noqa
import app.domain.users.user             # noqa


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/coins_test"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=None)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session_maker(engine):
    """Czyści dane po każdym teście — repozytoria commitują same, więc
    zagnieżdżona transakcja z rollbackiem tu nie zadziała."""
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    yield maker
    async with engine.begin() as conn:
        tables = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
        await conn.exec_driver_sql(f"TRUNCATE {tables} RESTART IDENTITY CASCADE")


@pytest.fixture
def storage():
    return FakeS3StorageRepository(path="/")


@pytest.fixture
def container(session_maker, storage):
    c = init_di()
    # AppContainer.session = providers.Factory(get_async_session), które zwraca sessionmaker
    c.session.override(providers.Object(session_maker))
    c.services.storage.override(providers.Object(storage))
    yield c
    c.unwire()


@pytest.fixture
async def client(container):
    app = initialize_app(di_container=container)      # app.py:22 przyjmuje kontener
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client(client, user, token):
    client.headers["Authorization"] = f"Bearer {token.key}"
    return client
```

**Trzy rzeczy, na które trzeba uważać:**

1. **`TRUNCATE`, nie rollback.** Standardowa sztuczka z zagnieżdżoną transakcją i rollbackiem
   nie zadziała, bo `GenericSQLAlchemyRepository.start_session` sam robi `commit()` i `close()`
   (`base_sqlalchemy_repository.py:35-45`). `TRUNCATE ... CASCADE` jest wolniejszy,
   ale przewidywalny.
2. **Import modeli.** `Base.metadata` jest pusta, dopóki moduły z encjami nie zostaną
   zaimportowane. Bez tego `create_all` stworzy zero tabel, a testy padną w niejasny sposób.
3. **`TrustedHostMiddleware`.** `app.py:26` dopuszcza tylko `coin-master.devsoft.pl`
   i `localhost` — `base_url` w kliencie testowym musi się z tym zgadzać
   albo lista hostów musi trafić do konfiguracji (patrz [02, krok 1.4](02_NAPRAWY_PRZED_MVP.md)).

---

## Strażnik kontenera DI — test, który zapobiega powtórce K1

To najważniejszy pojedynczy test w całym projekcie. Wyłapuje **całą klasę błędów**:
rozjechanie sygnatury komendy z jej okablowaniem oraz brakujące repozytoria.

```python
# tests/units/test_di_container.py
import pytest
from dependency_injector import providers

from app.infrastructure.di.app_container import AppContainer


def _named_providers(container):
    return [
        (name, p) for name, p in container.providers.items()
        if not isinstance(p, (providers.DependenciesContainer, providers.Dependency))
    ]


@pytest.mark.parametrize("kind", ["commands", "queries", "repositories", "services"])
def test_every_provider_can_be_constructed(container, kind):
    """Każdy provider musi dać się zbudować bez TypeError.

    Ten test wykrywa: brakujące zależności w providers.Callable (K1)
    oraz repozytoria nieobecne w kontenerze (K1b).
    """
    sub = getattr(container, kind)()
    for name, provider in _named_providers(sub):
        try:
            provider()
        except TypeError as exc:
            pytest.fail(f"Provider '{kind}.{name}' nie da się zbudować: {exc}")
```

Dodatkowo warto sprawdzić, że **każda trasa zarejestrowana w routerze da się wywołać**
(choćby z 401) — to wykrywa endpointy odwołujące się do nieistniejących providerów:

```python
async def test_every_route_responds(client):
    for route in client._transport.app.routes:
        ...  # wywołanie i asercja, że to NIE jest 500
```

---

## Fabryki

`factory-boy` jest już w zależnościach (`pyproject.toml:40`), katalog `tests/factories/`
istnieje i jest pusty.

```python
class ReceiptFactory(factory.Factory):
    class Meta:
        model = Receipt

    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    purchase_date = factory.Faker("date_between", start_date="-1y", end_date="today")
    scan_file = None                       # zdjęcie opcjonalne (D5)
    company = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)
```

Zasady:
- fabryki tworzą **obiekty**, zapis do bazy jest jawny w teście — mniej magii przy sesjach async
- `purchase_date` zawsze z przeszłości (walidacja z MVP tego wymaga)
- osobna fabryka `ReceiptWithScanFactory` dla przypadków ze zdjęciem

---

## Storage w testach — dwa poziomy

| Poziom | Implementacja | Zakres |
|---|---|---|
| Jednostkowe i większość integracyjnych | `FakeS3StorageRepository` | Szybkie, bez sieci, bez Dockera |
| `tests/integration/test_storage_minio.py` | Prawdziwe MinIO | Podpisy, wygasanie, prywatność bucketa |

Drugi poziom jest niezbędny, bo **`FakeS3` nie potrafi zasymulować podpisu ani wygaśnięcia**.
A to są dokładnie te rzeczy, na których zależy nam najbardziej (decyzja D3):

```python
async def test_presigned_url_expires(minio_storage):
    url = minio_storage.get_presigned_url("test.jpg", expires_in=2)
    assert httpx.get(url).status_code == 200
    await asyncio.sleep(3)
    assert httpx.get(url).status_code == 403        # link wygasł

async def test_bucket_is_private(minio_storage):
    """Bez podpisu nie ma dostępu — fundament decyzji D3."""
    plain_url = f"{settings.AWS_ENDPOINT_URL}/{settings.AWS_S3_BUCKET_NAME}/test.jpg"
    assert httpx.get(plain_url).status_code == 403
```

Te dwa testy to jedyny twardy dowód, że prywatność zdjęć faktycznie działa.
`FakeS3StorageRepository` musi dostać metody `get_presigned_url` i `delete`, żeby
nie rozjechał się z interfejsem — **dopisz test sprawdzający, że obie implementacje
mają identyczny zestaw metod publicznych.**

---

## Co musi być pokryte, żeby MVP było wiarygodne

Poza samym procentem, ta lista jest obowiązkowa:

| Obszar | Test |
|---|---|
| **Izolacja użytkowników** | Dla **każdego** endpointu: użytkownik A nie widzi i nie zmienia zasobów użytkownika B (404, nie 403 — nie zdradzamy istnienia zasobu) |
| **Presigned URL** | Działa, wygasa, nie działa bez podpisu |
| **Prywatność bucketa** | Bezpośredni URL zwraca 403 |
| **Upload** | Za duży plik, zły format, plik udający obraz, uszkodzony obraz |
| **Transakcje** | Błąd w połowie komendy → brak zapisu w bazie (regresja K4) |
| **Usuwanie** | `DELETE` zwraca 204 i naprawdę usuwa (regresja K2) |
| **Kaskady** | Usunięcie paragonu usuwa pozycje i pliki z bucketa |
| **Normalizacja** | Warianty zapisu tej samej nazwy trafiają do jednej grupy (D6) |
| **Analityka** | Wyniki zgodne z ręcznym wyliczeniem na znanym zestawie danych |
| **Paginacja** | Granice: strona 0, poza zakresem, `limit` ponad maksimum |
| **Migracje** | `upgrade head` i `downgrade` na czystej bazie |

---

## Konfiguracja pokrycia

Przywróć zakomentowaną linię w `pyproject.toml:68`:

```toml
addopts = """
    --no-header -v --new-first --showlocals
    --cov=app/ --cov-report=term-missing --cov-report=html
    --cov-fail-under=100 --durations=10
"""
```

**Kiedy włączyć próg 100%:**

| Etap | Próg |
|---|---|
| Faza 0, krok 2-3 | bez progu — piszemy testy, które mają być czerwone |
| Koniec Fazy 0 | `--cov-fail-under=90` |
| Koniec MVP | `--cov-fail-under=100` |

Włączenie 100% od pierwszego dnia zablokowałoby pracę zanim cokolwiek powstanie.

### Zasady dla `pragma: no cover`

Wyłączenia są już skonfigurowane (`pyproject.toml:86-94`): `__repr__`, `__str__`,
`TYPE_CHECKING`, `raise NotImplementedError`, `@abstractmethod`. To rozsądny zestaw.

Reguła na przyszłość: **`# pragma: no cover` wymaga komentarza z uzasadnieniem.**
Bez tego stanie się wygodnym sposobem na chowanie nieprzetestowanego kodu i cała
dyscyplina 100% straci sens.

---

## Kolejność pisania testów

### Faza 0 (patrz [02_NAPRAWY_PRZED_MVP.md](02_NAPRAWY_PRZED_MVP.md))

1. `conftest.py` + fabryki
2. `test_di_container.py` ← natychmiast wykrywa K1 i K1b
3. `test_receipts.py` — czerwone, potem zielone po naprawach
4. `test_auth.py` — brama do wszystkiego
5. Repozytorium generyczne
6. Reszta istniejących komend i zapytań

**Cel: 90%**

### MVP (patrz [03_MVP_BACKEND.md](03_MVP_BACKEND.md))

Każdy etap ma testy pisane **razem z kodem**, nie po. Na koniec zostaje tylko
domknięcie brakujących gałęzi i włączenie progu 100%.

---

## CI

```yaml
services:
  postgres:
    image: postgis/postgis:16-3.4
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: coins_test
    options: >-
      --health-cmd pg_isready --health-interval 5s --health-retries 10
    ports: ["5432:5432"]

  minio:
    image: minio/minio:latest
    env:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000"]
```

Kroki: `black --check` → `isort --check-only` → `flake8` → `pytest` → raport pokrycia.
`mypy` na razie z `continue-on-error: true` — obecny kod go nie przejdzie, a nie chcemy
blokować pracy na starcie.

**Merge musi być zablokowany przy czerwonych testach.** Bez tego cała reszta jest dobrowolna.

---

## Czego nie robić

| Antywzorzec | Dlaczego |
|---|---|
| Testowanie na SQLite | Fałszywe bezpieczeństwo — inny dialekt niż produkcja |
| Mockowanie SQLAlchemy | Testujesz wtedy mocka, nie kod. Prawdziwa baza w Dockerze jest tania |
| Jeden wielki test „end-to-end" na wszystko | Przy porażce nie wiadomo, co się zepsuło |
| Testy zależne od kolejności | `TRUNCATE` po każdym teście to załatwia — nie polegaj na stanie z poprzedniego |
| Asercja tylko na kod odpowiedzi | `assert response.status_code == 200` nie sprawdza, czy dane są poprawne |
| Dopisywanie `pragma: no cover` dla procentu | Kłamiesz sobie w raporcie |
| Sztywne `sleep()` w testach | Poza jednym przypadkiem wygasania presigned URL, gdzie jest nieunikniony |
