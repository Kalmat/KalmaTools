#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import AppKit
import Quartz


def sendBehind(name):
    w = None
    for win in AppKit.NSApp().orderedWindows():
        w = win
        break
    if w:
        # https://stackoverflow.com/questions/4982584/how-do-i-draw-the-desktop-on-mac-os-x
        w.setLevel_(Quartz.kCGDesktopWindowLevel - 1)
        w.setCollectionBehavior_(Quartz.NSWindowCollectionBehaviorCanJoinAllSpaces |
             Quartz.NSWindowCollectionBehaviorStationary |
             Quartz.NSWindowCollectionBehaviorIgnoresCycle)


def sendFront(name):
    w = None
    for win in AppKit.NSApp().orderedWindows():
        w = win
        break
    if w:
        # https://stackoverflow.com/questions/4982584/how-do-i-draw-the-desktop-on-mac-os-x
        w.setLevel_(Quartz.kCGDesktopWindowLevel + 1)
        w.setCollectionBehavior_(Quartz.NSWindowCollectionBehaviorCanJoinAllSpaces |
             Quartz.NSWindowCollectionBehaviorStationary |
             Quartz.NSWindowCollectionBehaviorIgnoresCycle)


def getWallpaper():
    # https://stackoverflow.com/questions/14099363/get-the-current-wallpaper-in-cocoa
    sharedSpace = AppKit.NSWorkspace.sharedWorkspace()
    mainScreen = AppKit.NSScreen.mainScreen()
    imageURL = sharedSpace.desktopImageURLForScreen_(mainScreen)
    return imageURL


def setWallpaper(imageURL):
    # https://stackoverflow.com/questions/65936437/change-macos-background-picture-with-adapt-to-screen-parameter-in-python
    # Use this to convert a "normal" image path into a macOS wallpaper path (NSURL)
    # imageURL = Foundation.NSURL.fileURLWithPath_(img)
    sharedSpace = AppKit.NSWorkspace.sharedWorkspace()
    mainScreen = AppKit.NSScreen.mainScreen()
    sharedSpace.setDesktopImageURL_forScreen_options_error_(imageURL, mainScreen, None, None)

    # Use this to change image scaling and other options
    # fillColor = AppKit.NSColor.darkGrayColor()
    # optDict = Foundation.NSDictionary.dictionaryWithObjects_forKeys_([AppKit.NSImageScaleAxesIndependently, fillColor],
    #                                                       [AppKit.NSWorkspaceDesktopImageScalingKey,
    #                                                        AppKit.NSWorkspaceDesktopImageFillColorKey])
    # sharedSpace.setDesktopImageURL_forScreen_options_error_(img, mainScreen, optDict, None)


def getWorkArea():
    work_area = AppKit.NSScreen.mainScreen().visibleFrame()
    return int(work_area.origin.x), 0, int(work_area.size.width), int(work_area.size.height)


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
