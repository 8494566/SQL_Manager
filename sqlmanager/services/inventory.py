"""Service functions for inventory (Goods) operations.

Item-set presets and equipment copy/paste. ``GoodsBuf`` is bound as ``bytes``
to the varbinary column (no hex-string assembly).
"""

from __future__ import annotations

from ..assets.itemsets_data import ITEM_SETS
from .. import config
from ..db import Connection, DatabaseError


def presets() -> list[tuple[str, str]]:
    """Return (key, label) pairs for the UI, in definition order."""
    return [(k, v["label"]) for k, v in ITEM_SETS.items()]


def apply_preset(conn: Connection, actor_id: int, key: str) -> None:
    preset = ITEM_SETS.get(key)
    if preset is None:
        raise DatabaseError(f"未知的套装: {key}")
    container = preset["container"]
    conn.execute(
        "DELETE FROM Goods WHERE ContainerID = ? AND ActorID = ?",
        (container, actor_id),
    )
    conn.execute(
        "INSERT INTO Goods (ContainerID, ActorID, GoodsBuf, GoodsNum) "
        "VALUES (?, ?, ?, ?)",
        (container, actor_id, preset["buf"], preset["goods_num"]),
    )


def copy_equipment(conn: Connection, actor_id: int) -> dict:
    """Read the character's equipment blob from the equip container."""
    row = conn.query_one(
        "SELECT GoodsBuf, GoodsNum FROM Goods "
        "WHERE ActorID = ? AND ContainerID = ?",
        (actor_id, config.CONTAINER_EQUIP),
    )
    if row is None or row.get("GoodsBuf") is None:
        raise DatabaseError("该角色没有可复制的装备！")
    return {
        "buf": bytes(row["GoodsBuf"]),
        "goods_num": int(row["GoodsNum"] or 0),
    }


def paste_equipment(conn: Connection, actor_id: int, clip: dict | None) -> None:
    if not clip or clip.get("buf") is None:
        raise DatabaseError("没有已复制的装备！")
    container = config.CONTAINER_EQUIP
    conn.execute(
        "DELETE FROM Goods WHERE ContainerID = ? AND ActorID = ?",
        (container, actor_id),
    )
    conn.execute(
        "INSERT INTO Goods (ContainerID, ActorID, GoodsBuf, GoodsNum) "
        "VALUES (?, ?, ?, ?)",
        (container, actor_id, clip["buf"], clip["goods_num"]),
    )
