"""Flet application shell and panels.

Wires the connection state, feature panels, theming and non-blocking feedback
to the service layer. All DB work goes through the services; this module is
UI-only.
"""

from __future__ import annotations

import flet as ft

from .. import config, credentials
from ..db import BACKENDS, Connection, DatabaseError
from ..services import account, character, clan, inventory


class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.conn = Connection()
        self.bound: dict | None = None
        self.clip: dict | None = None
        self._locked: list[ft.Control] = []

        page.title = f"{config.APP_TITLE} v{config.APP_VERSION}"
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = ft.Theme(color_scheme_seed=ft.colors.INDIGO)
        page.dark_theme = ft.Theme(color_scheme_seed=ft.colors.INDIGO)
        page.padding = 16
        try:
            page.window.width = 900
            page.window.height = 760
            page.window.min_width = 720
            page.window.min_height = 600
        except Exception:
            pass

        self._build()
        self._load_saved()
        self._set_connected(False)

    # ---------------------------------------------------------------- helpers
    def notify(self, message: str, error: bool = False) -> None:
        color = ft.colors.RED_400 if error else ft.colors.GREEN_600
        self.page.open(
            ft.SnackBar(ft.Text(message), bgcolor=color, duration=3000)
        )

    def run(self, fn, success: str | None = None) -> bool:
        """Execute a service call, surfacing success/error as a snackbar."""
        try:
            fn()
        except DatabaseError as exc:
            self.notify(str(exc), error=True)
            return False
        except Exception as exc:  # pragma: no cover - defensive
            self.notify(f"操作失败：{exc}", error=True)
            return False
        if success:
            self.notify(success)
        return True

    def require_bound(self) -> dict | None:
        if self.bound is None:
            self.notify("请先绑定角色！", error=True)
            return None
        return self.bound

    def _int(self, field: ft.TextField, what: str) -> int | None:
        try:
            return int((field.value or "").strip())
        except ValueError:
            self.notify(f"{what} 必须是数字！", error=True)
            return None

    def lock(self, control: ft.Control) -> ft.Control:
        self._locked.append(control)
        return control

    def _set_connected(self, connected: bool) -> None:
        for c in self._locked:
            c.disabled = not connected
        self.btn_connect.disabled = connected
        self.btn_disconnect.disabled = not connected
        self.conn_status.value = "已连接" if connected else "未连接"
        self.conn_status.color = (
            ft.colors.GREEN_400 if connected else ft.colors.GREY
        )
        self.page.update()

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        self._build_topbar()
        self._build_connection()
        self._build_tabs()
        self.page.add(
            self.topbar,
            self.connection_card,
            self.tabs,
        )

    def _build_topbar(self) -> None:
        self.theme_icon = ft.IconButton(
            icon=ft.icons.LIGHT_MODE,
            tooltip="切换主题",
            on_click=self._toggle_theme,
        )
        self.topbar = ft.Row(
            [
                ft.Text(config.APP_TITLE, size=22, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                self.theme_icon,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _toggle_theme(self, _=None) -> None:
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_icon.icon = ft.icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_icon.icon = ft.icons.LIGHT_MODE
        self.page.update()

    # -------------------------------------------------------- connection card
    def _build_connection(self) -> None:
        self.d_backend = ft.Dropdown(
            label="数据库类型", width=140, value="mysql",
            options=[ft.dropdown.Option(k, v) for k, v in BACKENDS.items()],
        )
        self.f_user = ft.TextField(label="用户名", value=config.DEFAULT_USER, width=160)
        self.f_pwd = ft.TextField(
            label="密码", password=True, can_reveal_password=True, width=160
        )
        self.f_source = ft.TextField(label="数据源 (IP)", width=200)
        self.f_catalog = ft.TextField(label="数据库", value=config.DEFAULT_CATALOG, width=160)
        self.f_area = ft.TextField(label="Area 库", value=config.DEFAULT_AREA, width=160)
        self.remember = ft.Checkbox(label="记住密码")
        self.conn_status = ft.Text("未连接")
        self.btn_connect = ft.FilledButton("连接", icon=ft.icons.LINK, on_click=self._connect)
        self.btn_disconnect = ft.OutlinedButton(
            "断开", icon=ft.icons.LINK_OFF, on_click=self._disconnect
        )

        self.connection_card = ft.Card(
            content=ft.Container(
                padding=14,
                content=ft.Column(
                    [
                        ft.Text("数据库连接", weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [self.d_backend, self.f_source, self.f_user, self.f_pwd, self.f_catalog, self.f_area],
                            wrap=True,
                        ),
                        ft.Row(
                            [
                                self.remember,
                                self.btn_connect,
                                self.btn_disconnect,
                                self.conn_status,
                            ],
                            spacing=14,
                        ),
                    ],
                    spacing=10,
                ),
            )
        )

    def _load_saved(self) -> None:
        data = credentials.load()
        if not data:
            return
        self.d_backend.value = data.get("backend", "mysql")
        self.f_user.value = data.get("user", config.DEFAULT_USER)
        self.f_pwd.value = data.get("password", "")
        self.f_source.value = data.get("data_source", "")
        self.f_catalog.value = data.get("catalog", config.DEFAULT_CATALOG)
        self.f_area.value = data.get("area", config.DEFAULT_AREA)
        self.remember.value = True

    def _connect(self, _=None) -> None:
        pwd = (self.f_pwd.value or "").strip()
        source = (self.f_source.value or "").strip()
        if not pwd or not source:
            self.notify("账号或者密码不能为空！", error=True)
            return
        ok = self.run(
            lambda: self.conn.connect(
                backend=self.d_backend.value,
                user=(self.f_user.value or "").strip(),
                password=pwd,
                catalog=(self.f_catalog.value or "").strip(),
                data_source=source,
            ),
            success="连接数据库成功！",
        )
        if not ok:
            return
        if self.remember.value:
            credentials.save(
                {
                    "backend": self.d_backend.value,
                    "user": self.f_user.value,
                    "password": pwd,
                    "data_source": source,
                    "catalog": self.f_catalog.value,
                    "area": self.f_area.value,
                }
            )
        else:
            credentials.clear()
        self._set_connected(True)

    def _disconnect(self, _=None) -> None:
        self.conn.disconnect()
        self.bound = None
        self.bound_label.value = "未绑定角色"
        self._set_connected(False)

    # ----------------------------------------------------------------- tabs
    def _build_tabs(self) -> None:
        self.tabs = ft.Tabs(
            expand=True,
            tabs=[
                ft.Tab(text="角色", icon=ft.icons.PERSON, content=self._tab_character()),
                ft.Tab(text="背包", icon=ft.icons.BACKPACK, content=self._tab_inventory()),
                ft.Tab(text="兵团", icon=ft.icons.GROUPS, content=self._tab_clan()),
                ft.Tab(text="账号", icon=ft.icons.KEY, content=self._tab_account()),
                ft.Tab(text="信息", icon=ft.icons.INFO, content=self._tab_info()),
            ],
        )

    def _pad(self, control: ft.Control) -> ft.Container:
        return ft.Container(content=control, padding=16)

    # -------- character tab
    def _tab_character(self) -> ft.Control:
        self.f_bind_name = ft.TextField(label="角色名", width=200)
        self.f_bind_id = ft.TextField(label="角色ID", width=140)
        self.bound_label = ft.Text("未绑定角色", weight=ft.FontWeight.BOLD)

        self.f_point = ft.TextField(label="点数增量", width=140)
        self.f_gold = ft.TextField(label="金币增量", width=140)
        self.f_exp = ft.TextField(label="经验增量", width=140)
        self.f_level = ft.TextField(label="等级", width=140)
        self.f_newname = ft.TextField(label="新角色名", width=200)
        self.d_camp = ft.Dropdown(
            label="阵营", width=140, value="1",
            options=[ft.dropdown.Option("1", "联邦"), ft.dropdown.Option("2", "帝国")],
        )
        self.d_sex = ft.Dropdown(
            label="性别", width=140, value="1",
            options=[ft.dropdown.Option("1", "男"), ft.dropdown.Option("2", "女")],
        )
        self.f_transfer = ft.TextField(label="目标账号", width=200)

        col = ft.Column(
            [
                ft.Row([
                    self.f_bind_name,
                    self.lock(ft.FilledButton("按名称绑定", on_click=self._bind_name)),
                    self.f_bind_id,
                    self.lock(ft.FilledButton("按ID绑定", on_click=self._bind_id)),
                ], wrap=True),
                self.bound_label,
                ft.Divider(),
                ft.Row([self.f_point, self.lock(ft.ElevatedButton("充值点数", on_click=self._add_point))], wrap=True),
                ft.Row([
                    self.f_gold,
                    self.lock(ft.ElevatedButton("增加金币", on_click=self._add_gold)),
                    self.lock(ft.ElevatedButton("金币补满", on_click=self._fill_gold)),
                    self.lock(ft.ElevatedButton("水晶币补满", on_click=self._fill_shop)),
                ], wrap=True),
                ft.Row([self.f_exp, self.lock(ft.ElevatedButton("增加经验", on_click=self._add_exp))], wrap=True),
                ft.Row([self.f_level, self.lock(ft.ElevatedButton("设置等级", on_click=self._set_level))], wrap=True),
                ft.Row([self.f_newname, self.lock(ft.ElevatedButton("修改姓名", on_click=self._rename))], wrap=True),
                ft.Row([
                    self.d_camp, self.lock(ft.ElevatedButton("设置阵营", on_click=self._set_camp)),
                    self.d_sex, self.lock(ft.ElevatedButton("设置性别", on_click=self._set_sex)),
                ], wrap=True),
                ft.Row([
                    self.lock(ft.ElevatedButton("解决卡团", on_click=self._reset_clan)),
                    self.f_transfer,
                    self.lock(ft.ElevatedButton("角色转移", on_click=self._transfer)),
                    self.lock(ft.FilledButton("删除角色", icon=ft.icons.DELETE,
                              style=ft.ButtonStyle(bgcolor=ft.colors.RED_400),
                              on_click=self._delete_char)),
                ], wrap=True),
            ],
            spacing=10, scroll=ft.ScrollMode.AUTO,
        )
        return self._pad(col)

    def _bind_name(self, _=None) -> None:
        name = (self.f_bind_name.value or "").strip()
        if not name:
            self.notify("请输入角色名！", error=True)
            return
        if self.run(lambda: self._store_bound(character.bind_by_name(self.conn, name))):
            self.notify("绑定成功！")

    def _bind_id(self, _=None) -> None:
        aid = self._int(self.f_bind_id, "角色ID")
        if aid is None:
            return
        if self.run(lambda: self._store_bound(character.bind_by_id(self.conn, aid))):
            self.notify("绑定成功！")

    def _store_bound(self, stats: dict) -> None:
        self.bound = stats
        self.bound_label.value = (
            f"已绑定：{stats.get('ActorName')} (ID {stats.get('ActorID')})"
        )
        self.page.update()

    def _refresh_bound(self) -> None:
        if self.bound is not None:
            self.bound = character.bind_by_id(self.conn, self.bound["ActorID"])
            self._store_bound(self.bound)

    def _name(self) -> str:
        return self.bound["ActorName"]

    def _add_point(self, _=None) -> None:
        if not self.require_bound():
            return
        amt = self._int(self.f_point, "点数增量")
        if amt is None:
            return
        if self.run(lambda: character.add_points(self.conn, self._name(), amt), "点数已更新"):
            self._refresh_bound()

    def _add_gold(self, _=None) -> None:
        if not self.require_bound():
            return
        amt = self._int(self.f_gold, "金币增量")
        if amt is None:
            return
        if self.run(lambda: character.add_gold(self.conn, self._name(), amt), "金币已更新"):
            self._refresh_bound()

    def _fill_gold(self, _=None) -> None:
        if not self.require_bound():
            return
        if self.run(lambda: character.fill_gold(self.conn, self._name()), "金币已补满"):
            self._refresh_bound()

    def _fill_shop(self, _=None) -> None:
        if not self.require_bound():
            return
        if self.run(lambda: character.fill_shopping(self.conn, self._name()), "水晶币已补满"):
            self._refresh_bound()

    def _add_exp(self, _=None) -> None:
        if not self.require_bound():
            return
        amt = self._int(self.f_exp, "经验增量")
        if amt is None:
            return
        if self.run(lambda: character.add_exp(self.conn, self._name(), amt), "经验已更新"):
            self._refresh_bound()

    def _set_level(self, _=None) -> None:
        if not self.require_bound():
            return
        lvl = self._int(self.f_level, "等级")
        if lvl is None:
            return
        if self.run(lambda: character.set_level(self.conn, self._name(), lvl), "等级已设置"):
            self._refresh_bound()

    def _rename(self, _=None) -> None:
        if not self.require_bound():
            return
        new = (self.f_newname.value or "").strip()
        if not new:
            self.notify("请输入新角色名！", error=True)
            return
        if self.run(lambda: character.rename(self.conn, self._name(), new), "改名成功"):
            self._refresh_bound()

    def _set_camp(self, _=None) -> None:
        if not self.require_bound():
            return
        if self.run(lambda: character.set_camp(self.conn, self._name(), int(self.d_camp.value)), "阵营已设置"):
            self._refresh_bound()

    def _set_sex(self, _=None) -> None:
        if not self.require_bound():
            return
        if self.run(lambda: character.set_sex(self.conn, self._name(), int(self.d_sex.value)), "性别已设置"):
            self._refresh_bound()

    def _reset_clan(self, _=None) -> None:
        if not self.require_bound():
            return
        if self.run(lambda: character.reset_clan(self.conn, self._name()), "已解决卡团"):
            self._refresh_bound()

    def _transfer(self, _=None) -> None:
        if not self.require_bound():
            return
        target = (self.f_transfer.value or "").strip()
        if not target:
            self.notify("请输入目标账号！", error=True)
            return
        self.run(
            lambda: character.transfer(
                self.conn, area=(self.f_area.value or "").strip(),
                actor_id=self.bound["ActorID"], target_account=target,
            ),
            "角色已转移",
        )

    def _delete_char(self, _=None) -> None:
        if not self.require_bound():
            return
        name = self._name()
        if self.run(lambda: character.delete_character(self.conn, name), "角色已删除"):
            self.bound = None
            self.bound_label.value = "未绑定角色"
            self.page.update()

    # -------- inventory tab
    def _tab_inventory(self) -> ft.Control:
        self.d_preset = ft.Dropdown(
            label="职业套装", width=220,
            options=[ft.dropdown.Option(k, label) for k, label in inventory.presets()],
        )
        col = ft.Column(
            [
                ft.Text("对已绑定角色操作背包", weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.d_preset,
                    self.lock(ft.FilledButton("应用套装", on_click=self._apply_preset)),
                ], wrap=True),
                ft.Divider(),
                ft.Row([
                    self.lock(ft.ElevatedButton("复制装备", icon=ft.icons.COPY, on_click=self._copy_eq)),
                    self.lock(ft.ElevatedButton("粘贴装备", icon=ft.icons.PASTE, on_click=self._paste_eq)),
                ], wrap=True),
            ],
            spacing=10,
        )
        return self._pad(col)

    def _apply_preset(self, _=None) -> None:
        if not self.require_bound():
            return
        key = self.d_preset.value
        if not key:
            self.notify("请选择套装！", error=True)
            return
        self.run(
            lambda: inventory.apply_preset(self.conn, self.bound["ActorID"], key),
            "套装已应用",
        )

    def _copy_eq(self, _=None) -> None:
        if not self.require_bound():
            return

        def do():
            self.clip = inventory.copy_equipment(self.conn, self.bound["ActorID"])

        if self.run(do, "装备已复制"):
            pass

    def _paste_eq(self, _=None) -> None:
        if not self.require_bound():
            return
        self.run(
            lambda: inventory.paste_equipment(self.conn, self.bound["ActorID"], self.clip),
            "装备已粘贴",
        )

    # -------- clan tab
    def _tab_clan(self) -> ft.Control:
        self.f_clan = ft.TextField(label="兵团名称", width=220)
        col = ft.Column(
            [
                ft.Row([
                    self.f_clan,
                    self.lock(ft.FilledButton("兵团补满", on_click=self._clan_max)),
                    self.lock(ft.FilledButton("删除兵团", icon=ft.icons.DELETE,
                              style=ft.ButtonStyle(bgcolor=ft.colors.RED_400),
                              on_click=self._clan_delete)),
                ], wrap=True),
            ],
            spacing=10,
        )
        return self._pad(col)

    def _clan_max(self, _=None) -> None:
        name = (self.f_clan.value or "").strip()
        if not name:
            self.notify("请输入兵团名称！", error=True)
            return
        self.run(lambda: self._clan_max_check(clan.max_out(self.conn, name)), None)

    def _clan_max_check(self, affected: int) -> None:
        if affected == 0:
            raise DatabaseError("找不到该兵团！")
        self.notify("兵团已补满")

    def _clan_delete(self, _=None) -> None:
        name = (self.f_clan.value or "").strip()
        if not name:
            self.notify("请输入兵团名称！", error=True)
            return
        self.run(lambda: clan.delete_clan(self.conn, name), "兵团已删除")

    # -------- account tab
    def _tab_account(self) -> ft.Control:
        self.f_new_user = ft.TextField(label="账号", width=200)
        self.f_new_pwd = ft.TextField(label="密码", password=True, can_reveal_password=True, width=200)
        self.f_set_user = ft.TextField(label="账号", width=200)
        self.f_set_pwd = ft.TextField(label="新密码", password=True, can_reveal_password=True, width=200)
        col = ft.Column(
            [
                ft.Text("创建账号", weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.f_new_user, self.f_new_pwd,
                    self.lock(ft.FilledButton("创建账号", on_click=self._create_acc)),
                ], wrap=True),
                ft.Divider(),
                ft.Text("修改密码", weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.f_set_user, self.f_set_pwd,
                    self.lock(ft.FilledButton("改密码", on_click=self._change_pwd)),
                ], wrap=True),
            ],
            spacing=10,
        )
        return self._pad(col)

    def _create_acc(self, _=None) -> None:
        user = (self.f_new_user.value or "").strip()
        pwd = (self.f_new_pwd.value or "").strip()
        if not user or not pwd:
            self.notify("账号或密码不能为空！", error=True)
            return
        self.run(
            lambda: account.create_account(
                self.conn, area=(self.f_area.value or "").strip(),
                user_name=user, password=pwd,
            ),
            "账号已创建",
        )

    def _change_pwd(self, _=None) -> None:
        user = (self.f_set_user.value or "").strip()
        pwd = (self.f_set_pwd.value or "").strip()
        if not user or not pwd:
            self.notify("账号或密码不能为空！", error=True)
            return
        self.run(
            lambda: account.change_password(
                self.conn, area=(self.f_area.value or "").strip(),
                user_name=user, password=pwd,
            ),
            "密码已修改",
        )

    # -------- info tab
    def _tab_info(self) -> ft.Control:
        self.info_view = ft.Column(spacing=6)
        col = ft.Column(
            [
                ft.Row([self.lock(ft.FilledButton("刷新信息", icon=ft.icons.REFRESH, on_click=self._refresh_info))]),
                ft.Divider(),
                self.info_view,
            ],
            spacing=10,
        )
        return self._pad(col)

    def _refresh_info(self, _=None) -> None:
        if not self.require_bound():
            return
        self._refresh_bound()
        data = character.summary(self.bound)
        self.info_view.controls = [
            ft.Row([ft.Text(f"{k}：", weight=ft.FontWeight.BOLD, width=80), ft.Text(str(v))])
            for k, v in data.items()
        ]
        self.page.update()


def main(page: ft.Page) -> None:
    App(page)
