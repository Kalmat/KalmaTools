#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform
from typing import Iterable
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtBoundSignal, pyqtSlot, QObject


__version__ = "0.0.1"


def initDisplay(parent, pos=(None, None), size=(None, None), setAsWallpaper=False, fullScreen=False, frameless=False,
                opacity=255, noFocus=False, noResize=False, caption=None, icon=None, hideIcon=False, aot=False, aob=False):

    screenSize = QtWidgets.QApplication.primaryScreen().size()
    flags = 0

    if caption:
        parent.setWindowTitle(caption)
    if (icon and not hideIcon and not setAsWallpaper) or "Linux" in platform.platform():
        # QtCore.Qt.Tool crashes on Linux when re-showing the app
        parent.setWindowIcon(QtGui.QIcon(icon))
        styleFlag = QtCore.Qt.Window
    else:
        styleFlag = QtCore.Qt.Tool

    if setAsWallpaper or fullScreen:
        xmax, ymax = screenSize.width(), screenSize.height()
        if setAsWallpaper:
            noFocus = True
            aot = False
            aob = True
            frameless = True
            parent.setGeometry(0, 0, xmax, ymax)
            if "Linux" in platform.platform():
                # This sends the window to the bottom, hides its icon and skips it from taskbar and pager
                parent.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDesktop, True)
        else:
            parent.showFullScreen()
    else:
        if len(pos) == 2 and pos[0] is not None and pos[1] is not None:
            parent.move(QtCore.QPoint(int(pos[0]), int(pos[1])))
        if len(size) == 2 and size[0] is not None and size[1] is not None:
            xmax, ymax = size
            if noResize:
                parent.setFixedSize(xmax, ymax)
            else:
                parent.setGeometry(parent.x(), parent.y(), xmax, ymax)
        else:
            parent.showFullScreen()
            xmax, ymax = screenSize.width(), screenSize.height()

    if aot:
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
    elif aob:
        pass
        flags = flags | QtCore.Qt.WindowStaysOnBottomHint

    if noFocus:
        parent.setFocusPolicy(QtCore.Qt.NoFocus)
        if "Linux" in platform.platform():
           parent.setAttribute(QtCore.Qt.WA_X11DoNotAcceptFocus, True)
        parent.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        parent.setAttribute(QtCore.Qt.WA_InputMethodTransparent)
        parent.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        flags = flags | QtCore.Qt.WindowDoesNotAcceptFocus

    if opacity == 0:
        parent.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        parent.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        frameless = True    # If window is not frameless, it will not be transparent (!)
    elif opacity != 255:
        parent.setWindowOpacity(opacity)

    if frameless:
        flags = flags | QtCore.Qt.FramelessWindowHint

    if flags:
        parent.setWindowFlags(styleFlag | QtCore.Qt.CustomizeWindowHint | flags)

    return xmax, ymax


def getScreenSize():
    size = QtWidgets.QApplication.primaryScreen().size()
    return size.width(), size.height()


def loadFont(font):
    loadedFont = -1
    fontId = QtGui.QFontDatabase.addApplicationFont(font)
    if fontId >= 0:
        families = QtGui.QFontDatabase.applicationFontFamilies(fontId)
        if len(families) > 0:
            loadedFont = QtGui.QFont(families[0])
    return loadedFont


def sendKeys(parent, char="", qkey=None, modifier=QtCore.Qt.NoModifier, text=None):
    # https://stackoverflow.com/questions/33758820/send-keystrokes-from-unicode-string-pyqt-pyside

    if qkey:
        char = qkey
    elif char:
        char = QtGui.QKeySequence.fromString(char)[0]
    else:
        return

    if not text:
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, char, modifier)
    else:
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, char, modifier, text)
    QtCore.QCoreApplication.sendEvent(parent, event)


