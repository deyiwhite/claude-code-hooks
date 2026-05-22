#!/usr/bin/env python3
"""Claude Code PreToolUse hook - permission dialog."""

import sys, os, json, tkinter as tk


if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

# ── 配色 ────────────────────────────────────────────────────────────────────
BG      = '#faf7ff'
CARD_BG = '#f5eeff'
CARD_BD = '#ddd0f0'
CODE_BG = '#f0eaf8'
CODE_BD = '#d5c5e0'
DIV     = '#e8d8f0'
TEXT    = '#3d2460'
SUB     = '#6b4f8a'
CODE_FG = '#4a3070'
ACC     = '#9c6cd4'
DEN     = '#c2788a'
DEN_HV  = '#b0687a'
MEM_HV  = '#8a5dc0'

# ── 字体 ─────────────────────────────────────────────────────────────────────
UI   = 'Segoe UI'
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


SKIP_KEYS = {'description', 'timeout'}

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


def _remember(tool_name, tool_input):
    rule = f'{tool_name}(*)'
    if tool_name == 'Bash':
        cmd = tool_input.get('command', '')
        # Only embed the command if it's a clean single-line, short command.
        # Multi-line scripts and long commands would produce invalid JSON rules.
        if cmd and '\n' not in cmd and len(cmd) <= 80:
            rule = f'{tool_name}({cmd})'
    # Write to the current project's .claude/settings.local.json,
    # not the hooks project's config. Falls back to global if cwd has no .claude.
    project_config = os.path.join(os.getcwd(), '.claude', 'settings.local.json')
    global_config = os.path.join(os.path.expanduser('~'), '.claude', 'settings.local.json')
    targets = [project_config]
    if project_config != global_config:
        targets.append(global_config)
    for p in targets:
        try:
            s = json.load(open(p, 'r', encoding='utf-8')) if os.path.exists(p) else {}
            s.setdefault('permissions', {}).setdefault('allow', [])
            if rule not in s['permissions']['allow']:
                s['permissions']['allow'].append(rule)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            json.dump(s, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        except Exception:
            pass


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
    root.title('Claude Code')
    root.resizable(False, False)
    root.configure(bg=BG)

    # ── 顶部彩虹条 ──────────────────────────────────────────────────────────
    rainbow = tk.Canvas(root, height=3, bg=BG, highlightthickness=0)
    rainbow.pack(fill='x')
    colors = ['#fda4af', '#fdba74', '#fde68a', '#a7f3d0', '#93c5fd', '#c4b5fd', '#f9a8d4']
    def _draw_rainbow(event=None):
        rainbow.delete('all')
        w = rainbow.winfo_width() or 460
        seg = w / len(colors)
        for i, c in enumerate(colors):
            rainbow.create_rectangle(i * seg, 0, (i + 1) * seg, 3, fill=c, outline='')
    rainbow.bind('<Configure>', _draw_rainbow)

    # ── 标题栏 ───────────────────────────────────────────────────────────────
    head = tk.Frame(root, bg=BG)
    head.pack(fill='x', padx=16, pady=(10, 0))

    badge = tk.Label(head, text=f' {tool_name} ',
                     bg=ACC, fg='#ffffff',
                     font=(UI, 9, 'bold'),
                     padx=6, pady=2)
    badge.pack(side='left')

    tk.Label(head, text='  请求执行操作',
             bg=BG, fg=TEXT,
             font=(UI, 11, 'bold')).pack(side='left', pady=2)

    tk.Frame(root, bg=DIV, height=1).pack(fill='x', padx=16, pady=(6, 8))

    # ── description 卡片 ─────────────────────────────────────────────────────
    if desc:
        desc_f = tk.Frame(root, bg=CARD_BG,
                          highlightbackground=CARD_BD, highlightthickness=1)
        desc_f.pack(fill='x', padx=16, pady=(0, 6))

        desc_label = tk.Label(desc_f, text=f'\U0001f380  {desc}',
                 bg=CARD_BG, fg=TEXT,
                 font=(UI, 11, 'bold'),
                 padx=10, pady=6,
                 justify='left')
        desc_label.pack(fill='x')

        def _adj_wrap():
            w = desc_f.winfo_width()
            if w > 20:
                desc_label.configure(wraplength=w - 20)
        root.after(10, _adj_wrap)

    # ── 命令详情框 ───────────────────────────────────────────────────────────
    if detail:
        code_f = tk.Frame(root, bg=CODE_BG,
                          highlightbackground=CODE_BD, highlightthickness=1)
        code_f.pack(fill='x', padx=16, pady=(0, 4))

        line_count = detail.count('\n') + 1
        box_height = min(line_count, 5)

        box = tk.Text(code_f,
                      font=(MONO, 10),
                      fg=CODE_FG, bg=CODE_BG,
                      wrap='char',
                      height=box_height,
                      bd=0, padx=10, pady=8,
                      cursor='arrow', relief='flat',
                      highlightthickness=0, takefocus=0)
        box.insert('1.0', detail)
        box.configure(state='disabled')
        box.pack(side='left', fill='both', expand=True)

        if line_count > 5:
            sb = tk.Scrollbar(code_f, command=box.yview, bd=0,
                              troughcolor=CODE_BG, activebackground=ACC,
                              elementborderwidth=0, highlightthickness=0)
            sb.pack(side='right', fill='y')
            box.configure(yscrollcommand=sb.set)

    # ── 按钮区 ───────────────────────────────────────────────────────────────
    bf = tk.Frame(root, bg=BG)
    bf.pack(fill='x', padx=16, pady=(6, 8))

    # 空占位，保持按钮右对齐

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
        root.after(50, root.quit)

    # 拒绝: 实心
    tk.Button(bf, text='拒绝',
              command=lambda: act(False),
              bg=DEN, fg='#ffffff',
              font=(UI, 10),
              activebackground=DEN_HV, activeforeground='#ffffff',
              relief='flat', padx=14, pady=6,
              cursor='hand2', bd=0
              ).pack(side='right', padx=(6, 0))

    # 记住: 实心
    tk.Button(bf, text='记住',
              command=lambda: act(True, True),
              bg=ACC, fg='#ffffff',
              font=(UI, 10),
              activebackground=MEM_HV, activeforeground='#ffffff',
              relief='flat', padx=14, pady=6,
              cursor='hand2', bd=0
              ).pack(side='right', padx=(6, 0))

    # 同意: 描边轮廓
    btn_ok = tk.Button(bf, text='同意',
                       command=lambda: act(True),
                       bg=BG, fg=ACC,
                       font=(UI, 10),
                       activebackground=CARD_BG, activeforeground=ACC,
                       relief='flat', padx=18, pady=6,
                       cursor='hand2', bd=0,
                       highlightthickness=1, highlightbackground=ACC)
    btn_ok.pack(side='right')

    # ── 快捷键 ────────────────────────────────────────────────────────────────
    root.bind('<Return>', lambda e: act(True, True))
    root.protocol('WM_DELETE_WINDOW', lambda: act(False))

    # ── 计算窗口尺寸 ──────────────────────────────────────────────────────────
    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    max_w = int(root.winfo_screenwidth() * 0.6)
    max_h = int(root.winfo_screenheight() * 0.65)
    _center(root, min(max(w, 460), max_w), min(h, max_h))

    _focus(root, btn_ok)
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            return  # no stdin data — let Claude Code decide
        data = json.loads(raw.decode())
    except Exception:
        return  # parse error — let Claude Code decide
    try:
        show(data)
    except Exception:
        pass  # dialog crashed — let Claude Code decide


if __name__ == '__main__':
    main()
