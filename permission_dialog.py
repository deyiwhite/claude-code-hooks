#!/usr/bin/env python3
"""Claude Code PreToolUse hook - permission dialog."""

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
CARD_BG = '#f7f0ff'
CARD_BD = '#d8c4ea'
CODE_BG = '#f2ebfa'
CODE_BD = '#d9c6e8'
DIV     = '#eadcf3'
TEXT    = '#3f255f'
SUB     = '#6e4f87'
CODE_FG = '#4b3170'
ACC     = '#c084d4'
ACC_HV  = '#ad70c0'
DEN     = '#c2788a'
DEN_HV  = '#b0687a'

UI   = 'Microsoft YaHei UI'
MONO = 'Consolas'

SKIP_KEYS = {'description', 'timeout'}


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
        root.attributes('-alpha', 1.0)
    except Exception:
        pass
    root.deiconify()
    _focus(root, focus_widget)
    try:
        root.attributes('-alpha', 1.0)
    except Exception:
        pass


def _detail(tool_input):
    lines = []
    for k, v in tool_input.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, str):
            lines.append(f'{k}: {v}')
        elif isinstance(v, (int, float, bool)):
            lines.append(f'{k}: {v}')
        elif isinstance(v, (dict, list)):
            lines.append(f'{k}: {json.dumps(v, ensure_ascii=False, indent=2)}')
    return '\n'.join(lines)


def _detail_cols(detail):
    lines = detail.splitlines() or ['']
    longest = max(len(line) for line in lines)
    if longest <= 36:
        return 44
    if longest <= 58:
        return 56
    if longest <= 76:
        return min(longest + 2, 64)
    if longest <= 98:
        return 66
    return 74


