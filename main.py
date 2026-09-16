"""英雄岛数据库管理工具 - 入口。"""

import sys

import flet as ft

from sqlmanager.ui.app import main


def _silence_proactor_shutdown_noise() -> None:
    """抑制 Windows 上关闭时的无害报错：
    ``RuntimeError: Event loop is closed`` —— Proactor 事件循环的
    StreamWriter.__del__ 在解释器退出、循环已关闭后触发，属已知的 Flet/asyncio
    行为，不影响功能。
    """
    if not sys.platform.startswith("win"):
        return
    import functools
    from asyncio.proactor_events import _ProactorBasePipeTransport

    original = _ProactorBasePipeTransport.__del__

    @functools.wraps(original)
    def _quiet_del(self, *args, **kwargs):
        try:
            original(self, *args, **kwargs)
        except RuntimeError as exc:
            if str(exc) != "Event loop is closed":
                raise

    _ProactorBasePipeTransport.__del__ = _quiet_del


if __name__ == "__main__":
    _silence_proactor_shutdown_noise()
    ft.app(target=main)
