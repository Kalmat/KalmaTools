import tkinter as tk
from PIL import ImageTk
from tkextrafont import Font


def tkLoadFont(fontpath, fontfamily):
    try:
        return Font(file=fontpath, family=fontfamily)
    except:
        return None


class FakeRoot(tk.Tk):
    # It creates a "Fake", minimum, transparent, iconified root window on top of which you can create a TopLevel
    # It allows to set system caption and icon, what would not be possible if TopLevel child has no title bar
    # Based on: (noob oddy) https://stackoverflow.com/questions/4066027/making-tkinter-windows-show-up-in-the-taskbar

    def __init__(self, title, icon):
        tk.Tk.__init__(self)

        self.title(title)
        self.wm_title(title)
        img = ImageTk.PhotoImage(file=icon)
        self.tk.call('wm', 'iconphoto', self._w, img)

        self.wait_visibility(self)
        self.configure(bg="black")
        self.attributes('-alpha', 0.0)
        self.geometry("1x1+0+0")
        self.lower()
        # self.iconify()

        # Catch and propagate WM Focus events (might be useful for the TopLevel child)
        # self.protocol('WM_TAKE_FOCUS', self.on_take_focus())  # Maybe it only works on Linux???
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)
        self.bind('<Map>', self.on_map)
        self.bind('<Unmap>', self.on_unmap)

    def on_take_focus(self, e=None):
        self.event_generate("<<TAKEFOCUS>>")

    def on_focus_in(self, e=None):
        self.event_generate("<<FOCUSIN>>")

    def on_focus_out(self, e=None):
        self.event_generate("<<FOCUSOUT>>")

    def on_map(self, e=None):
        self.event_generate("<<MAP>>")

    def on_unmap(self, e=None):
        self.event_generate("<<UNMAP>>")


def round_rectangle(parent, canvas, x1, y1, x2, y2, radius=25, bgcolor="grey", color="black", **kwargs):
    # https://stackoverflow.com/questions/68874874/how-can-i-make-tkinters-windows-corner-rounded

    parent.overrideredirect(True)
    parent.config(background=bgcolor)
    parent.attributes("-transparentcolor", bgcolor)

    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True, fill=color)


class Tooltip:
    '''
    It creates a tooltip for a given widget as the mouse goes on it. see:

    https://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216
    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.
    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.
    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.

      Tested on Ubuntu 16.04/16.10, running Python 3.5.2
    '''

    def __init__(self, widget,
                 *,
                 bg='#303030',
                 fg='#FFFFFF',
                 pad=(5, 3, 5, 3),
                 text='widget info',
                 waittime=500,
                 wraplength=300):

        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<Button-1>", self.onLeave)
        self.bg = bg
        self.fg = fg
        self.pad = pad
        self.id = None
        self.tw = None
        self._isVisible = False

    def onEnter(self, event=None):
        self.schedule()

    def onLeave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(widget, label,
                               *,
                               tip_delta=(10, 5), pad=(5, 3, 5, 3)):

            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                             pad[1] + label.winfo_reqheight() + pad[3])

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:

                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        bg = self.bg
        fg = self.fg
        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = tk.Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.attributes('-topmost', True)
        win = tk.Frame(self.tw,
                       background=bg,
                       borderwidth=0)
        label = tk.Label(win,
                         text=self.text,
                         justify=tk.LEFT,
                         background=bg,
                         foreground=fg,
                         relief=tk.SOLID,
                         borderwidth=0,
                         highlightthickness=0,
                         wraplength=self.wraplength)
        label.grid(padx=(pad[0], pad[2]),
                   pady=(pad[1], pad[3]),
                   sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))
        self._isVisible = True

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None
        self._isVisible = False

    def isVisible(self):
        return self._isVisible
