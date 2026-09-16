"""Service functions for character (Actor) operations.

Pure DB logic - no UI. All SQL is parameterized. Additive operations
(point/gold/exp) re-read the current DB value at call time, fixing the legacy
stale-accumulation bug.
"""

from __future__ import annotations

from .. import config
from ..db import Connection, DatabaseError, validate_identifier


def bind_by_name(conn: Connection, name: str) -> dict:
    row = conn.query_one(
        "SELECT * FROM Actor WHERE ActorName = ?", (name,)
    )
    if row is None:
        raise DatabaseError("找不到该角色！")
    return row


def bind_by_id(conn: Connection, actor_id: int) -> dict:
    row = conn.query_one(
        "SELECT * FROM Actor WHERE ActorID = ?", (actor_id,)
    )
    if row is None:
        raise DatabaseError("找不到该角色！")
    return row


def _current(conn: Connection, name: str, column: str) -> int:
    row = conn.query_one(
        f"SELECT {column} AS v FROM Actor WHERE ActorName = ?", (name,)
    )
    if row is None:
        raise DatabaseError("找不到该角色！")
    return int(row["v"] or 0)


def add_points(conn: Connection, name: str, amount: int) -> int:
    total = _current(conn, name, "point") + amount
    conn.execute("UPDATE Actor SET point = ? WHERE ActorName = ?", (total, name))
    return total


def add_gold(conn: Connection, name: str, amount: int) -> int:
    total = _current(conn, name, "HoldMoney") + amount
    conn.execute(
        "UPDATE Actor SET HoldMoney = ? WHERE ActorName = ?", (total, name)
    )
    return total


def fill_gold(conn: Connection, name: str) -> None:
    conn.execute(
        "UPDATE Actor SET HoldMoney = ? WHERE ActorName = ?",
        (config.MONEY_FILL, name),
    )


def fill_shopping(conn: Connection, name: str) -> None:
    conn.execute(
        "UPDATE Actor SET ShoppingMoney = ? WHERE ActorName = ?",
        (config.MONEY_FILL, name),
    )


def add_exp(conn: Connection, name: str, amount: int) -> int:
    total = _current(conn, name, "ExploitAll") + amount
    if total < 0:
        total = config.EXP_OVERFLOW_CLAMP
    conn.execute(
        "UPDATE Actor SET ExploitAll = ? WHERE ActorName = ?", (total, name)
    )
    return total


def set_level(conn: Connection, name: str, level: int) -> None:
    conn.execute(
        "UPDATE Actor SET ExploitLevel = ? WHERE ActorName = ?", (level, name)
    )


def rename(conn: Connection, old_name: str, new_name: str) -> None:
    conn.execute(
        "UPDATE Actor SET ActorName = ? WHERE ActorName = ?",
        (new_name, old_name),
    )


def set_camp(conn: Connection, name: str, camp: int) -> None:
    conn.execute(
        "UPDATE Actor SET CampID = ? WHERE ActorName = ?", (camp, name)
    )


def set_sex(conn: Connection, name: str, sex: int) -> None:
    conn.execute("UPDATE Actor SET Sex = ? WHERE ActorName = ?", (sex, name))


def reset_clan(conn: Connection, name: str) -> None:
    conn.execute("UPDATE Actor SET ClanID = 0 WHERE ActorName = ?", (name,))


def delete_character(conn: Connection, name: str) -> int:
    """Delete by name. Corrects the legacy broken statement
    (``DELETE FROM dbo.Actor = '<name>' WHERE ...``).
    """
    return conn.execute("DELETE FROM Actor WHERE ActorName = ?", (name,))


def transfer(
    conn: Connection, *, area: str, actor_id: int, target_account: str
) -> None:
    """Move a character to another account by resolving the target account's
    UserID from ``[<area>]..account`` and updating the Actor owner column.
    """
    area = validate_identifier(area, "Area 数据库名")
    owner_col = config.ACTOR_OWNER_COLUMN
    row = conn.query_one(
        f"SELECT UserID FROM [{area}]..account WHERE UserName = ?",
        (target_account,),
    )
    if row is None:
        raise DatabaseError("目标账号不存在！")
    conn.execute(
        f"UPDATE Actor SET {owner_col} = ? WHERE ActorID = ?",
        (row["UserID"], actor_id),
    )


def summary(stats: dict) -> dict:
    """Build a read-only, human-readable summary from bound-character stats."""
    camp = stats.get("CampID")
    sex = stats.get("Sex")
    return {
        "角色名": stats.get("ActorName"),
        "ID": stats.get("ActorID"),
        "点数": stats.get("point"),
        "等级": stats.get("ExploitLevel"),
        "金币": stats.get("HoldMoney"),
        "经验": stats.get("ExploitAll"),
        "阵营": config.CAMP_LABELS.get(camp, str(camp)),
        "性别": config.SEX_LABELS.get(sex, str(sex)),
    }