def createImgFromText(text, font, bcolor=QtGui.QColor(QtCore.Qt.black), fcolor=QtGui.QColor(QtCore.Qt.white), saveFile=""):
    # https://stackoverflow.com/questions/41904610/how-to-create-a-simple-image-qimage-with-text-and-colors-in-qt-and-save-it-as

    fm = QtGui.QFontMetrics(font)
    width = int(fm.width(text) * 1.06)
    height = fm.height()
    img = QtGui.QImage(QtCore.QSize(width, height), QtGui.QImage.Format_RGB32)
    p = QtGui.QPainter(img)
    p.setBrush(QtGui.QBrush(bcolor))
    p.fillRect(QtCore.QRectF(0, 0, width, height), bcolor)
    p.setPen(QtGui.QPen(fcolor))
    p.setFont(font)
    p.drawText(QtCore.QRectF(0, 0, width, height), text)
    if saveFile:
        img.save(saveFile)
    return img


def resizeImageWithQT(img, width, height, keepAspectRatio=True, expand=True):

    pixmap_resized = QtGui.QPixmap()
    pixmap = QtGui.QPixmap(img)

    if not pixmap.isNull():
        if keepAspectRatio:
            if expand:
                flag = QtCore.Qt.KeepAspectRatioByExpanding
            else:
                flag = QtCore.Qt.KeepAspectRatio
        else:
            flag = QtCore.Qt.IgnoreAspectRatio
        pixmap_resized = pixmap.scaled(int(width), int(height), flag, QtCore.Qt.SmoothTransformation)
    return pixmap_resized


def getColor(styleSheet):
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop[:6] == "color:":
            return prop
    color = QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Normal, QtGui.QPalette.Window))
    return "color:rgba(%i, %i, %i, %i)" % (color.red(), color.green(), color.blue(), color.alpha())


def setColor(styleSheet, RGBcolor):
    newStyleSheet = ""
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop and prop[:6] != "color:":
                newStyleSheet += prop + ";"
    newStyleSheet += "color:" + RGBcolor + ";"
    return newStyleSheet


def setColorAlpha(styleSheet, newAlpha):
    newStyleSheet = ""
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop[:6] == "color:":
            values = prop.split(",")
            values[0] = values[0].replace("rgb(", "rgba(")
            prop = values[0] + "," + values[1] + "," + values[2] + "," + str(newAlpha) + ")"
        if prop:
            newStyleSheet += prop + ";"
    return newStyleSheet


def getBkgColor(styleSheet):
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop[:17] == "background-color:":
            return prop
    color = QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Normal, QtGui.QPalette.WindowText))
    return "background-color:rgba(%i, %i, %i, %i)" % (color.red(), color.green(), color.blue(), color.alpha())


def setBkgColor(styleSheet, RGBcolor):
    newStyleSheet = ""
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop and prop[:17] != "background-color:":
            newStyleSheet += prop + ";"
    newStyleSheet += "background-color:" + RGBcolor + ";"
    return newStyleSheet


def setBkgColorAlpha(styleSheet, newAlpha):
    newStyleSheet = ""
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop[:17] == "background-color:":
            values = prop.split(",")
            values[0] = values[0].replace("rgb(", "rgba(")
            prop = values[0] + "," + values[1] + "," + values[2] + "," + str(newAlpha) + ")"
        if prop:
            newStyleSheet += prop + ";"
    return newStyleSheet


def setStyleSheet(styleSheet, bkgRGBcolor, fontRGBcolor):
    newStyleSheet = "background-color:" + bkgRGBcolor + ";" + "color:" + fontRGBcolor + ";"
    props = styleSheet.replace("\n", "").split(";")
    for prop in props:
        if prop and prop[:17] != "background-color:" and prop[:6] != "color:":
            newStyleSheet += prop + ";"
    return newStyleSheet


def getRGBAfromColorName(name):
    color = QtGui.QColor(name)
    return "rgba(%i, %i, %i, %i)" % (color.red(), color.green(), color.blue(), color.alpha())


def getRGBAfromColorRGB(color):
    colorRGB = color.replace("rgba(", "").replace("rgb(", "").replace(")", ""). split(",")
    r = int(colorRGB[0])
    g = int(colorRGB[1])
    b = int(colorRGB[2])
    if len(colorRGB) > 3:
        a = int(colorRGB[3])
    else:
        a = 255
    return r, g, b, a


