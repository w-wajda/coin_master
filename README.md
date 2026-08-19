# Coin Master

Aplikacja do śledzenia paragonów i wydatków (backend).

Pełna dokumentacja planu rozwoju znajduje się w [`.claude/00_README.md`](.claude/00_README.md).

## Uruchomienie lokalne

```bash
cp .env.example .env
docker compose up -d
curl http://localhost:8000/health/
```

Panel MinIO (podgląd wgranych plików): http://localhost:9001 (`minioadmin` / `minioadmin`).

## Testy

```bash
poetry install
poetry run pytest
```
