#!/usr/bin/env python3
"""Claude Code Notification hook - idle prompt popup."""

import os
import sys
import tkinter as tk


def _enable_windows_polish():
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass


_enable_windows_polish()

BG   = '#ede5f5'
CARD = '#fdfaff'
TEXT = '#4a2e6a'
SUB  = '#7a5490'
ACC  = '#c084d4'
ACC2 = '#ad70c0'
BD   = '#d8c4ea'
DIV  = '#eadcf3'

FONT = 'Microsoft YaHei UI'
MONO = 'Consolas'


def _center(root, w, h):
    root.geometry(f'{w}x{h}')
    root.eval('tk::PlaceWindow . center')


def _focus(root, btn):
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.focus_force()
    btn.focus_set()


def _fade_in(root, alpha=0.0):
    try:
        root.attributes('-alpha', alpha)
        if alpha < 1.0:
            root.after(12, lambda: _fade_in(root, min(alpha + 0.12, 1.0)))
    except Exception:
        pass


def _show_smooth(root, focus_widget):
    try:
        root.attributes('-alpha', 0.0)
    except Exception:
        pass
    root.deiconify()
    _focus(root, focus_widget)
    _fade_in(root)


def _accent_bar(parent):
    bar = tk.Canvas(parent, height=4, bg=CARD, highlightthickness=0)
    bar.pack(fill='x')
    colors = ['#f9a8d4', '#f0abfc', '#d8b4fe', '#c4b5fd', '#fbcfe8']

    def hex_to_rgb(value):
        value = value.lstrip('#')
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    def mix(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def draw(event=None):
        bar.delete('all')
        w = bar.winfo_width() or 340
        stops = [hex_to_rgb(c) for c in colors]
        steps = max(1, min(w, 180))
        for i in range(steps):
            pos = i / max(steps - 1, 1) * (len(stops) - 1)
            idx = min(int(pos), len(stops) - 2)
            color = mix(stops[idx], stops[idx + 1], pos - idx)
            x1 = int(i * w / steps)
            x2 = int((i + 1) * w / steps) + 1
            bar.create_rectangle(x1, 0, x2, 4, fill=f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}', outline='')

    bar.bind('<Configure>', draw)


def show_dialog():
    root = tk.Tk()
    root.withdraw()
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=CARD)

    _accent_bar(root)

    tk.Label(root, text='♡(˃͈ ε ˂͈ )', bg=CARD, fg=ACC,
             font=(FONT, 15)).pack(pady=(24, 0))

    tk.Frame(root, bg=DIV, height=1).pack(fill='x', padx=30, pady=(16, 16))

    tk.Label(root, text='任务已完成，等待新指令', bg=CARD, fg=SUB,
             font=(FONT, 11, 'bold')).pack()

    tk.Frame(root, bg=CARD, height=18).pack()

    def close():
        root.quit()

    btn = tk.Button(root, text='知道啦', command=close,
                    bg=ACC, fg='#ffffff', font=(FONT, 11, 'bold'),
                    activebackground=ACC2, activeforeground='#ffffff',
                    relief='flat', padx=28, pady=7, cursor='hand2', bd=0)
    btn.pack()

    countdown_var = tk.StringVar(value='10s 后自动关闭')
    tk.Label(root, textvariable=countdown_var, bg=CARD, fg=BD,
             font=(FONT, 8)).pack(pady=(8, 18))

    remaining = [10]

    def tick():
        if not root.winfo_exists():
            return
        remaining[0] -= 1
        if remaining[0] <= 0:
            close()
        else:
            countdown_var.set(f'{remaining[0]}s 后自动关闭')
            root.after(1000, tick)

    root.after(1000, tick)
    root.bind('<Return>', lambda e: close())
    root.protocol('WM_DELETE_WINDOW', close)

    _center(root, 340, 226)
    _show_smooth(root, btn)

    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass


def main():
    try:
        sys.stdin.buffer.read()
    except Exception:
        pass
    try:
        show_dialog()
    except Exception:
        pass


if __name__ == '__main__':
    main()
