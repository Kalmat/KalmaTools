#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from typing import List
import ctypes
import pywintypes
import win32con
import win32gui
import win32api


def findWindowHandlesB(parent: int = None, window_class: str = None, title: str = None) -> List[int]:
    # https://stackoverflow.com/questions/56973912/how-can-i-set-windows-10-desktop-background-with-smooth-transition

    def _make_filter(class_name: str, title: str):
        """https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows"""

        def enum_windows(handle: int, h_list: list):
            if not (class_name or title):
                h_list.append(handle)
            if class_name and class_name not in win32gui.GetClassName(handle):
                return True  # continue enumeration
            if title and title not in win32gui.GetWindowText(handle):
                return True  # continue enumeration
            h_list.append(handle)

        return enum_windows

    cb = _make_filter(window_class, title)
    try:
        handle_list = []
        if parent:
            win32gui.EnumChildWindows(parent, cb, handle_list)
        else:
            win32gui.EnumWindows(cb, handle_list)
        return handle_list
    except pywintypes.error:
        return []


def findWindowHandles(parent: int = None, window_class: str = None, title: str = None) -> List[int]:
    # https://stackoverflow.com/questions/61151811/how-to-get-handle-for-a-specific-application-window-in-python-using-pywin32
    # WARNING: Crashes when using QtWebEngineWidgets!!!!
    thelist = []

    def findit(hwnd, ctx):
        if (not parent or (parent and parent == win32gui.GetParent(hwnd))) and \
                (not window_class or (window_class and window_class == win32gui.GetClassName(hwnd))) and \
                (not title or (title and title == win32gui.GetWindowText(hwnd))):
            thelist.append(hwnd)

    win32gui.EnumWindows(findit, None)
    return thelist


def findWindowHandle(title):
    return win32gui.FindWindowEx(0, 0, None, title)


def sendBehind(name):
    def getWorkerW():

        thelist = []

        def findit(hwnd, ctx):
            p = win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", "")
            if p != 0:
                thelist.append(win32gui.FindWindowEx(None, hwnd, "WorkerW", ""))

        win32gui.EnumWindows(findit, None)
        return thelist

    def getWinHandle(title):

        thelist = []

        def findit(hwnd, ctx):

            thelist = []

            if win32gui.GetWindowText(hwnd) == title:
                thelist.append(hwnd)

        win32gui.EnumWindows(findit, None)
        return thelist[0] if thelist else 0

    # https://www.codeproject.com/Articles/856020/Draw-Behind-Desktop-Icons-in-Windows-plus
    workerw = getWorkerW()
    if not workerw:
        progman = win32gui.FindWindow("Progman", None)
        win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
        workerw = getWorkerW()
    # hWnd = getWinHandle(name)
    hWnd = findWindowHandle(name)
    ret = False
    if hWnd and workerw:
        win32gui.SetParent(hWnd, workerw[0])
        ret = True
    return ret


def sendFront(name, parent):
    hWnd = findWindowHandle(name)
    win32gui.SetParent(hWnd, parent)


def getWallpaper():
    wp = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER, 260, 0)
    return wp


def setWallpaper(img=""):
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, img,
                                  win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE)


def closeWindow(hWnd):
    win32gui.PostMessage(hWnd, win32con.WM_CLOSE, 0, 0)


def clearWindow(hWnd):
    win32gui.PostMessage(hWnd, win32con.WM_CLEAR, 0, 0)


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


def enable_activedesktop():
    """https://stackoverflow.com/a/16351170"""
    try:
        progman = findWindowHandles(window_class='Progman')[0]
        cryptic_params = (0x52c, 0, 0, 0, 500, None)
        ctypes.windll.user32.SendMessageTimeoutW(progman, *cryptic_params)
    except IndexError as e:
        raise WindowsError('Cannot enable Active Desktop') from e


def toggleDesktopIcons():
    thelist = []

    def findit(hwnd, ctx):
        p = win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", "")
        if p != 0:
            thelist.append(p)

    win32gui.EnumWindows(findit, None)
    if thelist:
        win32gui.SendMessage(thelist[0], 0x111, 0x7402, 0)


def getWorkArea():
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
    work_area = monitor_info.get("Work")
    return work_area[0], work_area[1], work_area[2], work_area[3]


def get_wm():
    # https://stackoverflow.com/questions/3333243/how-can-i-check-with-python-which-window-manager-is-running
    return os.environ.get('XDG_CURRENT_DESKTOP') or ""


def getWMAdjustments(is_macos, line_width):
    wm = get_wm()
    if "GNOME" in wm:
        # PyQt5 geometry is not correct in Ubuntu/GNOME?!?!?!
        xAdj = 0
        yAdj = 0
        xGap = line_width * 6
        yGap = 0
        wGap = line_width * 6
        hGap = line_width * 7
    elif "Cinnamon" in wm:
        # Mouse position does not fit windowsAt coordinates in Cinnamon
        xAdj = 0
        yAdj = 20
        xGap = 0
        yGap = line_width * 3
        wGap = 0
        hGap = - line_width * 3
    elif is_macos:
        xAdj = 0
        yAdj = 0
        xGap = 0
        yGap = line_width * 3
        wGap = 0
        hGap = 0
    else:
        xAdj = 0
        yAdj = 0
        xGap = - line_width
        yGap = 0
        wGap = line_width * 2
        hGap = line_width

    return xAdj, yAdj, xGap, yGap, wGap, hGap

