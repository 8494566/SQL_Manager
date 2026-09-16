"""账号相关操作（Area 数据库）。

密码使用后端对应的 SHA1 十六进制表达式在服务端计算，两个后端都产出 40 位小写
十六进制，保持格式一致。
"""

from __future__ import annotations

from .. import config
from ..db import Connection, DatabaseError


def account_exists(conn: Connection, area: str, user_name: str) -> bool:
    table = conn.account_table(area)
    row = conn.query_one(
        f"SELECT UserName FROM {table} WHERE UserName = ?", (user_name,)
    )
    return row is not None


def create_account(
    conn: Connection, *, area: str, user_name: str, password: str
) -> None:
    table = conn.account_table(area)
    if account_exists(conn, area, user_name):
        raise DatabaseError("该账号已存在！")

    h = conn.hash_expr
    sql = (
        f"INSERT INTO {table} "
        "(LoginType, UserName, PassWord, AreaWorld, GameWorld, Ip, SerialNO, "
        "BuffHardDisk, BuffBios, BuffCpu, ToCenterDB, UserType, SecPsw, lPPFlag, "
        "UserMatrix, PromptFlag, PromptMsg, ConfigVIP, MediaID, QQ, TxzUserName, "
        "ActorPsw, NewUser, HasPID, Point) VALUES ("
        f"0, ?, {h}, NULL, NULL, NULL, NULL, NULL, NULL, NULL, "
        f"0, 0, {h}, 0, 0, 0, 'login success!', 0, 0, '111111', 'no', "
        "?, 0, 1, NULL)"
    )
    conn.execute(sql, (user_name, password, password, config.EMPTY_SHA1_HEX))


def change_password(
    conn: Connection, *, area: str, user_name: str, password: str
) -> None:
    table = conn.account_table(area)
    if not account_exists(conn, area, user_name):
        raise DatabaseError("没有这个账号！")
    conn.execute(
        f"UPDATE {table} SET PassWord = {conn.hash_expr} WHERE UserName = ?",
        (password, user_name),
    )
