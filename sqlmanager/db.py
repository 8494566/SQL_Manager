"""数据库连接封装，支持 SQL Server (pyodbc) 与 MySQL (PyMySQL)。

所有语句都走参数化 ``execute`` / ``query_*``；服务层统一用 ``?`` 占位符，
MySQL 后端会自动转成 ``%s``。方言差异（跨库账号表写法、密码哈希函数）由本模块封装。
"""

from __future__ import annotations

import re
from typing import Any, Sequence

import pyodbc

from . import config

# 后端标识 -> 显示名
BACKENDS = {
    "sqlserver": "SQL Server",
    "mysql": "MySQL",
}


class DatabaseError(Exception):
    """面向用户的数据库错误（已带可读信息）。"""


class DriverNotFoundError(DatabaseError):
    """未安装所需驱动。"""


_PREFERRED_DRIVERS = (
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")

_DEFAULT_MYSQL_PORT = 3306
_DEFAULT_SQLSERVER_PORT = 1433


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
    """校验无法作为绑定参数传入的 SQL 标识符（如跨库 Area 名），防止注入。"""
    if not name or not _IDENTIFIER_RE.match(name):
        raise DatabaseError(f"非法的{what}: {name!r}")
    return name


def _split_host_port(data_source: str, default_port: int) -> tuple[str, int]:
    host = data_source.strip()
    for sep in (",", ":"):
        if sep in host:
            head, _, tail = host.rpartition(sep)
            try:
                return head.strip(), int(tail.strip())
            except ValueError:
                return host, default_port
    return host, default_port


class Connection:
    """有状态的数据库连接。"""

    def __init__(self) -> None:
        self._conn: Any | None = None
        self.backend: str = "sqlserver"

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    # ------------------------------------------------------------- connect
    def connect(
        self,
        *,
        backend: str,
        user: str,
        password: str,
        catalog: str,
        data_source: str,
    ) -> None:
        if self.is_connected:
            raise DatabaseError("已经连接到数据库了，请勿再次连接！")
        if backend not in BACKENDS:
            raise DatabaseError(f"未知的数据库类型: {backend}")
        self.backend = backend
        if backend == "mysql":
            self._connect_mysql(user, password, catalog, data_source)
        else:
            self._connect_sqlserver(user, password, catalog, data_source)

    def _connect_sqlserver(
        self, user: str, password: str, catalog: str, data_source: str
    ) -> None:
        driver = find_driver()
        parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={data_source}",
            f"DATABASE={catalog}",
            f"UID={user}",
            f"PWD={password}",
        ]
        if driver == "ODBC Driver 18 for SQL Server":
            parts.append("Encrypt=no")
            parts.append("TrustServerCertificate=yes")
        conn_str = ";".join(parts) + ";"
        try:
            self._conn = pyodbc.connect(conn_str, timeout=config.CONNECT_TIMEOUT)
        except pyodbc.Error as exc:
            self._conn = None
            raise DatabaseError(f"不能连接数据库！\n{_message(exc)}") from exc

    def _connect_mysql(
        self, user: str, password: str, catalog: str, data_source: str
    ) -> None:
        try:
            import pymysql
        except ImportError as exc:  # pragma: no cover
            raise DriverNotFoundError(
                "未安装 PyMySQL，请运行: pip install pymysql"
            ) from exc
        host, port = _split_host_port(data_source, _DEFAULT_MYSQL_PORT)
        try:
            self._conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=catalog,
                connect_timeout=config.CONNECT_TIMEOUT,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        except Exception as exc:
            self._conn = None
            raise DatabaseError(f"不能连接数据库！\n{_message(exc)}") from exc

    def disconnect(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None

    # ------------------------------------------------------------- dialect
    @property
    def hash_expr(self) -> str:
        """返回把一个绑定参数（明文密码）算成 SHA1 十六进制串的 SQL 片段。

        两个后端都产出 40 位小写十六进制，格式一致。
        """
        if self.backend == "mysql":
            return "SHA1(?)"
        return (
            "substring(sys.fn_VarBinToHexStr("
            "hashbytes('SHA1', CAST(? AS VARCHAR(128)))), 3, 128)"
        )

    def account_table(self, area: str) -> str:
        """跨库 account 表的限定名。"""
        area = validate_identifier(area, "Area 数据库名")
        if self.backend == "mysql":
            return f"`{area}`.account"
        return f"[{area}]..account"

    def _translate(self, sql: str) -> str:
        return sql.replace("?", "%s") if self.backend == "mysql" else sql

    # ------------------------------------------------------------- execute
    def _cursor(self):
        if self._conn is None:
            raise DatabaseError("请先连接数据库！")
        return self._conn.cursor()

    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        cur = self._cursor()
        try:
            cur.execute(self._translate(sql), tuple(params))
            affected = cur.rowcount
            self._conn.commit()
            return affected
        except _DB_ERRORS as exc:
            raise DatabaseError(_message(exc)) from exc
        finally:
            cur.close()

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> dict | None:
        rows = self.query_all(sql, params)
        return rows[0] if rows else None

    def query_all(self, sql: str, params: Sequence[Any] = ()) -> list[dict]:
        cur = self._cursor()
        try:
            cur.execute(self._translate(sql), tuple(params))
            rows = cur.fetchall()
            if self.backend == "mysql":
                # DictCursor already returns dicts.
                return list(rows)
            columns = [c[0] for c in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in rows]
        except _DB_ERRORS as exc:
            raise DatabaseError(_message(exc)) from exc
        finally:
            cur.close()


def _mysql_error_types() -> tuple:
    try:
        import pymysql

        return (pymysql.MySQLError,)
    except ImportError:  # pragma: no cover
        return tuple()


_DB_ERRORS = (pyodbc.Error,) + _mysql_error_types()


def _message(exc: Exception) -> str:
    try:
        if len(exc.args) > 1:
            return str(exc.args[1])
    except Exception:
        pass
    return str(exc)