def setHTMLStyle(text, color=None, bkgcolor=None, font=None, fontSize=None, align=None, valign=None, strong=False):

    colorHTML = bkgcolorHTML = fontHTML = fontSizeHTML = alignHTML = valignHTML = ""
    if color:
        if "rgb" in color:
            colorRGB = color.replace("rgba(", "").replace("rgb(", "").replace(")", ""). split(",")
            r = "%0.2X" % int(colorRGB[0])
            g = "%0.2X" % int(colorRGB[1])
            b = "%0.2X" % int(colorRGB[2])
            colorHTML = "color:#%s;" % (r+g+b)
        else:
            colorHTML = "color:%s;" % color
    if bkgcolor:
        if "rgb" in bkgcolor:
            bkgcolorRGB = bkgcolor.replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")
            r = "%0.2X" % int(bkgcolorRGB[0])
            g = "%0.2X" % int(bkgcolorRGB[1])
            b = "%0.2X" % int(bkgcolorRGB[2])
            bkgcolorHTML = "background-color:#%s;" % (r + g + b)
        else:
            bkgcolorHTML = "background-color:%s;" % bkgcolor
    if font:
        fontHTML = "font-family:%s;" % font
    if fontSize:
        fontSizeHTML = "font-size:%ipx;" % fontSize
    if align:
        alignHTML = "text-align:%s;" % align
    if valign:
        valignHTML = "vertical-align:%s;" % valign
    marginHTML = "margin-top:-10%;"
    if strong:
        style = "<span style=\"%s%s%s%s%s%s\"><strong>%s</strong></span>" % (colorHTML, bkgcolorHTML, fontHTML, fontSizeHTML, alignHTML, valignHTML, text)
    else:
        style = "<span style=\"%s%s%s%s%s%s%s\">%s</span>" % (marginHTML, bkgcolorHTML, colorHTML, fontHTML, fontSizeHTML, alignHTML, valignHTML, text)
    return style


def getQColorFromRGB(color):
    rgb = color.replace("background-color:", "").replace("color:", "").replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")
    r = int(rgb[0])
    g = int(rgb[1])
    b = int(rgb[2])
    if len(rgb) > 3:
        a = int(rgb[3])
    else:
        a = 255
    return QtGui.QColor(r, g, b, a)


