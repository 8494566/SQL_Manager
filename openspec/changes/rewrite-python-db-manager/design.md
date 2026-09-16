## Context

The existing tool (`MFCAppManager/`) is a Windows C++/MFC dialog app that administers a game's SQL Server database (`GameDB`) and a separate account database (`GameDBArea`). It connects via ADO/`SQLOLEDB`, skins itself with `SkinH.dll`, remembers credentials in the Windows registry, and gates usage behind MAC-address licensing with a hardcoded production credential in `RememberInit()`. All SQL is built by raw string interpolation; two statements are syntactically broken and one column is misspelled (`Actor.UsreID`).

We are rewriting it in Python with a Flet UI. Decisions already locked with the user: **Flet** UI, **SQL Server only** via `pyodbc`, **drop MAC licensing** but **keep an (encrypted) remember-password**, and **easy PyInstaller packaging**.

The complete legacy behavior and SQL map is recorded in the proposal and specs, derived from `MFCAppManagerDlg.cpp`.

## Goals / Non-Goals

**Goals:**
- Reproduce all GM operations (character, inventory, clan, account, summary) with correct, parameterized SQL.
- Modern Flet UI with light/dark theming and clear per-action feedback.
- Encrypted local credential store replacing the registry.
- Single-command PyInstaller build producing a distributable with no source dependency on MFC/ADO/SkinH.
- Preserve the exact item-set blobs and `GoodsBuf` semantics so in-game results match the legacy tool.

**Non-Goals:**
- Multi-database support (MySQL/PG/SQLite) — SQL Server only.
- MAC-based licensing or any device binding.
- Re-implementing the `SkinH` skin engine (Flet theming replaces it).
- Changing the game's DB schema; we adapt to it.

## Decisions

### UI framework: Flet
Chosen per user. Flet gives a modern Flutter-rendered UI with minimal Python code and packages via PyInstaller. Alternatives: PySide6 (heavier, more controls but more packaging setup), CustomTkinter (smaller but fewer components). Trade-off accepted: larger bundle and slower cold start than Tkinter.

### DB access: `pyodbc` + Microsoft ODBC Driver
`SQLOLEDB` is deprecated; `pyodbc` with `ODBC Driver 17/18 for SQL Server` is the current path. Connection string mirrors the legacy fields: `DRIVER={ODBC Driver 17 for SQL Server};SERVER=<data source>;DATABASE=<catalog>;UID=<user>;PWD=<pwd>;` plus a login timeout. All statements use `cursor.execute(sql, params)` with `?` placeholders. Cross-DB account statements reference `[<Area>]..account` — the `Area` name is validated/whitelisted (identifier, not a parameter) since it cannot be bound.

### Layered structure
- `db.py` — `Connection` wrapper: connect/disconnect/state, `execute(sql, params)`, `query_one/query_all`.
- `services/` — one module per capability (`character.py`, `inventory.py`, `clan.py`, `account.py`) holding pure functions that take the connection + values and run parameterized SQL. No UI here.
- `ui/` — Flet panels per capability, plus the app shell (`app.py`) wiring navigation, theme toggle, and snackbar feedback.
- `credentials.py` — encrypted store.
- `assets/itemsets.py` (or JSON) — the extracted class/container blobs.
- `main.py` — entrypoint calling `ft.app(...)`.

### Item-set blobs as data assets
The large hardcoded `0x…` blobs (per class, containers 6/7) and the copy/paste `GoodsBuf` layout must be copied verbatim from `MFCAppManagerDlg.cpp` into a Python data module keyed by (preset name → container, GoodsBuf bytes, GoodsNum). `GoodsBuf` is passed to `pyodbc` as `bytes` bound to a `varbinary` column, avoiding hex-string assembly. This preserves exact in-game outcomes.

### SHA1 password hashing stays server-side
Account create/change reuse the exact SQL Server expression `substring(sys.fn_VarBinToHexStr(hashbytes('SHA1', ?)), 3, 128)` with the cleartext password bound as a parameter, so stored hashes remain byte-identical to the legacy tool. `ActorPsw` default remains the SHA1-of-empty-string constant.

### Credential store: encrypted file via `cryptography.Fernet`
Store JSON (data source, user, catalog, area, password) encrypted with a Fernet key persisted in a per-user app-data file with restrictive intent. Replaces registry + plaintext. Disabling remember-me deletes the file. Key is generated on first save and stored alongside (obfuscation-grade, not a secrets vault — matches the tool's threat model, strictly better than the plaintext-registry original).

### Bind-then-edit state
Edit operations require a bound character. On each mutating op, re-read the current DB value for additive fields (point/gold/exp) rather than trusting stale cached values, fixing the legacy stale-accumulation bug. Camp/Sex use a 2-value selector (1/2). Delete-character and delete-clan use corrected parameterized SQL.

### Packaging: PyInstaller
`flet pack main.py` (or `pyinstaller` spec) produces the distributable; document that the target host needs the Microsoft ODBC Driver installed (not bundled). Provide a build script/spec file.

## Risks / Trade-offs

- [ODBC driver not installed on target] → Detect the missing-driver error and show an actionable message with the download/name; document the prerequisite in build notes.
- [Item-set blobs copied incorrectly] → Extract bytes programmatically from the source and verify length/content against the legacy values before shipping; keep them in one reviewable data module.
- [Cross-DB `Area` name cannot be parameterized] → Validate `Area` as a SQL identifier (whitelist charset) before embedding, preventing injection via that field.
- [Flet bundle size / cold start] → Accepted per framework choice; use one-dir build if startup matters.
- [Encrypted store key stored locally] → Documented as obfuscation-grade; still strictly better than the legacy plaintext registry value.
- [Schema typo `UsreID`] → Make the owner user-id column name a config constant defaulting to the actual DB column; confirm against the live schema.

## Migration Plan

1. Stand up the Python project alongside the existing `MFCAppManager/` (do not delete legacy sources).
2. Implement `db.py` + `credentials.py`, then services, then UI panels, then packaging.
3. Verify each operation against a test SQL Server / `GameDB` copy, comparing effects to the legacy tool (especially item-set blobs and account hashes).
4. Ship the PyInstaller artifact; retire the MFC app once parity is confirmed.
5. Rollback: the legacy MFC executable remains usable until parity is signed off.

## Open Questions

- Exact `GoodsBuf` byte length (legacy assumed ~3888) and the full untruncated blob bytes — must be read verbatim from source.
- Correct real column name behind the legacy `Actor.UsreID` (confirm `UserID`).
- Definitive meaning/labels of `CampID` and `Sex` codes (1 vs 2) for the summary view.
- Whether more inventory containers than 6/7 need presets.
