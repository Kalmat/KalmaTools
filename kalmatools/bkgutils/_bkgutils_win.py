#!/usr/bin/python
# -*- coding: utf-8 -*-

import ctypes
from typing import List

import win32api
import win32con
import win32gui


def findWindowHandles(parent: int = None, window_class: str = None, title: str = None, onlyVisible: bool = False) -> List[int]:
    # https://stackoverflow.com/questions/56973912/how-can-i-set-windows-10-desktop-background-with-smooth-transition
    # Fixed: original post returned duplicated handles when trying to retrieve all windows (no class nor title)

    def _make_filter(class_name: str, title: str, onlyVisible=False):

        def enum_windows(handle: int, h_list: list):
            if class_name and class_name not in win32gui.GetClassName(handle):
                return True  # continue enumeration
            if title and title not in win32gui.GetWindowText(handle):
                return True  # continue enumeration
            if not onlyVisible or (onlyVisible and win32gui.IsWindowVisible(handle)):
                h_list.append(handle)

        return enum_windows

    cb = _make_filter(window_class, title, onlyVisible)
    try:
        handle_list = []
        if parent:
            win32gui.EnumChildWindows(parent, cb, handle_list)
        else:
            win32gui.EnumWindows(cb, handle_list)
        return handle_list
    except:
        return []


def findWindowHandle(title):
    return win32gui.FindWindowEx(0, 0, None, title)


def getWallpaper():
    wp = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER, 260, 0)
    return wp


def setWallpaper(img=""):
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, img,
                                  win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE)


def enable_activedesktop():
    # https://stackoverflow.com/a/16351170
    try:
        progman = findWindowHandles(window_class='Progman')[0]
        cryptic_params = (0x52c, 0, 0, 0, 500, None)
        ctypes.windll.user32.SendMessageTimeoutW(progman, *cryptic_params)
    except IndexError as e:
        raise WindowsError('Cannot enable Active Desktop') from e


def refreshDesktop():
    # https://newbedev.com/how-to-refresh-reload-desktop

    hWnd = win32gui.GetWindow(win32gui.FindWindow("Progman", "Program Manager"), win32con.GW_CHILD)
    if not hWnd:
        ptrs = findWindowHandles(window_class="WorkerW")
        for i in range(len(ptrs)):
            hWnd = win32gui.FindWindowEx(ptrs[i], 0, "SHELLDLL_DefView", "")
    if hWnd:
        win32gui.SendMessage(hWnd, 0x111, 0x7402, 0)


def refreshDesktopB():
    win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 1)


def force_refresh():
    ctypes.windll.user32.UpdatePerUserSystemParameters(1)


def toggleDesktopIcons():
    thelist = []

    def findit(hwnd, ctx):
        p = win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", "")
        if p != 0:
            thelist.append(p)

    win32gui.EnumWindows(findit, None)
    if thelist:
        win32gui.SendMessage(thelist[0], 0x111, 0x7402, 0)


def getScreenSize():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def getWorkArea():
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
    work_area = monitor_info.get("Work")
    return work_area[0], work_area[1], work_area[2], work_area[3]


def getAttributes(hWnd):
    raise NotImplementedError
