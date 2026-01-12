import os
import json
import sqlite3
import webbrowser
from datetime import datetime, date
from urllib.parse import quote_plus, quote

import requests
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# Basic config
API_BASE = os.getenv("NEWS_API_BASE", "http://127.0.0.1:8000")
DB_FILE = "websearch_sessions.db"
DOCK_PANEL_WIDTH = 520


# ---------------------------
# Database helpers (from pasted script)
# ---------------------------


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_session_to_db(name: str, data: dict):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        payload = json.dumps(data)
        created_at = datetime.utcnow().isoformat(timespec="seconds")
        cur.execute(
            """
            INSERT INTO sessions (name, data, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                data=excluded.data,
                created_at=excluded.created_at
            """,
            (name, payload, created_at),
        )
        conn.commit()
    finally:
        conn.close()


def load_session_from_db(name: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT data FROM sessions WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        return None


def list_sessions():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name, created_at FROM sessions ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def import_sessions_list_to_db(sessions_list, overwrite_existing: bool):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        for sess in sessions_list:
            name = sess.get("name")
            data = sess.get("data")
            created_at = sess.get("created_at") or datetime.utcnow().isoformat(timespec="seconds")
            if not name or data is None:
                continue
            payload = json.dumps(data)
            if overwrite_existing:
                cur.execute(
                    """
                    INSERT INTO sessions (name, data, created_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        data=excluded.data,
                        created_at=excluded.created_at
                    """,
                    (name, payload, created_at),
                )
            else:
                cur.execute(
                    "INSERT OR IGNORE INTO sessions (name, data, created_at) VALUES (?, ?, ?)",
                    (name, payload, created_at),
                )
        conn.commit()
    finally:
        conn.close()


# ---------------------------
# Query / URL helpers (from pasted script)
# ---------------------------


def build_query(keyword: str, date_str: str = "", domain: str = "") -> str:
    parts = []
    if keyword:
        parts.append(keyword)
    if date_str:
        parts.append(date_str)
    if domain:
        parts.append(f"site:{domain}")
    return " ".join(parts).strip()


def route_query(query: str, base_url: str) -> str:
    if not base_url:
        return ""

    if "{query}" in base_url:
        pos_placeholder = base_url.find("{query}")
        pos_qmark = base_url.find('?')
        if pos_qmark == -1 or pos_placeholder < pos_qmark:
            q_encoded = quote(query, safe='') if query else ""
        else:
            q_encoded = quote_plus(query) if query else ""
        return base_url.replace("{query}", q_encoded)

    if "?" in base_url:
        return f"{base_url}&q={quote_plus(query)}" if query else base_url

    return f"{base_url}?q={quote_plus(query)}" if query else base_url


# ---------------------------
# Tk UI client adapted
# ---------------------------


class TkClient:
    def __init__(self, api_base=API_BASE):
        self.api_base = api_base.rstrip('/')
        self.root = tk.Tk()
        self.root.title('Web Search Tool (Tk client)')
        self.root.geometry('1200x900')
        self.news_sources = {}

        # UI state
        self.row_entries = []
        self.global_keyword_var = tk.StringVar()
        self.global_date_var = tk.StringVar()
        self.session_name_var = tk.StringVar()
        self.sessions_combobox = None

        init_db()
        self.build_ui()

    def fetch_sources(self):
        try:
            r = requests.get(f"{self.api_base}/api/sources", timeout=5)
            r.raise_for_status()
            data = r.json()
            # expected mapping: {category: {source: template}}
            self.news_sources = data
            return True
        except Exception as e:
            messagebox.showerror('Error', f'Failed to fetch sources from API: {e}')
            return False

    def add_row(self):
        frame = tk.Frame(self.rows_frame)
        frame.pack(fill='x', pady=2)

        url_var = tk.StringVar()
        keyword_var = tk.StringVar()

        col_url = tk.Frame(frame)
        col_url.pack(side='left', padx=5)
        tk.Label(col_url, text='URL', anchor='w').pack(anchor='w')
        tk.Entry(col_url, textvariable=url_var, width=56).pack()

        col_kw = tk.Frame(frame)
        col_kw.pack(side='left', padx=5)
        tk.Label(col_kw, text='Keyword', anchor='w').pack(anchor='w')
        tk.Entry(col_kw, textvariable=keyword_var, width=48).pack()

        self.row_entries.append({'frame': frame, 'url': url_var, 'keyword': keyword_var})

    def ensure_rows(self, n: int):
        while len(self.row_entries) < n:
            self.add_row()

    def clear_all_rows(self):
        for r in self.row_entries:
            r['frame'].destroy()
        self.row_entries = []
        self.ensure_rows(6)

    def insert_source_bottom(self, url: str, keyword: str):
        for r in self.row_entries:
            if r['url'].get().strip() == '':
                r['url'].set(url)
                r['keyword'].set(keyword)
                return
        self.add_row()
        r = self.row_entries[-1]
        r['url'].set(url)
        r['keyword'].set(keyword)

    def open_all(self):
        date_val = self.global_date_var.get().strip()
        for r in self.row_entries:
            url_template = r['url'].get().strip()
            keyword = r['keyword'].get().strip()
            if not url_template:
                continue
            query = build_query(keyword, date_val, '')
            final_url = route_query(query, url_template)
            # open in a new browser tab when possible
            try:
                webbrowser.open(final_url, new=2)
            except Exception:
                webbrowser.open(final_url)

    def export_current_rows_to_file(self):
        rows_data = []
        for r in self.row_entries:
            url = r['url'].get().strip()
            keyword = r['keyword'].get().strip()
            if not (url or keyword):
                continue
            rows_data.append({'url': url, 'keyword': keyword})
        if not rows_data:
            messagebox.showinfo('Export', 'No row data to export.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
        if not path:
            return
        payload = {'exported_at': datetime.utcnow().isoformat(timespec='seconds'), 'rows': rows_data}
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            messagebox.showinfo('Export', f'Current rows exported to:\n{path}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export rows: {e}')

    def export_all_sessions_to_file(self):
        sessions = list_sessions()
        if not sessions:
            messagebox.showinfo('Export', 'No saved sessions to export.')
            return
        sessions_payload = []
        for name, created_at in sessions:
            sess = load_session_from_db(name)
            if sess is None:
                continue
            sessions_payload.append({'name': name, 'created_at': created_at, 'data': sess})
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({'exported_at': datetime.utcnow().isoformat(timespec='seconds'), 'sessions': sessions_payload}, f, indent=2, ensure_ascii=False)
            messagebox.showinfo('Export', f'All sessions exported to:\n{path}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export sessions: {e}')

    def import_sessions_from_file(self):
        path = filedialog.askopenfilename(filetypes=[('JSON files', '*.json'), ('All files', '*.*')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror('Import Error', f'Failed to read file: {e}')
            return
        sessions_list = None
        if isinstance(data, dict) and 'sessions' in data and isinstance(data['sessions'], list):
            sessions_list = data['sessions']
        elif isinstance(data, list):
            sessions_list = data
        else:
            messagebox.showerror('Import Error', "JSON format not recognized. Must be a list or contain 'sessions' key.")
            return
        if not sessions_list:
            messagebox.showinfo('Import', 'No sessions found in the file.')
            return
        overwrite = messagebox.askyesno('Import Sessions', 'Overwrite existing sessions with the same name?')
        try:
            import_sessions_list_to_db(sessions_list, overwrite)
            self.refresh_sessions_combobox()
            messagebox.showinfo('Import', f'Imported {len(sessions_list)} session(s) from:\n{path}')
        except Exception as e:
            messagebox.showerror('Import Error', f'Failed to import sessions: {e}')

    def save_session_with_name(self, name: str):
        if not name:
            messagebox.showerror('Save Session', 'Session name cannot be empty.')
            return
        rows_data = []
        for r in self.row_entries:
            rows_data.append({'url': r['url'].get().strip(), 'keyword': r['keyword'].get().strip()})
        payload = {'rows': rows_data}
        save_session_to_db(name, payload)
        self.refresh_sessions_combobox()
        messagebox.showinfo('Saved', f"Session '{name}' saved successfully.")

    def refresh_sessions_combobox(self):
        sessions = list_sessions()
        names = [n for n, _ in sessions]
        if self.sessions_combobox:
            self.sessions_combobox['values'] = names
            if names:
                self.sessions_combobox.set(names[0])
            else:
                self.sessions_combobox.set('')

    def load_session_into_rows(self, name: str):
        data = load_session_from_db(name)
        if not data:
            messagebox.showerror('Error', f"Session '{name}' not found or invalid.")
            return
        self.clear_all_rows()
        rows = data.get('rows', [])
        for row in rows:
            self.add_row()
            r = self.row_entries[-1]
            r['url'].set(row.get('url', ''))
            r['keyword'].set(row.get('keyword', ''))

    def build_news_sources_panel(self, parent):
        panel = tk.Frame(parent, width=DOCK_PANEL_WIDTH)
        panel.pack_propagate(False)

        nb = ttk.Notebook(panel)
        nb.pack(fill='both', expand=True, padx=4, pady=4)

        self.news_vars = {}
        self.region_kw_vars = {}

        cb_wrap = DOCK_PANEL_WIDTH - 60

        for region, sources in self.news_sources.items():
            tab = tk.Frame(nb)
            nb.add(tab, text=region)

            search_frame = tk.Frame(tab)
            search_frame.pack(fill='x', padx=6, pady=(6, 2))
            tk.Label(search_frame, text='Filter:').pack(side='left')
            search_var = tk.StringVar()
            tk.Entry(search_frame, textvariable=search_var, width=30).pack(side='left', padx=(6, 4))

            sc_container, sc_inner, _ = self.make_scrollable_frame(tab)
            sc_container.pack(fill='both', expand=True, padx=6, pady=4)

            region_map = {}
            for name, url in sources.items():
                var = tk.BooleanVar(value=False)
                cb = tk.Checkbutton(sc_inner, text=name, variable=var, anchor='w', justify='left', wraplength=cb_wrap)
                cb.pack(anchor='w', fill='x', padx=2, pady=1)
                region_map[name] = (var, url, cb)
            self.news_vars[region] = region_map

            controls = tk.Frame(tab)
            controls.pack(fill='x', padx=6, pady=6)

            tk.Label(controls, text='Keyword:').grid(row=0, column=0, sticky='w')
            kw_var = tk.StringVar()
            tk.Entry(controls, textvariable=kw_var, width=30).grid(row=0, column=1, sticky='w', padx=(6, 4))
            self.region_kw_vars[region] = kw_var

            def select_all_region(r=region):
                for v, _u, _cb in self.news_vars[r].values():
                    v.set(True)

            def clear_all_region(r=region):
                for v, _u, _cb in self.news_vars[r].values():
                    v.set(False)

            def add_selected_region(r=region):
                keyword = self.region_kw_vars[r].get().strip() or self.global_keyword_var.get().strip()
                added = 0
                for name, (v, url_template, _cb) in self.news_vars[r].items():
                    if v.get():
                        self.insert_source_bottom(url_template, keyword)
                        added += 1
                if added == 0:
                    messagebox.showinfo('No selection', 'No sources selected.')
                else:
                    messagebox.showinfo('Added', f'Added {added} source(s) to the rows.')

            btn_frame = tk.Frame(tab)
            btn_frame.pack(fill='x', padx=6, pady=(0, 6))
            tk.Button(btn_frame, text='Select All', command=select_all_region).pack(side='left', padx=2)
            tk.Button(btn_frame, text='Clear All', command=clear_all_region).pack(side='left', padx=2)
            tk.Button(btn_frame, text='Add Selected', command=add_selected_region).pack(side='left', padx=8)

            def make_filter_callback(sv, r=region):
                def on_change(*a):
                    q = sv.get().strip().lower()
                    for name, (_v, _u, cb) in self.news_vars[r].items():
                        visible = (q == '') or (q in name.lower())
                        if visible:
                            cb.pack(anchor='w', fill='x', padx=2, pady=1)
                        else:
                            cb.pack_forget()
                return on_change

            search_var.trace_add('write', make_filter_callback(search_var, region))

        return panel

    def make_scrollable_frame(self, parent):
        container = tk.Frame(parent)
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vsb = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas)

        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        return container, inner, canvas

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x', pady=10)

        tk.Label(top_frame, text='Global Keyword:').pack(side='left', padx=5)
        tk.Entry(top_frame, textvariable=self.global_keyword_var, width=30).pack(side='left', padx=5)

        tk.Label(top_frame, text='Session Name:').pack(side='left', padx=(15, 5))
        tk.Entry(top_frame, textvariable=self.session_name_var, width=25).pack(side='left', padx=5)
        tk.Button(top_frame, text='Save Session', command=lambda: self.save_session_with_name(self.session_name_var.get().strip())).pack(side='left', padx=5)

        tk.Label(top_frame, text='Saved Sessions:').pack(side='left', padx=(15, 5))
        self.sessions_combobox = ttk.Combobox(top_frame, values=[], width=30, state='readonly')
        self.sessions_combobox.pack(side='left', padx=5)
        tk.Button(top_frame, text='Load Session', command=lambda: self.load_session_into_rows(self.sessions_combobox.get().strip())).pack(side='left', padx=5)
        tk.Button(top_frame, text='Refresh', command=self.refresh_sessions_combobox).pack(side='left', padx=5)

        news_btn = tk.Menubutton(top_frame, text='News Sources', relief='raised')
        news_btn.pack(side='left', padx=10)
        news_menu = tk.Menu(news_btn, tearoff=0)
        news_menu.add_command(label='Export Current Rows...', command=self.export_current_rows_to_file)
        news_menu.add_command(label='Export All Sessions...', command=self.export_all_sessions_to_file)
        news_menu.add_command(label='Import Sessions...', command=self.import_sessions_from_file)
        news_btn.config(menu=news_menu)

        tk.Button(top_frame, text='Open All', command=self.open_all, bg='red', fg='yellow').pack(side='left', padx=10)
        tk.Button(top_frame, text='Clear All', command=self.clear_all_rows).pack(side='left', padx=5)

        tk.Label(top_frame, text='Date:').pack(side='left', padx=(8, 2))
        tk.Entry(top_frame, textvariable=self.global_date_var, width=12).pack(side='left', padx=(0, 6))
        tk.Button(top_frame, text='Today', command=lambda: self.global_date_var.set(date.today().isoformat())).pack(side='left', padx=(0, 4))
        tk.Button(top_frame, text='Clear Date', command=lambda: self.global_date_var.set('')).pack(side='left', padx=(0, 8))

        pw = tk.PanedWindow(self.root, orient='horizontal')
        pw.pack(fill='both', expand=True)

        right_container = tk.Frame(pw)
        pw.add(right_container)

        # fetch sources and build news panel
        ok = self.fetch_sources()
        news_panel = self.build_news_sources_panel(pw) if ok else tk.Frame(pw)
        pw.add(news_panel)

        container = tk.Frame(right_container)
        container.pack(fill='both', expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        self.rows_frame = tk.Frame(canvas)
        self.rows_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.rows_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.ensure_rows(6)
        self.refresh_sessions_combobox()

    def run(self):
        try:
            self.root.state('zoomed')
        except Exception:
            pass
        self.root.mainloop()


if __name__ == '__main__':
    app = TkClient()
    app.run()
