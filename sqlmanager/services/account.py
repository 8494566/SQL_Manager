"""Service functions for account operations (Area database).

Passwords are hashed server-side with the exact legacy SQL Server expression so
stored hashes stay byte-identical to the old tool. The cleartext password is
CAST to VARCHAR before hashing to match the legacy varchar literals (nvarchar
would hash differently).
"""

from __future__ import annotations

from .. import config
from ..db import Connection, DatabaseError, validate_identifier

# Server-side SHA1 hex of a VARCHAR password (matches legacy behaviour).
_HASH_EXPR = "substring(sys.fn_VarBinToHexStr(hashbytes('SHA1', CAST(? AS VARCHAR(128)))), 3, 128)"


def account_exists(conn: Connection, area: str, user_name: str) -> bool:
    area = validate_identifier(area, "Area 数据库名")
    row = conn.query_one(
        f"SELECT UserName FROM [{area}]..account WHERE UserName = ?",
        (user_name,),
    )
    return row is not None


def create_account(
    conn: Connection, *, area: str, user_name: str, password: str
) -> None:
    area = validate_identifier(area, "Area 数据库名")
    if account_exists(conn, area, user_name):
        raise DatabaseError("该账号已存在！")

    sql = (
        f"INSERT INTO [{area}]..account "
        "(LoginType, UserName, PassWord, AreaWorld, GameWorld, Ip, SerialNO, "
        "BuffHardDisk, BuffBios, BuffCpu, ToCenterDB, UserType, SecPsw, lPPFlag, "
        "UserMatrix, PromptFlag, PromptMsg, ConfigVIP, MediaID, QQ, TxzUserName, "
        "ActorPsw, NewUser, HasPID, Point) VALUES ("
        f"0, ?, {_HASH_EXPR}, NULL, NULL, NULL, NULL, NULL, NULL, NULL, "
        f"0, 0, {_HASH_EXPR}, 0, 0, 0, 'login success!', 0, 0, '111111', 'no', "
        "?, 0, 1, NULL)"
    )
    conn.execute(
        sql,
        (user_name, password, password, config.EMPTY_SHA1_HEX),
    )


def change_password(
    conn: Connection, *, area: str, user_name: str, password: str
) -> None:
    area = validate_identifier(area, "Area 数据库名")
    if not account_exists(conn, area, user_name):
        raise DatabaseError("没有这个账号！")
    conn.execute(
        f"UPDATE [{area}]..account SET PassWord = {_HASH_EXPR} "
        "WHERE UserName = ?",
        (password, user_name),
    )
