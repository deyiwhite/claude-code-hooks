#!/usr/bin/env python3
"""Claude Code PreToolUse hook - lightweight notification for file edits."""

import json
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

BG      = '#faf7ff'
CARD    = '#fdfaff'
BD      = '#d8c4ea'
TEXT    = '#3f255f'
SUB     = '#705087'
DIM     = '#9e85b8'
ACC     = '#c084d4'
ACC_HV  = '#ad70c0'
BLUE    = '#a5b4fc'
GREEN   = '#93c5fd'
YELLOW  = '#f4d77d'
PINK    = '#f0abfc'

UI   = 'Microsoft YaHei UI'
MONO = 'Consolas'

COLORS_MAP = {
    'Edit': BLUE,
    'MultiEdit': BLUE,
    'Write': GREEN,
    'NotebookEdit': BLUE,
}


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
            root.after(12, lambda: _fade_in(root, min(alpha + 0.14, 1.0)))
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
        w = bar.winfo_width() or 330
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


def _short_path(path, max_len=72):
    if len(path) <= max_len:
        return path
    return '...' + path[-(max_len - 3):]


def show(data):
    tool_name = data.get('tool_name', 'Edit')
    tool_input = data.get('tool_input', {})

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {}

    desc = tool_input.get('description', '')
    file_path = tool_input.get('file_path') or tool_input.get('path') or ''
    badge_color = COLORS_MAP.get(tool_name, ACC)

    root = tk.Tk()
    root.withdraw()
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=CARD)

    _accent_bar(root)

    wrap = tk.Frame(root, bg=CARD, padx=18, pady=14)
    wrap.pack(fill='both', expand=True)

    head = tk.Frame(wrap, bg=CARD)
    head.pack(fill='x')
    tk.Label(head, text=tool_name,
             bg=badge_color, fg='#ffffff',
             font=(MONO, 9, 'bold'),
             padx=8, pady=3).pack(side='left')
    tk.Label(head, text='  即将修改',
             bg=CARD, fg=TEXT, font=(UI, 11, 'bold')).pack(side='left')

    tk.Frame(wrap, bg=BD, height=1).pack(fill='x', pady=(10, 9))

    if file_path:
        info = tk.Frame(wrap, bg='#f8f1ff', highlightbackground=BD, highlightthickness=1)
        info.pack(fill='x')
        tk.Label(info, text=os.path.basename(file_path),
                 bg='#f8f1ff', fg=TEXT, font=(UI, 10, 'bold'),
                 padx=10, pady=7,
                 anchor='w').pack(fill='x')
        dirn = os.path.dirname(file_path)
        if dirn:
            tk.Label(info, text=_short_path(dirn),
                     bg='#f8f1ff', fg=DIM, font=(MONO, 8),
                     padx=10, pady=0,
                     anchor='w').pack(fill='x', pady=(0, 7))

    if desc:
        outer = tk.Frame(wrap, bg=badge_color, highlightbackground=BD, highlightthickness=1)
        outer.pack(fill='x', pady=(9, 0))
        desc_f = tk.Frame(outer, bg='#f8f1ff')
        desc_f.pack(fill='both', expand=True, padx=(4, 0))
        desc_lbl = tk.Label(desc_f, text=desc,
                            bg='#f8f1ff', fg=SUB,
                            font=(UI, 9), justify='left',
                            padx=10, pady=7, anchor='w',
                            wraplength=330)
        desc_lbl.pack(fill='x')

        def adj_wrap():
            w = desc_f.winfo_width()
            if w > 24:
                desc_lbl.configure(wraplength=w - 24)

        root.after(10, adj_wrap)

    footer = tk.Frame(wrap, bg=CARD)
    footer.pack(fill='x', pady=(12, 0))

    countdown_var = tk.StringVar(value='10s 后自动关闭')
    tk.Label(footer, textvariable=countdown_var, bg=CARD, fg=DIM,
             font=(UI, 8)).pack(side='left')

    def close():
        root.quit()

    btn = tk.Button(footer, text='知道了', command=close,
                    bg=CARD, fg=ACC, font=(UI, 9),
                    activebackground='#f3e8ff', activeforeground=ACC_HV,
                    relief='flat', padx=16, pady=3, cursor='hand2',
                    bd=0, highlightthickness=1, highlightbackground=BD)
    btn.pack(side='right')

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

    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    max_w = int(root.winfo_screenwidth() * 0.6)
    max_h = int(root.winfo_screenheight() * 0.35)
    _center(root, min(max(w, 360), max_w), min(h, max_h))

    _show_smooth(root, btn)
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            sys.exit(0)
        data = json.loads(raw.decode('utf-8'))
    except Exception:
        sys.exit(0)
    try:
        show(data)
    except Exception:
        pass
    sys.exit(0)


if __name__ == '__main__':
    main()
