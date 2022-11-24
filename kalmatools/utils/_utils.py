#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import queue
import subprocess
import sys
from typing import Callable, Any

import playsound
import plyer
import pywinctl
import threading
import time

__version__ = "0.0.1"


def resource_path(file, rel_path):
    """ Thanks to: detly < https://stackoverflow.com/questions/4416336/adding-a-program-icon-in-python-gtk/4416367 > """
    dir_of_py_file = os.path.dirname(file)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    if os.path.isdir(abs_path_to_resource) and abs_path_to_resource[-1:] != os.path.sep:
        abs_path_to_resource += os.path.sep
    return abs_path_to_resource


class Timer:

    SNOOZE = 0
    ONEOFF = 1

    def __init__(self, timerType=SNOOZE):

        self._obj = self._Counter()
        self._keep = threading.Event()
        self._timerType = timerType
        self._msec = 0
        self._thread = None
        self._function = None

    class _Counter:

        def __init__(self):
            super().__init__()
            self._Qmsec = queue.Queue()
            self._Qcallback = queue.Queue()

        def run(self, keep_event: threading.Event(), msec: int, callback: Callable[[], Any], oneoffType) -> None:
            while True:
                keep_event.wait()
                if not self._Qmsec.empty():
                    msec = self._Qmsec.get()
                endTime = round(time.time() * 1000) + msec
                while round(time.time() * 1000) < endTime and keep_event.is_set():
                    time.sleep(0.001)
                if keep_event.is_set():
                    keep_event.clear()
                    if not self._Qcallback.empty():
                        callback = self._Qcallback.get()
                    callback()
                    if oneoffType:
                        break

    def start(self, msec: int, callback: Callable[[], Any], start_now=False) -> None:
        if msec > 0:
            self._msec = msec
            self._function = callback
            if self._timerType == self.SNOOZE and start_now:
                self._function()
            if not self._thread:
                self._keep.set()
                self._thread = threading.Thread(target=self._obj.run, args=(self._keep, self._msec, self._callback, self._timerType == self.ONEOFF))
                self._thread.setDaemon(True)
                self._thread.start()
            else:
                self._obj._Qmsec.put(self._msec)
                self._obj._Qcallback.put(self._callback)
                self._keep.set()

    def _callback(self):
        self._function()
        if self._timerType == self.SNOOZE:
            self.start(self._msec, self._function)
        else:
            self._thread = None

    def stop(self) -> None:
        self._keep.clear()
        if self._timerType == self.ONEOFF:
            self._thread.join()
            self._thread = None

    def isAlive(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and self._keep.is_set()
    is_alive = isAlive


def get_CPU_temp(archOS):
    # Will only work on Linux OS
    temp = "n/a"
    if "arm" in archOS or "Linux" in archOS:
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline().replace(os.linesep, "")
        if res.isdigit():
            temp = str(round(float(res) / 1000, 1)) + "º"

    return temp


def get_CPU_usage(archOS):
    # Will only work on Linux OS
    usage = "n/a"
    if "arm" in archOS or "Linux" in archOS:
        usage = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2+$4}'").readline().strip() + "%"

    return usage


def notify(message, sound, icon, title='Warning'):
    if message is not None:
        plyer.notification.notify(
            title=title,
            message=message,
            app_icon=icon,
            timeout=5,
        )

    if sound is not None:
        playsound.playsound(sound)


def load_font(archOS, fontpath, private=True, enumerable=False):
    '''
    Makes fonts located in file `fontpath` available to the font system.
    `private`     if True, other processes cannot see this font, and this
                  font will be unloaded when the process dies
    `enumerable`  if True, this font will appear when enumerating fonts
    See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx
    '''
    # This function was taken from
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15

    if "Windows" in archOS:
        from ctypes import windll, byref, create_string_buffer

        FR_PRIVATE = 0x10
        FR_NOT_ENUM = 0x20

        pathbuf = create_string_buffer(fontpath.encode())
        AddFontResourceEx = windll.gdi32.AddFontResourceExA

        flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
        numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
        return bool(numFontsAdded)
    else:
        from fontTools.ttLib import TTFont
        try:
            TTFont(fontpath)
            return True
        except:
            return False


def win_run_as_admin(argv=None, debug=False, force_admin=True):
    # https://stackoverflow.com/questions/19672352/how-to-run-python-script-with-elevated-privilege-on-windows (Gary Lee)

    from ctypes import windll
    shell32 = windll.shell32

    if argv is None and shell32.IsUserAnAdmin():
        # Already running as admin
        return True

    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = argv[1:]
    else:
        arguments = argv
    argument_line = u' '.join(arguments)
    executable = sys.executable
    if debug:
        print('Command line: ', executable, argument_line)
    console_mode = 0
    if debug:
        console_mode = 1
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, console_mode)
    if int(ret) <= 32:
        # Not possible to gain admin privileges
        if not force_admin:
            argument_line = "not_admin " + argument_line
            shell32.ShellExecuteW(None, u"open", executable, argument_line, None, console_mode)
        return False

    # Gaining admin privileges in process
    return None


