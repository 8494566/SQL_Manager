## Why

The current game GM admin tool is a Windows-only C++/MFC app tied to `SQLOLEDB`, a `SkinH.dll` skin, Windows registry, and MAC-based licensing. It is hard to maintain, ships broken SQL (`DELETE FROM dbo.Actor = '<name>' WHERE ...`), embeds a hardcoded production credential, and interpolates raw user input into SQL. Rewriting it in Python with a modern Flet UI gives a cleaner, better-looking, parameterized, easily-packaged tool.

## What Changes

- Rewrite the entire app in Python 3 with a **Flet** desktop UI (modern, themed, dark/light).
- Keep **SQL Server only** connectivity, via `pyodbc` (ODBC Driver 17/18), with **parameterized queries** replacing all raw string interpolation.
- Port all GM operations: connect, bind character (by name / by ID), edit point / gold (HoldMoney) / exp / level / rename / camp / sex / clan reset / shopping money, delete character, clan max-out & delete, inventory class item-set fills (containers 6/7) and copy/paste equipment, character transfer between accounts.
- Port account operations against the separate `Area` DB: create account and change password using SQL Server SHA1 hex hashing (`substring(sys.fn_VarBinToHexStr(hashbytes('SHA1', ?)), 3, 128)`).
- Port the read-only "message" stat summary view (camp/sex code mapping).
- **BREAKING**: Remove MAC-based licensing, the `MyOwn` license table auto-connect path, and the hardcoded production credential.
- **BREAKING**: Replace Windows-registry "remember password" with a **local encrypted credential store** (no plaintext, no registry).
- Fix the two broken SQL statements (delete character, delete clan) and the `Actor.UsreID` typo (map to correct column, configurable).
- Package as a single distributable via **PyInstaller** (one-file/one-dir), no MFC/ODBC-skin DLL dependencies bundled by us beyond the system ODBC driver.

## Capabilities

### New Capabilities
- `app-shell-ui`: Flet application shell ¡ª window, theming (dark/light), navigation between feature panels, status/toast feedback, packaging entrypoint.
- `db-connection`: SQL Server connection management via `pyodbc`, connection form (user/password/catalog/data-source/area), connect/disconnect state, parameterized query execution helper.
- `credential-store`: Local encrypted "remember me" store replacing registry; save/load/clear last connection secrets.
- `character-management`: Bind a character by name or ID, view cached stats, and edit point/gold/exp/level/name/camp/sex/clan-reset/shopping-money; delete a character.
- `inventory-management`: Apply predefined class item-set blobs to inventory containers (6/7), and copy/paste a character's equipment blob between characters.
- `clan-management`: Max-out a clan's stats and delete a clan by name.
- `account-management`: Create a game account and change an account password against the `Area` database using SHA1 hex hashing.

### Modified Capabilities
<!-- None ¡ª no prior OpenSpec specs exist in openspec/specs/. -->

## Impact

- New Python codebase (replaces `MFCAppManager/` C++ sources; old sources retained for reference, not deleted by this change).
- New dependencies: `flet`, `pyodbc`; dev/build: `pyinstaller`, `cryptography` (for credential encryption).
- External requirement: SQL Server reachable + **Microsoft ODBC Driver for SQL Server** installed on the host.
- Data assets: the large hardcoded `0x¡­` item-set blobs and the `GoodsBuf` byte layout must be extracted verbatim from `MFCAppManagerDlg.cpp` into Python data files.
- Configuration: `Area` database name (default `GameDBArea`) and the `Actor` user-id column name become explicit config inputs.
