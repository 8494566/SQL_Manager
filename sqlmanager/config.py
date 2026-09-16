"""Application-wide configuration constants.

Values mirror the legacy MFC tool. Anything the legacy code hardcoded but that
depends on the deployed schema is centralized here so it can be corrected
without hunting through the codebase.
"""

APP_TITLE = "英雄岛数据库管理工具"
APP_VERSION = "1.0.0"

# Connection form defaults (from the legacy dialog).
DEFAULT_USER = "sa"
DEFAULT_CATALOG = "GameDB"
DEFAULT_AREA = "GameDBArea"

# Login timeout, seconds (legacy ADO used ConnectionTimeout = 8).
CONNECT_TIMEOUT = 8

# Fill / max values used by the "补满" operations.
MONEY_FILL = 99999999
# int32 overflow guard for experience (legacy: if exp < 0 -> this value).
EXP_OVERFLOW_CLAMP = 2130000000

# Camp / Sex code -> human-readable label (used by the summary view).
CAMP_LABELS = {1: "联邦", 2: "帝国"}
SEX_LABELS = {1: "男", 2: "女"}

# The Actor column that stores the owning account id.
# The legacy source misspelled this as "UsreID"; the real DB column is UserID.
ACTOR_OWNER_COLUMN = "UserID"

# Inventory containers used by the presets / copy-paste.
CONTAINER_CLASS_4 = 6
CONTAINER_CLASS_OTHER = 7
CONTAINER_EQUIP = 7

# Max-out values for a clan (from the legacy 兵团补满 UPDATE).
CLAN_MAX = {
    "ClanPaySparePerson": 250,
    "ClanPaySpareNum": 250,
    "ClanSparePerson": 250,
    "ClanSpareNum": 250,
    "ClanMoney": 99999999,
    "ClanExp": 99999999,
    "ClanLevel": 25,
    "ClanTech": 20,
    "ClanTech2": 20,
    "ClanTech3": 20,
    "Popularity": 99999999,
}

# SHA1-of-empty-string, the legacy default for the ActorPsw column.
EMPTY_SHA1_HEX = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
