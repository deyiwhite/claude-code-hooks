#!/usr/bin/env python3
"""Claude Code Notification hook - idle prompt popup."""

import sys, os, tkinter as tk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

BG   = '#ede5f5'
CARD = '#fdfaff'
TEXT = '#4a2e6a'
SUB  = '#7a5490'
ACC  = '#c084d4'
ACC2 = '#ad70c0'
BD   = '#cdbde0'
DIV  = '#dccde8'

FONT = 'Segoe UI'
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


def show_dialog():
    root = tk.Tk()
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=CARD)

    # 顶部彩虹条
    rainbow = tk.Canvas(root, height=3, bg=CARD, highlightthickness=0)
    rainbow.pack(fill='x')
    colors = ['#fda4af','#fdba74','#fde68a','#a7f3d0','#93c5fd','#c4b5fd','#f9a8d4']
    def _draw(event=None):
        rainbow.delete('all')
        w = rainbow.winfo_width() or 340
        seg = w / len(colors)
        for i, c in enumerate(colors):
            rainbow.create_rectangle(i*seg, 0, (i+1)*seg, 3, fill=c, outline='')
    rainbow.bind('<Configure>', _draw)

    # 颜文字
    tk.Label(root, text='\u2661(\u02c3\u0348 \u03b5 \u02c2\u0348 )', bg=CARD,
             font=(FONT, 14)).pack(pady=(18, 0))

    # 标题
    tk.Label(root, text='Claude', bg=CARD, fg=TEXT,
             font=(MONO, 13, 'bold')).pack(pady=(6, 0))

    tk.Frame(root, bg=DIV, height=1).pack(fill='x', padx=30, pady=(10, 12))

    # 消息
    tk.Label(root, text='任务已完成，等待新指令', bg=CARD, fg=SUB,
             font=(FONT, 11, 'bold')).pack()

    tk.Frame(root, bg=CARD, height=10).pack()

    def close():
        root.quit()

    btn = tk.Button(root, text='知道啦', command=close,
                    bg=ACC, fg='#fff', font=(FONT, 11, 'bold'),
                    activebackground=ACC2, activeforeground='#fff',
                    relief='flat', padx=28, pady=7, cursor='hand2', bd=0)
    btn.pack()

    # 倒计时
    tk.Frame(root, bg=CARD, height=6).pack()
    countdown_var = tk.StringVar(value='10s 后自动关闭')
    tk.Label(root, textvariable=countdown_var, bg=CARD, fg='#c4b5fd',
             font=(FONT, 8)).pack()

    remaining = [10]
    def _tick():
        if not root.winfo_exists():
            return
        remaining[0] -= 1
        if remaining[0] <= 0:
            close()
        else:
            countdown_var.set(f'{remaining[0]}s 后自动关闭')
            root.after(1000, _tick)
    root.after(1000, _tick)

    _focus(root, btn)
    root.bind('<Return>', lambda e: close())
    root.protocol('WM_DELETE_WINDOW', close)

    _center(root, 340, 225)

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
