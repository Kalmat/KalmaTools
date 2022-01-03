# BKGUtils
# A cross-platform module with several random utilities to manage background.

import sys

__version__ = "0.0.1"


if sys.platform == "darwin":
    from ._bkgutils_macos import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        getWorkArea,
        get_wm,
        getWMAdjustments
    )

elif sys.platform == "win32":
    from ._bkgutils_win import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        refreshDesktop,
        force_refresh,
        enable_activedesktop,
        toggleDesktopIcons,
        getWorkArea,
        get_wm,
        getWMAdjustments
    )

elif sys.platform == "linux":
    from ._bkgutils_linux import (
        sendBehind,
        sendFront,
        getWallpaper,
        setWallpaper,
        getWorkArea,
        getAttributes,
        get_wm,
        getWMAdjustments
    )

else:
    raise NotImplementedError('BkgUtils currently does not support this platform. If you think you can help, please contribute! https://github.com/Kalmat/')

