# BKGUtils
# A cross-platform module with several random utilities to manage background.

import os
import sys
import tkinter as tk
import importlib

__version__ = "0.0.1"


def getScreenSize():
    root = tk.Tk()
    root.withdraw()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return w, h


def get_wm():
    # https://stackoverflow.com/questions/3333243/how-can-i-check-with-python-which-window-manager-is-running
    return os.environ.get('XDG_CURRENT_DESKTOP', "")


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


if sys.platform == "darwin":
    from ._bkgutils_macos import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        enable_activedesktop,
        toggleDesktopIcons,
        getWorkArea,
        getAttributes
    )

elif sys.platform == "win32":
    from ._bkgutils_win import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        enable_activedesktop,
        toggleDesktopIcons,
        getWorkArea,
        getAttributes
    )

elif sys.platform == "linux":
    from ._bkgutils_linux import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        enable_activedesktop,
        toggleDesktopIcons,
        getWorkArea,
        getAttributes
    )

else:
    raise NotImplementedError('BkgUtils currently does not support this platform. If you think you can help, please contribute! https://github.com/Kalmat/')
