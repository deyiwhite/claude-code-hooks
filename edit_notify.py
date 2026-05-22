#!/usr/bin/env python3
"""Claude Code PreToolUse hook - lightweight notification for Edit/Write."""

import sys, os, json, tkinter as tk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

BG      = '#faf7ff'
CARD    = '#f5eeff'
BD      = '#ddd0f0'
TEXT    = '#3d2460'
SUB     = '#6b4f8a'
DIM     = '#b098c8'
ACC     = '#9c6cd4'
BLUE    = '#93c5fd'
GREEN   = '#a7f3d0'
YELLOW  = '#fde68a'

UI   = 'Segoe UI'
MONO = 'Consolas'

COLORS_MAP = {
    'Edit':          BLUE,
    'MultiEdit':     BLUE,
    'Write':         GREEN,
    'NotebookEdit':  YELLOW,
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


def show(data):
    tool_name = data.get('tool_name', 'Edit')
    tool_input = data.get('tool_input', {})

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {}

    desc = tool_input.get('description', '')
    file_path = tool_input.get('file_path', '')
    badge_color = COLORS_MAP.get(tool_name, ACC)

    root = tk.Tk()
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=CARD)

    # ── 彩虹条 ──────────────────────────────────────────────────
    rainbow = tk.Canvas(root, height=3, bg=CARD, highlightthickness=0)
    rainbow.pack(fill='x')
    seg_colors = ['#fda4af','#fdba74','#fde68a','#a7f3d0','#93c5fd','#c4b5fd','#f9a8d4']
    def _draw_r(event=None):
        rainbow.delete('all')
        w = rainbow.winfo_width() or 310
        seg = w / len(seg_colors)
        for i, c in enumerate(seg_colors):
            rainbow.create_rectangle(i*seg, 0, (i+1)*seg, 3, fill=c, outline='')
    rainbow.bind('<Configure>', _draw_r)

    # ── 标题 ────────────────────────────────────────────────────
    head = tk.Frame(root, bg=CARD)
    head.pack(fill='x', padx=12, pady=(10, 0))

    tk.Label(head, text=f' {tool_name} ',
             bg=badge_color, fg='#ffffff',
             font=(UI, 11, 'bold'),
             padx=10, pady=3).pack(side='left')

    tk.Label(head, text=' 即将修改',
             bg=CARD, fg=TEXT,
             font=(UI, 11, 'bold')).pack(side='left', pady=2)

    # ── 分割线 ──────────────────────────────────────────────────
    tk.Frame(root, bg=BD, height=1).pack(fill='x', padx=12, pady=(5, 6))

    # ── 文件名 ──────────────────────────────────────────────────
    if file_path:
        name = os.path.basename(file_path)
        dirn = os.path.dirname(file_path)
        tk.Label(root, text=f'\U0001f4c4 {name}',
                 bg=CARD, fg=TEXT,
                 font=(UI, 10, 'bold')).pack(padx=12, anchor='w')
        if dirn:
            tk.Label(root, text=dirn,
                     bg=CARD, fg=DIM,
                     font=(MONO, 7)).pack(padx=12, anchor='w')

    # ── 描述 ────────────────────────────────────────────────────
    if desc:
        tk.Frame(root, bg=CARD, height=4).pack()
        desc_lbl = tk.Label(root, text=desc,
                 bg=CARD, fg=SUB,
                 font=(UI, 9),
                 justify='left')
        desc_lbl.pack(padx=12, anchor='w', fill='x')

        def _adj_wrap():
            w = root.winfo_width()
            if w > 24:
                desc_lbl.configure(wraplength=w - 24)
        root.after(10, _adj_wrap)

    # ── 按钮 ────────────────────────────────────────────────────
    tk.Frame(root, bg=CARD, height=10).pack()

    remaining = [10]

    def close():
        root.quit()

    def _tick():
        if not root.winfo_exists():
            return
        remaining[0] -= 1
        if remaining[0] <= 0:
            root.quit()
        else:
            countdown_var.set(f'{remaining[0]}s 后自动关闭')
            root.after(1000, _tick)
    root.after(1000, _tick)

    btn = tk.Button(root, text='知道了', command=close,
                    bg=CARD, fg=ACC,
                    font=(UI, 9),
                    activebackground='#ede0f8', activeforeground=ACC,
                    relief='flat', padx=16, pady=2,
                    cursor='hand2', bd=0,
                    highlightthickness=1, highlightbackground=BD)
    btn.pack()

    # ── 倒计时 ──────────────────────────────────────────────────
    tk.Frame(root, bg=CARD, height=3).pack()
    countdown_var = tk.StringVar(value='10s 后自动关闭')
    tk.Label(root, textvariable=countdown_var, bg=CARD, fg=DIM,
             font=(UI, 8)).pack()
    tk.Frame(root, bg=CARD, height=4).pack()

    root.bind('<Return>', lambda e: close())
    root.protocol('WM_DELETE_WINDOW', close)

    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    max_w = int(root.winfo_screenwidth() * 0.6)
    max_h = int(root.winfo_screenheight() * 0.35)
    _center(root, min(max(w, 310), max_w), min(h, max_h))

    _focus(root, btn)
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            os.write(1, b'{"continue": true}\n')
            return
        data = json.loads(raw.decode())
    except Exception:
        os.write(1, b'{"continue": true}\n')
        return
    try:
        show(data)
    except Exception:
        pass
    os.write(1, b'{"continue": true}\n')


if __name__ == '__main__':
    main()
