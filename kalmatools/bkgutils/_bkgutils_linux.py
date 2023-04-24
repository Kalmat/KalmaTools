#!/usr/bin/python
# -*- coding: utf-8 -*-

import ctypes
import os
import subprocess

import Xlib
import bkgutils
import pywinctl as pwc

DISP = Xlib.display.Display()
SCREEN = DISP.screen()
ROOT = SCREEN.root


def _X11SendBehind(hWnd=None, name="", parent=None):
    # Attempts to send window behind desktop icons and useful commands examples using Xlib and X11 library

    x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
    # m_display = x11.XOpenDisplay(None)
    m_display = x11.XOpenDisplay(bytes(os.environ.get("DISPLAY", ""), 'ascii'))
    if m_display == 0: return
    m_root_win = x11.XDefaultRootWindow(m_display, ctypes.c_int(0))

    # HANDLES
    # prevParent = hWnd.query_tree().parent
    # parent = _X11GetWindowsWithTitle(m_display, m_root_win, "gnome-shell")[-1]
    # hwnd = _X11GetWindowsWithTitle(m_display, m_root_win, name)[0]

    # NAMES
    # winName = ctypes.c_char_p()
    # x11.XFetchName(m_display, parent, ctypes.byref(winName))
    # print(winName.value.decode())

    # GEOMETRY
    # root = ctypes.POINTER(ctypes.c_ulong)()
    # x = ctypes.c_uint()
    # y = ctypes.c_uint()
    # width = ctypes.c_uint()
    # height = ctypes.c_uint()
    # border = ctypes.c_uint()
    # depth = ctypes.c_uint()
    # x11.XGetGeometry(m_display, hWnd, ctypes.byref(root), ctypes.byref(x), ctypes.byref(y), ctypes.byref(width), ctypes.byref(height), ctypes.byref(border), ctypes.byref(depth))

    # TREE
    # root = ctypes.c_ulong()
    # children = ctypes.POINTER(ctypes.c_ulong)()
    # wparent = ctypes.c_ulong()
    # nchildren = ctypes.c_uint()
    # x11.XQueryTree(m_display, hwnd, ctypes.byref(root), ctypes.byref(wparent), ctypes.byref(children), ctypes.byref(nchildren))
    # print("PARENT", wparent.value)

    # REPARENT
    x11.XReparentWindow(m_display, hWnd, parent, ctypes.c_uint(0), ctypes.c_uint(0))
    x11.XFlush(m_display)

    # RAISE
    x11.XRaiseWindow(m_display, hWnd)
    x11.XFlush(m_display)

    # LOWER
    # x11.XLowerWindow(m_display, hWnd)
    # x11.XFlush(m_display)

    # RESTACK
    # windows = [parent, hwnd]
    # cwindows = (ctypes.c_ulong * len(windows))(*windows)
    # x11.XRestackWindows(m_display, cwindows, ctypes.c_int(2))
    # x11.XFlush(m_display)


def _X11GetWindowsWithTitle(display=None, parent=None, name=""):
    # https://stackoverflow.com/questions/37918260/python3-segfaults-when-using-ctypes-on-xlib-python2-works
    # https://www.unix.com/programming/254680-xlib-search-window-his-name.html
    # https://stackoverflow.com/questions/55173668/xgetwindowproperty-and-ctypes
    x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
    if not display:
        # display = x11.XOpenDisplay(None)
        display = x11.XOpenDisplay(bytes(os.environ["DISPLAY"], 'ascii'))
        if display == 0: return []
    if not parent:
        parent = x11.XDefaultRootWindow(display, ctypes.c_int(0))

    def queryTree(hwnd):
        root = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        parent = ctypes.c_ulong()
        nchildren = ctypes.c_uint()
        childrenList = []

        x11.XQueryTree(display, hwnd, ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children), ctypes.byref(nchildren))

        for index in range(nchildren.value):
            childrenList.append(children[index])

        return childrenList

    def getName(hwnd):
        winName = ctypes.c_char_p()
        x11.XFetchName(display, hwnd, ctypes.byref(winName))
        name = ""
        if winName.value is not None:
            name = winName.value.decode()
        return name

    matches = []
    if not name:
        matches = [parent]

    def findit(hwnd):

        children = queryTree(hwnd)
        for child in children:
            if getName(child) == name:
                matches.append(child)
            findit(child)

    findit(parent)
    return matches


def _xlibGetAllWindows(parent=None, title=""):
    # Not using window class (get_wm_class())

    if not parent:
        parent = ROOT
    matches = []
    if not title:
        matches.append(parent)

    def findit(hwnd):
        query = hwnd.query_tree()
        for child in query.children:
            if not title or (title and title == child.get_wm_name()):
                matches.append(child)
            findit(child)

    findit(parent)
    return matches


def getWallpaper():
    cmd = """gsettings get org.gnome.desktop.background picture-uri"""
    try:
        wp = subprocess.check_output(cmd, shell=True).decode(encoding="utf-8").strip().replace("file://", "").replace("'", "")
    except:
        wp = ""
    return wp


def setWallpaper(img=""):
    cmd = """gsettings set org.gnome.desktop.background picture-uri '%s'""" % img
    try:
        subprocess.Popen(cmd, shell=True)
        return True
    except:
        return False


def refreshDesktop():
    wm = bkgutils.get_wm().upper()
    cmd = ""
    if "GNOME" in wm:
        cmd = """killall -3 gnome-shell"""
    elif "CINNAMON" in wm:
        cmd = """cinnamon --replace --display=%s""" % os.environ.get("DISPLAY", None)
    elif "LXDE" in wm:
        cmd = """/etc/init.d/lxdm restart"""
    if cmd:
        try:
            subprocess.Popen(cmd, shell=True)
            return True
        except:
            return False
    else:
        return False


def enable_activedesktop():
    raise NotImplementedError


def toggleDesktopIcons(forceRefresh=False):
    desktopFolder = subprocess.check_output(['xdg-user-dir', 'DESKTOP']).strip().decode()
    if os.path.isfile(desktopFolder+"/.hidden"):
        cmd = """cd %s &&
                 gsettings set org.gnome.shell.extensions.desktop-icons show-trash true &&
                 gsettings set org.gnome.shell.extensions.desktop-icons show-home true &&
                 rm -f .hidden""" % desktopFolder
    else:
        cmd = """cd %s &&
                 gsettings set org.gnome.shell.extensions.desktop-icons show-trash false &&
                 gsettings set org.gnome.shell.extensions.desktop-icons show-home false &&
                 ls > .hidden""" % desktopFolder
    os.system(cmd)
    if forceRefresh:
        refreshDesktop()


def getScreenSize():
    resolution = ROOT.get_geometry()
    return resolution.width, resolution.height


def getWorkArea():
    work_area = pwc.getWorkArea()
    return work_area[0], work_area[1], work_area[2], work_area[3]


def getAttributes(hWnd):
    win = pwc.Window(hWnd)
    return win._win.getWmWindowType(hWnd, str=True)
