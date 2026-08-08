# Coin Master — dokumentacja planu

Zestaw dokumentów opisujący drogę od obecnego stanu repozytorium do działającego MVP,
a następnie do wersji zaawansowanej.

**Kolejność czytania:**

| Dokument | Co zawiera |
|---|---|
| [01_STAN_OBECNY.md](01_STAN_OBECNY.md) | Co realnie jest w repo — co działa, co jest zepsute, czego brakuje |
| [02_NAPRAWY_PRZED_MVP.md](02_NAPRAWY_PRZED_MVP.md) | Faza 0 — co trzeba naprawić **zanim** zaczniemy MVP |
| [03_MVP_BACKEND.md](03_MVP_BACKEND.md) | Zakres MVP (backend), model danych, endpointy, definicja ukończenia |
| [04_ZAAWANSOWANE.md](04_ZAAWANSOWANE.md) | Co po MVP — OCR, gwarancje, front, infrastruktura |
| [05_TESTY.md](05_TESTY.md) | Strategia testów i droga do 100% pokrycia |
| [06_OCR_SPIKE.md](06_OCR_SPIKE.md) | Dokument roboczy — 2-dniowe badanie, który OCR wybrać |

> `06_OCR_SPIKE.md` czyta się dopiero przy fazie Z2. Warto jednak zajrzeć tam **wcześniej**:
> wymaga przygotowania 20 zdjęć paragonów, które najlepiej zbierać już w trakcie MVP.

---

## Decyzje projektowe (ustalone)

Te decyzje są podjęte świadomie i stanowią założenia całej dokumentacji.
Można je zmienić, ale **przed** napisaniem kodu — później kosztują migracje.

| # | Decyzja | Wybór | Uzasadnienie |
|---|---|---|---|
| D1 | Zakres danych | **Jednoosobowy** — wszystko scoped po `user_id` | Brak porównań między użytkownikami. Historia cen dotyczy własnych paragonów ze wszystkich sklepów |
| D2 | Storage na czas MVP | **MinIO lokalnie**, AWS S3 przy deployu | Ten sam kod (`endpoint_url`), bez konta AWS, bez karty, działa offline |
| D3 | Dostęp do zdjęć | **Bucket prywatny + presigned URL** | Paragony zawierają dane wrażliwe. Podgląd 15 min, udostępnianie 7 dni (maksimum AWS) |
| D4 | Trwałe udostępnienie | **Załącznik e-mail** | Przypadek „reklamacja w sklepie po 3 tygodniach" — plik zostaje u odbiorcy, niezależnie od linków |
| D5 | Zdjęcie paragonu | **Opcjonalne** (`scan_file` nullable) | Paragon można dodać ręcznie gdy zdjęcie się nie udało lub wyblakło |
| D6 | Historia cen produktu | **Auto-normalizacja nazwy** | Kolumna `normalized_name` + indeks. Zero pracy dla użytkownika |
| D7 | Kolejność prac | **Backend, potem front** | Front (React Native) dopiero po zamknięciu MVP backendu |
| D8 | Baza danych | **PostgreSQL** | Już jest, migracje są pod nią napisane, analytics korzysta z window functions |

---

## Uwaga o `plan_dzialnia.txt`

Plik `.claude/plan_dzialnia.txt` zawiera **nieaktualne informacje** w sekcji „Co już istnieje"
(m.in. Redis i MinIO w Dockerze, działające testy, gotowy storage). Szczegółowe sprostowania
znajdują się w [01_STAN_OBECNY.md](01_STAN_OBECNY.md#sprostowania-do-plan_dzialniatxt).

Traktuj `plan_dzialnia.txt` jako zapis pierwotnej wizji produktu, a nie jako opis stanu kodu.
