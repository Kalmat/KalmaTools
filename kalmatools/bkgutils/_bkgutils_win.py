#!/usr/bin/python
# -*- coding: utf-8 -*-

import ctypes
import os
from typing import List

import pywintypes
import win32api
import win32con
import win32gui


def findWindowHandles(parent: int = None, window_class: str = None, title: str = None) -> List[int]:
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

    # https://www.codeproject.com/Articles/856020/Draw-Behind-Desktop-Icons-in-Windows-plus
    workerw = getWorkerW()
    if not workerw:
        progman = win32gui.FindWindow("Progman", None)
        win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
        workerw = getWorkerW()
    hWnd = findWindowHandle(name)
    ret = False
    if hWnd and workerw:
        win32gui.SetParent(hWnd, workerw[0])
        ret = True
    return ret


def sendFront(hWnd=None, name=""):
    if not hWnd and name:
        hWnd = findWindowHandle(name)
    if hWnd:
        win32gui.ShowWindow(hWnd, win32con.SW_SHOW)
        win32gui.BringWindowToTop(hWnd)
        win32gui.SetForegroundWindow(hWnd)


def getWallpaper():
    wp = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER, 260, 0)
    return wp


def setWallpaper(img=""):
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, img,
                                  win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE)


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