def linux_run_as_admin():
    euid = os.geteuid()
    if euid != 0:
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)


def get_screen_pos(name=None):
    # Position doesn't take into account border width and title bar height
    try:
        import pywinctl

        win = None
        if not name:
            win = pywinctl.getActiveWindow()
        else:
            windows = pywinctl.getWindowsWithTitle(name)
            if windows:
                win = windows[0]
        if win:
            return win.left, win.top, win.width, win.height
    except:
        return None, None, 0, 0

    return None, None, 0, 0


def win_get_screen_pos(hwnd=None, add_decoration=False):
    # https: // stackoverflow.com / questions / 4135928 / pygame - display - position?rq = 1  (Alexandre Willame)

    from ctypes import POINTER, WINFUNCTYPE, windll
    from ctypes.wintypes import BOOL, HWND, RECT

    # get our window ID
    if not hwnd:
        # pygame example:
        # hwnd = pygame.display.get_wm_info()["window"]
        hwnd = windll.user32.GetForegroundWindow()

    # Jump through all the ctypes hoops:
    prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
    paramflags = (1, "hwnd"), (2, "lprect")

    GetWindowRect = prototype(("GetWindowRect", windll.user32), paramflags)

    # finally get our data!
    rect = GetWindowRect(hwnd)

    # This can be used to adjust the position if needed:
    titlebar_height = 0
    border_width = 0
    if add_decoration:
        try:  # >= win 8.1
            windll.shcore.SetProcessDpiAwareness(2)
        except:  # win 8.0 or less
            windll.user32.SetProcessDPIAware()
        titlebar_height = windll.user32.GetSystemMetrics(4)
        border_width = windll.user32.GetSystemMetrics(5)

    # Return x, y, width, height
    return rect.left - border_width, rect.top - titlebar_height, rect.right - rect.left, rect.bottom - rect.top


def linux_get_screen_pos():
    # https://stackoverflow.com/questions/12775136/get-window-position-and-size-in-python-with-xlib (mgalgs)

    import Xlib.display

    disp = Xlib.display.Display()
    root = disp.screen().root
    win_id = root.get_full_property(disp.intern_atom('_NET_ACTIVE_WINDOW'), Xlib.X.AnyPropertyType).value[0]
    try:
        win = disp.create_resource_object('window', win_id)
    except Xlib.error.XError:
        win = None

    """
    Returns the (x, y, height, width) of a window relative to the top-left
    of the screen.
    """
    if win is not None:
        geom = win.get_geometry()
        (x, y) = (geom._x, geom._y)
        while True:
            parent = win.query_tree()._parent
            pgeom = parent.get_geometry()
            x += pgeom._x
            y += pgeom._y
            if parent.id == root.id:
                break
            win = parent
        return x, y, geom.width, geom.height
    else:
        return None, None, 0, 0


def subprocess_args(include_stdout=True):
    # https: // github.com / pyinstaller / pyinstaller / wiki / Recipe - subprocess (by twisted)
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret


def wrap_text(text, font, width):
    # ColdrickSotK
    # https://github.com/ColdrickSotK/yamlui/blob/master/yamlui/util.py#L82-L143
    """Wrap text to fit inside a given width when rendered.
    :param text: The text to be wrapped.
    :param font: The font the text will be rendered in.
    :param width: The width to wrap to."""

    text_lines = text.replace('\t', '    ').split('\n')
    if width is None or width == 0:
        return text_lines

    wrapped_lines = []
    for line in text_lines:
        line = line.rstrip() + ' '
        if line == ' ':
            wrapped_lines.append(line)
            continue

        # Get the leftmost space ignoring leading whitespace
        start = len(line) - len(line.lstrip())
        start = line.index(' ', start)
        while start + 1 < len(line):
            # Get the next potential splitting point
            next = line.index(' ', start + 1)
            if font.size(line[:next])[0] <= width:
                start = next
            else:
                wrapped_lines.append(line[:start])
                line = line[start + 1:]
                start = line.index(' ')
        line = line[:-1]
        if line:
            wrapped_lines.append(line)

    return wrapped_lines


def to_float(s, dec=1):
    num = ''.join(n for n in str(s) if n.isdigit() or n == "." or n == "-")
    try:
        return round(float(num), dec)
    except Exception:
        return 0.0


def getFilesInFolder(folder, extensions):
    try:
        files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]
        fileList = []
        for file in files:
            if not extensions or file.split(".")[-1].lower() in extensions:
                fileList.append(os.path.join(folder, file))
    except:
        fileList = []
    return fileList


def checkInstances(name):
    instances = 0
    for win in pywinctl.getWindowsWithTitle(name):
        if ".py" not in win.title:
            instances += 1
    return instances > 1
