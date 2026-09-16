"""SQL Server connection wrapper (pyodbc).

Replaces the legacy ADO/SQLOLEDB access. All statements go through parameterized
``execute`` / ``query_*`` helpers - no raw string interpolation of user input.
"""

from __future__ import annotations

import re
from typing import Any, Sequence

import pyodbc

from . import config


class DatabaseError(Exception):
    """User-facing database error (already carries a readable message)."""


class DriverNotFoundError(DatabaseError):
    """No Microsoft ODBC Driver for SQL Server is installed."""


_PREFERRED_DRIVERS = (
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


def find_driver() -> str:
    installed = set(pyodbc.drivers())
    for name in _PREFERRED_DRIVERS:
        if name in installed:
            return name
    raise DriverNotFoundError(
        "未找到 Microsoft ODBC Driver for SQL Server。\n"
        "请安装 ODBC Driver 17 或 18: "
        "https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"
    )


def validate_identifier(name: str, what: str = "标识符") -> str:
    """Validate a SQL identifier that cannot be passed as a bound parameter
    (e.g. the cross-database ``Area`` name). Prevents injection via that field.
    """
    if not name or not _IDENTIFIER_RE.match(name):
        raise DatabaseError(f"非法的{what}: {name!r}")
    return name


class Connection:
    """Stateful SQL Server connection."""

    def __init__(self) -> None:
        self._conn: pyodbc.Connection | None = None

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    def connect(
        self,
        *,
        user: str,
        password: str,
        catalog: str,
        data_source: str,
    ) -> None:
        if self.is_connected:
            raise DatabaseError("已经连接到数据库了，请勿再次连接！")

        driver = find_driver()
        parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={data_source}",
            f"DATABASE={catalog}",
            f"UID={user}",
            f"PWD={password}",
        ]
        # Driver 18 defaults to Encrypt=yes with cert validation; game servers
        # rarely have valid certs, so trust the server certificate.
        if driver == "ODBC Driver 18 for SQL Server":
            parts.append("Encrypt=no")
            parts.append("TrustServerCertificate=yes")
        conn_str = ";".join(parts) + ";"

        try:
            self._conn = pyodbc.connect(conn_str, timeout=config.CONNECT_TIMEOUT)
        except pyodbc.Error as exc:
            self._conn = None
            raise DatabaseError(f"不能连接数据库！\n{_message(exc)}") from exc

    def disconnect(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None

    def _cursor(self) -> pyodbc.Cursor:
        if self._conn is None:
            raise DatabaseError("请先连接数据库！")
        return self._conn.cursor()

    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        """Run a non-query statement; returns affected row count."""
        cur = self._cursor()
        try:
            cur.execute(sql, params)
            affected = cur.rowcount
            self._conn.commit()  # type: ignore[union-attr]
            return affected
        except pyodbc.Error as exc:
            raise DatabaseError(_message(exc)) from exc
        finally:
            cur.close()

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> dict | None:
        rows = self.query_all(sql, params)
        return rows[0] if rows else None

    def query_all(self, sql: str, params: Sequence[Any] = ()) -> list[dict]:
        cur = self._cursor()
        try:
            cur.execute(sql, params)
            columns = [c[0] for c in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except pyodbc.Error as exc:
            raise DatabaseError(_message(exc)) from exc
        finally:
            cur.close()


def _message(exc: pyodbc.Error) -> str:
    try:
        return str(exc.args[1]) if len(exc.args) > 1 else str(exc)
    except Exception:
        return str(exc)
