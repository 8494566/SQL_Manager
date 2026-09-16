## 1. Project setup & packaging

- [x] 1.1 Create Python project layout (`src/` with `main.py`, `db.py`, `credentials.py`, `services/`, `ui/`, `assets/`) alongside existing `MFCAppManager/`
- [x] 1.2 Add dependencies: `flet`, `pyodbc`, `cryptography`; add dev dep `pyinstaller`; create `requirements.txt`
- [x] 1.3 Add `README`/build notes documenting the Microsoft ODBC Driver prerequisite
- [x] 1.4 Create PyInstaller build script/spec (`flet pack main.py` or `.spec`) and verify it produces a runnable artifact
- [x] 1.5 Add app icon and window title/config

## 2. Database layer

- [x] 2.1 Implement `Connection` wrapper: build pyodbc connection string from fields + login timeout
- [x] 2.2 Implement connect / disconnect / `is_connected` state and double-connect guard
- [x] 2.3 Implement `execute(sql, params)`, `query_one`, `query_all` using `?` bound parameters
- [x] 2.4 Map/surface driver errors (incl. missing-ODBC-driver) into user-friendly messages
- [x] 2.5 Add `Area` identifier validation helper (whitelist charset) for cross-DB `[<Area>]..account` references

## 3. Credential store

- [x] 3.1 Implement Fernet-based encrypted store: save/load/clear connection secrets in per-user app-data
- [x] 3.2 Generate/persist key on first save; ensure no plaintext and no registry usage
- [x] 3.3 Wire "remember me" opt-in: save on successful connect, prefill on startup, delete on disable

## 4. Item-set data assets

- [x] 4.1 Extract the hardcoded `0x…` class item-set blobs (containers 6/7, all jobs) verbatim from `MFCAppManagerDlg.cpp` into a data module keyed by preset → (container, GoodsBuf bytes, GoodsNum)
- [x] 4.2 Verify extracted blob lengths/bytes match the legacy values
- [x] 4.3 Confirm the `GoodsBuf` byte layout used by copy/paste (container 7)

## 5. Character service

- [x] 5.1 Bind by ActorName and by ActorID; cache stats; handle not-found
- [x] 5.2 Add-points and add-gold (re-read current DB value, write absolute total)
- [x] 5.3 Fill gold and fill shopping money (99999999)
- [x] 5.4 Add-exp with negative/overflow clamp to 2130000000
- [x] 5.5 Set level, rename, set camp (1/2), set sex (1/2), reset clan id to 0
- [x] 5.6 Delete character with corrected parameterized `DELETE`
- [x] 5.7 Transfer character: resolve target account UserID from `[<Area>]..account`, update owner user-id column (configurable, fixes `UsreID`)
- [x] 5.8 Build stat summary with camp/sex label mapping

## 6. Inventory service

- [x] 6.1 Apply class item-set preset: delete container rows for actor, insert `GoodsBuf`/`GoodsNum` (GoodsBuf bound as bytes)
- [x] 6.2 Copy equipment: read `GoodsBuf`/`GoodsNum` from container 7 into in-app clipboard; handle empty
- [x] 6.3 Paste equipment: delete container 7 rows, insert copied blob; guard against paste-without-copy

## 7. Clan service

- [x] 7.1 Max-out clan by name (all configured max fields)
- [x] 7.2 Delete clan with corrected parameterized `DELETE`

## 8. Account service

- [x] 8.1 Create account: uniqueness check, insert with SHA1 hex hashing and established default fields
- [x] 8.2 Change password: existence check, update `PassWord` with SHA1 hex expression

## 9. UI (Flet)

- [x] 9.1 App shell: window, Material theme, light/dark toggle, navigation between panels
- [x] 9.2 Connection panel: inputs with defaults (`sa`/`GameDB`/`GameDBArea`), validation, connect/disconnect, remember-me
- [x] 9.3 Character panel wired to character service (bind + all edit actions)
- [x] 9.4 Inventory panel wired to inventory service (presets + copy/paste)
- [x] 9.5 Clan panel wired to clan service
- [x] 9.6 Account panel wired to account service
- [x] 9.7 Message/summary view (read-only stats with labels)
- [x] 9.8 Non-blocking snackbar/banner feedback for all operations; disable feature panels until connected

## 10. Verification

- [ ] 10.1 Manually verify each operation against a test `GameDB`/`GameDBArea`, comparing effects to the legacy tool
- [ ] 10.2 Verify item-set fills and copy/paste produce identical in-game inventory as the legacy blobs
- [ ] 10.3 Verify account create/change produce byte-identical SHA1 hashes vs legacy
- [ ] 10.4 Build with PyInstaller and smoke-test the packaged executable on a clean host with ODBC driver
