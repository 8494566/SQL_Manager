"""Service functions for clan (Clan) operations."""

from __future__ import annotations

from .. import config
from ..db import Connection


def max_out(conn: Connection, clan_name: str) -> int:
    """Set all configured clan stats to their maximum for the named clan."""
    columns = list(config.CLAN_MAX.keys())
    set_clause = ", ".join(f"{col} = ?" for col in columns)
    params = [config.CLAN_MAX[col] for col in columns]
    params.append(clan_name)
    return conn.execute(
        f"UPDATE Clan SET {set_clause} WHERE ClanName = ?", params
    )


def delete_clan(conn: Connection, clan_name: str) -> int:
    """Delete a clan by name. Corrects the legacy broken statement
    (``WHERE ClanName = = '<name>'``).
    """
    return conn.execute("DELETE FROM Clan WHERE ClanName = ?", (clan_name,))
