#!/usr/bin/python
# -*- coding: utf-8 -*-

import AppKit
import Quartz

WS = AppKit.NSWorkspace.sharedWorkspace()
SCREEN = AppKit.NSScreen.mainScreen()


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
    imageURL = WS.desktopImageURLForScreen_(SCREEN)
    return imageURL


def setWallpaper(imageURL):
    # https://stackoverflow.com/questions/65936437/change-macos-background-picture-with-adapt-to-screen-parameter-in-python
    # Use this to convert a "normal" image path into a macOS wallpaper path (NSURL)
    # imageURL = Foundation.NSURL.fileURLWithPath_(img)
    WS.setDesktopImageURL_forScreen_options_error_(imageURL, SCREEN, None, None)

    # Use this to change image scaling and other options
    # fillColor = AppKit.NSColor.darkGrayColor()
    # optDict = Foundation.NSDictionary.dictionaryWithObjects_forKeys_([AppKit.NSImageScaleAxesIndependently, fillColor],
    #                                                       [AppKit.NSWorkspaceDesktopImageScalingKey,
    #                                                        AppKit.NSWorkspaceDesktopImageFillColorKey])
    # sharedSpace.setDesktopImageURL_forScreen_options_error_(img, mainScreen, optDict, None)


def enable_activedesktop():
    raise NotImplementedError


def toggleDesktopIcons():
    raise NotImplementedError


def getScreenSize():
    screen_area = SCREEN.frame()
    return screen_area.size.width, screen_area.size.height


def getWorkArea():
    work_area = SCREEN.visibleFrame()
    return int(work_area.origin.x), 0, int(work_area.size.width), int(work_area.size.height)


def getAttributes(hWnd):
    raise NotImplementedError