class Marquee(QtWidgets.QLabel):

    def __init__(self, parent=None, font=None, color="white", bkgColor="black", fps=60, direction=QtCore.Qt.RightToLeft):
        super().__init__(parent)
        self._parent = parent
        if font:
            self.setFont(font)
        self._fm = QtGui.QFontMetrics(self.font())
        self._color = color
        self._bkgColor = bkgColor
        self._fps = fps
        self._direction = direction if direction in (QtCore.Qt.RightToLeft, QtCore.Qt.LeftToRight) else QtCore.Qt.RightToLeft

        self._document = None
        self._timer = None
        self._speed = int(1 / self._fps * 1000)
        self._paused = False
        self._initX = 0
        self._x = 0

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.translate)

    def setHtml(self, text):

        self._document = QtGui.QTextDocument(self)
        htmlText = setHTMLStyle(text=text, color=self._color, bkgcolor=self._bkgColor, font=self.font().family(), fontSize=int(self.font().pointSize()*1.5), strong=True)
        self._document.setHtml(htmlText)
        self._document.setTextWidth(self._fm.width(text))
        self._document.setUseDesignMetrics(True)

        self.setDirection(self._direction)

    def start(self):
        if not self._timer.isActive() and self._document.textWidth() > self.width():
            self._paused = False
            self._timer.start(self._speed)

    def paintEvent(self, event):
        if self._document:
            p = QtGui.QPainter(self)
            p.translate(self._x, 0)
            self._document.drawContents(p)
        return super().paintEvent(event)

    @pyqtSlot()
    def translate(self):
        if not self._paused:
            if self._direction == QtCore.Qt.RightToLeft:
                if self.width() - self._x < self._document.textWidth():
                    self._x -= 1
                else:
                    self._x = self._initX
            else:
                if self._x <= self.width():
                    self._x += 1
                else:
                    self._x = self._initX
            self.repaint()

    def event(self, event):
        if event.type() == QtCore.QEvent.Enter:
            self._paused = True
        elif event.type() == QtCore.QEvent.Leave:
            self._paused = False
        return super().event(event)

    def pause(self):
        if self._timer.isActive():
            self._paused = True
            self._timer.stop()

    def resume(self):
        if not self._timer.isActive() and self._paused:
            self._paused = False
            self._timer.start(self._speed)

    def getFPS(self):
        return self._fps

    def setFPS(self, fps):
        self._fps = fps
        self._speed = int(1 / self._fps * 1000)
        if not self._paused:
            if self._timer.isActive():
                self._timer.stop()
            self._timer.start(self._speed)

    def getDirection(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction if direction in (QtCore.Qt.RightToLeft, QtCore.Qt.LeftToRight) else QtCore.Qt.RightToLeft
        if self._document:
            if self._direction == QtCore.Qt.RightToLeft:
                self._initX = self._parent.width() / 2 if self._parent else self.width()
            else:
                self._initX = -(self._document.textWidth() * 0.85)
            self._x = self._initX
        else:
            self._initX = 0
            self._x = 0

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()


class MarqueeQt(QtWidgets.QLabel):
    # Based on moving a QLabel with a pixmap generated from the desired text
    # Good try, but still consumes a lot of CPU (for an RPi or alike, not for a PC)
    # Smooth=False is an ugly hack to make it work on RPi 1 whilst not raising CPU usage to 100%

    def __init__(self, parent, font=None, stylesheet=None, fps=60, direction=QtCore.Qt.RightToLeft, smooth=True):
        super(MarqueeQt, self).__init__(parent)

        self.hide()

        self._parent = parent
        self._direction = direction
        self._smooth = smooth
        self._lag = (1 if smooth else 20)
        self._fps = fps
        self._speed = fps / self._lag
        self._initText = ""
        self._blanksLen = 0
        self._initX = 0
        self._x = 0
        self._y = 0

        if font:
            _font = font
        else:
            _font = self._parent.font()
        self.setFont(_font)
        self._fm = QtGui.QFontMetrics(self.font())

        if stylesheet:
            _style = stylesheet
        else:
           _style = self._parent.styleSheet()
        self.setStyleSheet(_style)

        self.setSizePolicy(self._parent.sizePolicy())
        self.setGeometry(self._parent.geometry())

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.translate)

    def setText(self, text):

        self._initText = text

        if self._smooth:

            bcolor = getQColorFromRGB(getBkgColor(self.styleSheet()))
            fcolor = getQColorFromRGB(getColor(self.styleSheet()))
            img = QtGui.QPixmap(createImgFromText(text, font=self.font(), bcolor=bcolor, fcolor=fcolor))
            self.setPixmap(img)
            self.setFixedWidth(img.width())
            self.setFixedHeight(img.height())

            if self._direction == QtCore.Qt.LeftToRight:
                self._initX = (self._parent.width() / 2) - self.width()
                self.setAlignment(QtCore.Qt.AlignRight)
            else:
                self._initX = self._parent.width()
                self.setAlignment(QtCore.Qt.AlignLeft)

        else:

            self._blanksLen = int(self._parent.width() / self._fm.width("B") * 1.5)
            if self._direction == QtCore.Qt.LeftToRight:
                text = text + (" " * self._blanksLen)
            else:
                text = (" " * self._blanksLen) + text
            super(Marquee, self).setText(text)

            if self._direction == QtCore.Qt.LeftToRight:
                self._initX = (self._parent.width() / 2) - self.width()
                self.setAlignment(QtCore.Qt.AlignRight)
            else:
                self._initX = 0
                self.setAlignment(QtCore.Qt.AlignLeft)

        self._x = self._initX
        self._y = self._parent.pos().y()

    @QtCore.pyqtSlot()
    def translate(self):
        if self._smooth:
            if self._direction == QtCore.Qt.LeftToRight:
                if self._x < self._parent.width():
                    self._x += self._lag
                else:
                    self._x = self._initX
            else:
                if abs(self._x) + (self._parent.width() / 2) < self.width():
                    self._x -= self._lag
                else:
                    self._x = self._initX
            self.move(self._x, self._y)
        else:
            if self._direction == QtCore.Qt.LeftToRight:
                text = self.text()[:-1]
            else:
                text = self.text()[1:]
            if len(text) == 0:
                text = self._initText
            super(Marquee, self).setText(text)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if self._smooth:
            if a0.rect().width() != self._initX + self._lag:
                # self.move(self._x, self._y)
                super(Marquee, self).paintEvent(a0)
        else:
            super(Marquee, self).paintEvent(a0)

    def start(self):
        if not self._timer.isActive():
            self._timer.start(int(1 / self._speed * 1000))
            self.show()

    def pause(self):
        self._timer.stop()

    def stop(self):
        self._timer.stop()
        self.clear()
        self.hide()

    def getFPS(self):
        return self._fps

    def setFPS(self, fps):
        self._fps = fps
        self._speed = fps / self._lag
        if self._timer.isActive():
            self._timer.stop()
            self._timer.start(int(1 / self._speed * 1000))

    def getDirection(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction


class Clock(QtWidgets.QLabel):
    # https://www.geeksforgeeks.org/create-analog-clock-using-pyqt5-in-python/

    # constructor
    def __init__(self, bcolor=QtCore.Qt.green, scolor=QtCore.Qt.red, bkcolor="black", size=300, hoffset=0, moffset=0, drawsec=False):
        QtWidgets.QLabel.__init__(self, None)

        # creating a timer object
        self.timer = QtCore.QTimer(self)

        # adding action to the timer
        # update the whole code
        self.timer.timeout.connect(self.update)

        # setting start time of timer i.e 1 second or 1 minute (if no seconds will be painted)
        lag = (1000 if drawsec else 60000)
        self.timer.start(lag)

        # setting window title
        self.setWindowTitle('Clock')

        # setting window geometry
        # self.setGeometry(200, 200, 300, 300)
        self.setFixedSize(size, size)

        # setting background color to the window
        self.setStyleSheet("background-color:"+bkcolor+";")

        # creating hour hand
        self.hPointer = QtGui.QPolygon([QtCore.QPoint(6, 7),
                                        QtCore.QPoint(-6, 7),
                                        QtCore.QPoint(0, -50)])

        # creating minute hand
        self.mPointer = QtGui.QPolygon([QtCore.QPoint(6, 7),
                                  QtCore.QPoint(-6, 7),
                                  QtCore.QPoint(0, -70)])

        # creating second hand
        self.drawsec = drawsec
        if self.drawsec:
            self.sPointer = QtGui.QPolygon([QtCore.QPoint(1, 1),
                                      QtCore.QPoint(-1, 1),
                                      QtCore.QPoint(0, -90)])
        # colors
        # color for minute and hour hand
        self.bColor = bcolor

        # color for second hand
        self.sColor = scolor

        # time offset for different timeZones
        self.hoffset = hoffset
        self.moffset = moffset

    # method for paint event
    def paintEvent(self, event):

        # getting minimum of width and height
        # so that clock remain square
        rec = min(self.width(), self.height())

        # getting current time
        tik = QtCore.QTime.currentTime()
        tik.setHMS(tik.hour() + self.hoffset, tik.minute() + self.moffset, tik.second())

        # creating a painter object
        painter = QtGui.QPainter(self)

        # method to draw the hands
        # argument : color rotation and which hand should be pointed
        def drawPointer(color, rotation, pointer):

            # setting brush
            painter.setBrush(QtGui.QBrush(color))

            # saving painter
            painter.save()

            # rotating painter
            painter.rotate(rotation)

            # draw the polygon i.e hand
            painter.drawConvexPolygon(pointer)

            # restore the painter
            painter.restore()

        # tune up painter
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # translating the painter
        painter.translate(self.width() / 2, self.height() / 2)

        # scale the painter
        painter.scale(rec / 200, rec / 200)

        # set current pen as no pen
        painter.setPen(QtCore.Qt.NoPen)

        # draw each hand
        drawPointer(self.bColor, (30 * (tik.hour() + tik.minute() / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (tik.minute() + tik.second() / 60)), self.mPointer)
        if self.drawsec:
            drawPointer(self.sColor, (6 * tik.second()), self.sPointer)

        # drawing background
        painter.setPen(QtGui.QPen(self.bColor))

        # for loop
        for i in range(0, 60):

            # drawing background lines
            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)

            # rotating the painter
            painter.rotate(6)

        # ending the painter
        painter.end()

    def stop(self):
        self.timer.stop()
        self.clear()


import tkinter as tk


class _MarqueeTk(tk.Canvas):
    def __init__(self, parent, text, margin=2, borderwidth=1, relief='flat', fps=30):
        super().__init__(parent, borderwidth=borderwidth, relief=relief)

        self.fps = fps

        # start by drawing the text off screen, then asking the canvas
        # how much space we need. Use that to compute the initial size
        # of the canvas.
        text = self.create_text(0, -1000, text=text, anchor="w", tags=("text",))
        (x0, y0, x1, y1) = self.bbox("text")
        width = (x1 - x0) + (2 * margin) + (2 * borderwidth)
        height = (y1 - y0) + (2 * margin) + (2 * borderwidth)
        self.configure(width=width, height=height)

        # start the animation
        self.animate()

    def animate(self):
        (x0, y0, x1, y1) = self.bbox("text")
        if x1 < 0 or y0 < 0:
            # everything is off the screen; reset the X
            # to be just past the right margin
            x0 = self.winfo_width()
            y0 = int(self.winfo_height() / 2)
            self.coords("text", x0, y0)
        else:
            self.move("text", -1, 0)

        # do again in a few milliseconds
        self.after_id = self.after(int(1000 / self.fps), self.animate)


def marqueeTk(parent, text, x, y, width, height, margin=2, borderwidth=1, relief='flat', fps=30, transparent=False, frameless=False):

    if parent:
        root = parent
    else:
        root = tk.Tk()
    marquee = _MarqueeTk(root, text, margin, borderwidth, relief, fps)
    marquee.pack(side="top", fill="x", pady=20)
    root.geometry("%sx%s+%s+%s" % (width, height, x, y))
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    if frameless:
        root.overrideredirect(True)
    if transparent:
        root.wm_attributes("-transparentcolor", "white")
    root.mainloop()


def _list_all_signals(obj: QObject) -> Iterable[pyqtBoundSignal]:
    attr_names = dir(obj)
    attributes = (getattr(obj, attr_name) for attr_name in attr_names)
    connectable = filter(lambda l: hasattr(l, "connect"), attributes)

    return connectable


class _SignalListener(QObject):
    @pyqtSlot()
    def universal_slot(self, *args, **kwargs):
        print("Signal caught" + 30 * "-")
        print("sender:", self.sender())
        meta_method = (self.sender().metaObject().method(self.senderSignalIndex()))
        print("signal:", meta_method.name())
        print("signal signature:", meta_method.methodSignature())


_SIGNAL_LISTENER = _SignalListener()


def spy_on_all_signals(obj: QObject, listener: _SignalListener = _SIGNAL_LISTENER):
    for signal in _list_all_signals(obj):
        signal.connect(listener.universal_slot)


def adjustFont(widget, initPointSize, text):
    # https://stackoverflow.com/questions/63767518/is-there-a-way-to-make-the-font-size-of-a-label-dynamicly-adjust-to-the-text-tha

    if widget.parent():
        # if the widget has a parent, get the available width by computing the
        # available rectangle between the parent rectangle and the widget
        # geometry (logical AND)
        rect = widget.parent().rect() & widget.geometry()
        width = rect.width()
    else:
        width = widget.width()
    font = widget.font()
    font.setPointSize(initPointSize)
    while True:
        textWidth = QtGui.QFontMetrics(font).size(QtCore.Qt.TextSingleLine, text).width()
        if textWidth <= width or font.pointSize() <= 6:
            break
        font.setPointSize(font.pointSize() - 1)
    return font


def getPlainText(widget):
    # https://stackoverflow.com/questions/8890320/get-plain-text-from-a-qlabel-with-rich-text
    doc = QtGui.QTextDocument()
    doc.setHtml(widget.text())
    plain_text = doc.toPlainText()
    del doc
    return plain_text
