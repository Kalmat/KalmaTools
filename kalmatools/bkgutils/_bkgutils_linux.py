#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
import ctypes

import Xlib
import Xlib.X
import Xlib.display
import ewmh
from pynput import mouse

DISP = Xlib.display.Display()
SCREEN = DISP.screen()
ROOT = SCREEN.root
EWMH = ewmh.EWMH(_display=DISP, root=ROOT)


def findAllWindowHandles(parent=None, window_class="", title=""):

    def getAllWindows(parent=None):
        if not parent:
            parent = ROOT
        windows = parent.query_tree().children
        return windows

    def getWindowsWithTitle(parent=None, window_class="", title=""):
        matches = []
        for win in getAllWindows(parent):
            w = DISP.create_resource_object('window', win)
            if title and title == w.get_wm_name() or \
                    window_class and window_class == w.get_wm_class():
                matches.append(win)
        return matches

    if title:
        windows = getWindowsWithTitle(parent=parent, title=title)
    else:
        windows = getAllWindows(parent=parent)
    return windows


def findWindowHandle(title):
    return findAllWindowHandles(title=title)


def sendBehind(name):
    # Mint/Cinnamon: just clicking on the desktop, it comes up, sending the window/wallpaper to bottom!
    m = mouse.Controller()
    m.click(SCREEN.width_in_pixels - 1, 300, 1)

    # Non-working attempts for Ubuntu/GNOME using Xlib
    # win = findWindowHandles(title=name)
    # if win:
    #     win = win[0]
    #     w = DISP.create_resource_object('window', win)
    #
    #     https://stackoverflow.com/questions/58885803/can-i-use-net-wm-window-type-dock-ewhm-extension-in-openbox
    #     Does not sends current window below. It does with the new window, but not behind the desktop icons
    #     w.change_property(DISP.intern_atom('_NET_WM_WINDOW_TYPE'), Xlib.Xatom.ATOM,
    #                       32, [DISP.intern_atom("_NET_WM_WINDOW_TYPE_DESKTOP"), ],
    #                       Xlib.X.PropModeReplace)
    #     w.map()
    #
    #     newWin = ROOT.create_window(0, 0, 500, 500, 1, SCREEN.root_depth,
    #                                 background_pixel=SCREEN.black_pixel,
    #                                 event_mask=Xlib.X.ExposureMask | Xlib.X.KeyPressMask)
    #     newWin.change_property(DISP.intern_atom('_NET_WM_WINDOW_TYPE'), Xlib.Xatom.ATOM,
    #                            32, [DISP.intern_atom("_NET_WM_WINDOW_TYPE_DESKTOP"), ],
    #                            Xlib.X.PropModeReplace)
    #     newWin.map()
    #     w.reparent(newWin, 0, 0)


def x11SendBehind(name):
    # Non-working attempts for Ubuntu/GNOME directly using x11 library (Xlib does not have XLowerWindow()???)
    x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
    # m_display = x11.XOpenDisplay(None)
    m_display = x11.XOpenDisplay(bytes(os.environ["DISPLAY"], 'ascii'))
    if m_display == 0: return
    m_root_win = x11.XDefaultRootWindow(m_display, ctypes.c_int(0))

    def x11GetWindowsWithTitle(display, current, name):
        # https://stackoverflow.com/questions/37918260/python3-segfaults-when-using-ctypes-on-xlib-python2-works
        # https://www.unix.com/programming/254680-xlib-search-window-his-name.html
        # https://stackoverflow.com/questions/55173668/xgetwindowproperty-and-ctypes

        winName = ctypes.c_char_p()
        x11.XFetchName(display, current, ctypes.byref(winName))

        retVal = 0
        wName = ""
        if winName.value is not None:
            try:
                wName = winName.value.decode()
            except:
                pass

        if wName == name:
            retVal = current

        else:
            root = ctypes.c_ulong()
            children = ctypes.POINTER(ctypes.c_ulong)()
            parent = ctypes.c_ulong()
            nchildren = ctypes.c_uint()

            x11.XQueryTree(display, current, ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children),
                           ctypes.byref(nchildren))

            for i in range(nchildren.value):
                retVal = x11GetWindowsWithTitle(display, children[i], name)
                if retVal != 0:
                    break

        return retVal

    hwnd = x11GetWindowsWithTitle(m_display, m_root_win, name)
    if hwnd:
        # https://stackoverflow.com/questions/33578144/xlib-push-window-to-the-back-of-the-other-windows
        window_type = x11.XInternAtom(m_display, "_NET_WM_WINDOW_TYPE", False)
        desktop = x11.XInternAtom(m_display, "_NET_WM_WINDOW_TYPE_DESKTOP", False)
        data = (ctypes.c_ubyte * len(str(desktop)))()

        # newWin = x11.XCreateSimpleWindow(m_display, m_root_win, ctypes.c_uint(0), ctypes.c_uint(0), ctypes.c_uint(1920), ctypes.c_uint(1080), ctypes.c_uint(0), ctypes.c_ulong(0), SCREEN.white_pixel)  # SCREEN.white_pixel) # WhitePixel(m_display, DefaultScreen(m_display)))
        # x11.XChangeProperty(m_display, newWin, window_type, Xlib.Xatom.ATOM, ctypes.c_int(32), Xlib.X.PropModeReplace, data, ctypes.c_int(1))
        # x11.XClearWindow(m_display, newWin)
        # x11.XMapWindow(m_display, newWin)

        x11.XChangeProperty(m_display, hwnd, window_type, Xlib.Xatom.ATOM, ctypes.c_int(32), Xlib.X.PropModeReplace, data, ctypes.c_int(1))
        # x11.XClearWindow(m_display, hwnd)
        x11.XMapWindow(m_display, hwnd)
        # x11.XReparentWindow(m_display, hwnd, newWin)

        x11.XLowerWindow(m_display, hwnd)


def sendFront(name, parent):
    win = findAllWindowHandles(title=name)
    w = DISP.create_resource_object('window', win)
    w.reparent(parent, 0, 0)


def getWallpaper():
    cmd = """gsettings get org.gnome.desktop.background picture-uri"""
    try:
        wp = subprocess.check_output(cmd, shell=True).decode(encoding="utf-8").strip()
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


def getWorkArea():
    work_area = EWMH.getWorkArea()
    return work_area[0], work_area[1], work_area[2], work_area[3]


def getAttributes(win):
    return EWMH.getWmWindowType(win, str=True)


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