def _remember(tool_name, tool_input):
    rule = f'{tool_name}(*)'
    if tool_name == 'Bash':
        cmd = tool_input.get('command', '')
        if cmd and '\n' not in cmd and len(cmd) <= 80:
            rule = f'{tool_name}({cmd})'

    project_config = os.path.join(os.getcwd(), '.claude', 'settings.local.json')
    try:
        s = json.load(open(project_config, 'r', encoding='utf-8')) if os.path.exists(project_config) else {}
        s.setdefault('permissions', {}).setdefault('allow', [])
        if rule not in s['permissions']['allow']:
            s['permissions']['allow'].append(rule)
        os.makedirs(os.path.dirname(project_config), exist_ok=True)
        with open(project_config, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _accent_bar(parent):
    bar = tk.Canvas(parent, height=4, bg=BG, highlightthickness=0)
    bar.pack(fill='x')
    colors = ['#f9a8d4', '#f0abfc', '#d8b4fe', '#c4b5fd', '#fbcfe8']

    def hex_to_rgb(value):
        value = value.lstrip('#')
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    def mix(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def draw(event=None):
        bar.delete('all')
        w = bar.winfo_width() or 460
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


def show(data):
    tool_name = data.get('tool_name', 'Unknown')
    tool_input = data.get('tool_input', {})

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {'raw': tool_input}

    desc = tool_input.get('description', '')
    detail = _detail(tool_input)
    done = {'ok': False}

    root = tk.Tk()
    root.withdraw()
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=BG)

    _accent_bar(root)

    head = tk.Frame(root, bg=BG)
    head.pack(fill='x', padx=16, pady=(14, 0))
    tk.Label(head, text=tool_name,
             bg=ACC, fg='#ffffff',
             font=(UI, 10, 'bold'),
             padx=9, pady=4).pack(side='left')
    tk.Label(head, text='  请求执行操作',
             bg=BG, fg=TEXT, font=(UI, 11, 'bold')).pack(side='left', pady=2)

    tk.Frame(root, bg=DIV, height=1).pack(fill='x', padx=16, pady=(10, 10))

    if desc:
        desc_f = tk.Frame(root, bg=CARD_BG, highlightbackground=CARD_BD, highlightthickness=1)
        desc_f.pack(fill='x', padx=16, pady=(0, 6))
        desc_label = tk.Label(desc_f, text=f'🎀  {desc}',
                              bg=CARD_BG, fg=TEXT,
                              font=(UI, 10, 'bold'),
                              padx=12, pady=8, justify='left',
                              anchor='w')
        desc_label.pack(fill='x')

        def adj_desc_wrap():
            w = desc_f.winfo_width()
            if w > 28:
                desc_label.configure(wraplength=w - 28)

        root.after(10, adj_desc_wrap)

    if detail:
        code_f = tk.Frame(root, bg=CODE_BG, highlightbackground=CODE_BD, highlightthickness=1)
        code_f.pack(fill='x', padx=16, pady=(0, 6))
        line_count = detail.count('\n') + 1
        box_cols = _detail_cols(detail)
        visual_lines = max(
            line_count,
            max((len(line) + box_cols - 1) // box_cols for line in detail.splitlines() or [''])
        )
        box_height = min(max(visual_lines, 1), 4)

        box = tk.Text(code_f, font=(MONO, 10), fg=CODE_FG, bg=CODE_BG,
                      wrap='char', height=box_height, width=box_cols, bd=0,
                      padx=10, pady=8, cursor='arrow', relief='flat',
                      highlightthickness=0, takefocus=0)
        box.insert('1.0', detail)
        box.configure(state='disabled')
        box.pack(side='left', fill='both', expand=True)

        if visual_lines > 4:
            sb = tk.Scrollbar(code_f, command=box.yview, bd=0,
                              troughcolor=CODE_BG, activebackground=ACC,
                              elementborderwidth=0, highlightthickness=0)
            sb.pack(side='right', fill='y')
            box.configure(yscrollcommand=sb.set)

    bf = tk.Frame(root, bg=BG)
    bf.pack(fill='x', padx=16, pady=(6, 10))

    def act(allow, rem=False):
        if done['ok']:
            return
        done['ok'] = True
        if rem:
            _remember(tool_name, tool_input)
        if allow:
            os.write(1, b'{"continue": true}\n')
        else:
            sys.stderr.write('user denied\n')
            sys.stderr.flush()
            sys.exit(2)
        root.after(40, root.quit)

    tk.Button(bf, text='拒绝', command=lambda: act(False),
              bg=DEN, fg='#ffffff', font=(UI, 10),
              activebackground=DEN_HV, activeforeground='#ffffff',
              relief='flat', padx=12, pady=4, cursor='hand2', bd=0).pack(side='right', padx=(5, 0))

    tk.Button(bf, text='记住', command=lambda: act(True, True),
              bg=ACC, fg='#ffffff', font=(UI, 10),
              activebackground=ACC_HV, activeforeground='#ffffff',
              relief='flat', padx=12, pady=4, cursor='hand2', bd=0).pack(side='right', padx=(5, 0))

    btn_ok = tk.Button(bf, text='同意', command=lambda: act(True),
                       bg=BG, fg=ACC, font=(UI, 10),
                       activebackground=CARD_BG, activeforeground=ACC_HV,
                       relief='flat', padx=16, pady=4, cursor='hand2',
                       bd=0, highlightthickness=1, highlightbackground=ACC)
    btn_ok.pack(side='right')

    root.bind('<Return>', lambda e: act(True))
    root.protocol('WM_DELETE_WINDOW', lambda: act(False))

    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    max_w = int(root.winfo_screenwidth() * 0.6)
    max_h = int(root.winfo_screenheight() * 0.65)
    _center(root, min(max(w, 460), max_w), min(h, max_h))

    _show_smooth(root, btn_ok)
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass
    sys.exit(0)


def main():
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            return
        data = json.loads(raw.decode('utf-8'))
    except Exception:
        return
    try:
        show(data)
    except Exception:
        pass


if __name__ == '__main__':
    main()
