# 英雄岛数据库管理工具 (Python rewrite)

Modern rewrite of the legacy MFC game GM admin tool, built with **Flet** and
**pyodbc** targeting **Microsoft SQL Server**.

## Prerequisites

- Python 3.11+
- **Microsoft ODBC Driver for SQL Server** installed on the host
  (ODBC Driver 17 or 18). The app auto-detects an installed driver; if none is
  found it shows an actionable error. Download:
  https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Item-set data assets

The class item-set blobs and equipment layouts were extracted **verbatim** from
the original C++ source into `sqlmanager/assets/itemsets_data.py` by
`tools/extract_itemsets.py`. The generated data file is committed; the original
source has been removed from the repo, so the generator is kept only as a
record of provenance and is no longer runnable.

## Packaging

Build a standalone, no-Python-required Windows executable with Flet's packer
(wraps PyInstaller and bundles the Flet client):

```bash
pip install pyinstaller
flet pack main.py --name HeroIslandDB --distpath dist -y
```

Output: `dist/HeroIslandDB.exe` (single file, ~93 MB). The target host still
needs the Microsoft ODBC Driver installed (not bundled).

## Notes

Compared to the legacy tool this rewrite:
- uses parameterized SQL everywhere (no raw string interpolation),
- fixes the broken delete-character / delete-clan statements,
- drops MAC-based licensing and the hardcoded credential,
- replaces the Windows-registry "remember password" with a local **encrypted**
  credential store.
