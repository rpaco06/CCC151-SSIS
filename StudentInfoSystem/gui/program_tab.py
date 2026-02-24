import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, StringVar, Toplevel
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database import load_programs, save_programs, get_college_codes, PROGRAM_FIELDS
from validator import validate_program, is_duplicate

FIELDS = PROGRAM_FIELDS
NAV    = "#0d1b2a"
ACCENT = "#1b4f72"
BG     = "#f5f7fa"
WHITE  = "#ffffff"
TEXT   = "#1a1a2a"
GREY   = "#6c757d"


def styled_entry(parent, textvariable, width=24):
    e = tk.Entry(parent, textvariable=textvariable,
                 font=("Segoe UI", 10), width=width,
                 relief="flat", bd=0, bg="#eef1f7",
                 fg=TEXT, insertbackground=TEXT)
    e.config(highlightthickness=2,
             highlightbackground="#dde3ee",
             highlightcolor=ACCENT)
    return e


class ProgramTab:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg=BG)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        tk.Label(self.parent, text="Programs",
                 font=("Georgia", 20, "bold"),
                 bg=BG, fg=NAV).pack(anchor="w", padx=25, pady=(20, 5))

        toolbar = tk.Frame(self.parent, bg=BG)
        toolbar.pack(fill="x", padx=25, pady=(0, 8))

        tk.Label(toolbar, text="Search",
                 font=("Segoe UI", 10), bg=BG, fg=GREY).pack(side="left")
        self.search_var = StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        se = styled_entry(toolbar, self.search_var, width=26)
        se.pack(side="left", padx=(6, 20), ipady=5)

        tk.Label(toolbar, text="Sort by",
                 font=("Segoe UI", 10), bg=BG, fg=GREY).pack(side="left")
        self.sort_var = StringVar(value="code")
        sort_cb = tb.Combobox(toolbar, textvariable=self.sort_var,
                              values=[f.capitalize() for f in FIELDS],
                              width=12, state="readonly", bootstyle="secondary")
        sort_cb.pack(side="left", padx=6)
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Frame(toolbar, bg=BG).pack(side="left", expand=True)
        tb.Button(toolbar, text="🗑  Delete",
                  bootstyle="secondary", command=self.delete,
                  width=10).pack(side="right", padx=(5,0))
        tb.Button(toolbar, text="＋  Add Program",
                  bootstyle="dark", command=self.open_add_dialog,
                  width=14).pack(side="right")
        table_frame = tk.Frame(self.parent, bg=BG)
        table_frame.pack(fill="both", expand=True, padx=25, pady=5)

        

        cols = ("code", "name", "college", "actions")
        self.tree = tb.Treeview(table_frame, columns=cols,
                                show="headings", height=14,
                                bootstyle="primary")
        self.tree.heading("code",    text="CODE")
        self.tree.heading("name",    text="NAME")
        self.tree.heading("college", text="COLLEGE")
        self.tree.heading("actions", text="")
        self.tree.column("code",    width=130, anchor="w")
        self.tree.column("name",    width=330, anchor="w")
        self.tree.column("college", width=120, anchor="w")
        self.tree.column("actions", width=80,  anchor="center")

        scroll = tb.Scrollbar(table_frame, orient="vertical",
                              command=self.tree.yview,
                              bootstyle="secondary-round")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.tag_configure("odd",  background="#f0f4fb")
        self.tree.tag_configure("even", background=WHITE)
        
        # row heights for text size since it wont worrk as usual
        big_font = tk.font.Font(family="Segoe UI", size=14)
        self.tree.configure(style="Treeview")
        style = tb.Style()
        style.configure("Treeview", rowheight=44, font=big_font)
        self.tree.bind("<ButtonRelease-1>", self.on_click)

        toolbar = tk.Frame(self.parent, bg=BG)
        toolbar.pack(fill="x", padx=25, pady=(0, 8))

        tb.Button(toolbar, text="🗑  Delete Selected",
                  bootstyle="secondary", command=self.delete,
                  width=18).pack(side="right")

    def refresh(self):
        q = self.search_var.get().lower()
        sort_field = self.sort_var.get().lower()
        rows = [r for r in load_programs()
                if any(q in r[f].lower() for f in FIELDS)]
        rows.sort(key=lambda r: r.get(sort_field, ""))
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end",
                             values=(r["code"], r["name"],
                                     r["college"], "✏ Edit"),
                             tags=(tag,))

    def on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        col    = self.tree.identify_column(event.x)
        row    = self.tree.identify_row(event.y)
        if region == "cell" and col == "#4" and row:
            vals = self.tree.item(row)["values"]
            self.open_edit_dialog(vals[0], vals[1], vals[2])

    def open_add_dialog(self):
        self._open_dialog("Add Program", "", "", "")

    def open_edit_dialog(self, code, name, college):
        self._open_dialog("Edit Program", code, name, college)

    def _open_dialog(self, title, code, name, college):
        win = Toplevel()
        win.title(title)
        win.geometry("420x310")
        win.configure(bg=WHITE)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=title, font=("Georgia", 14, "bold"),
                 bg=WHITE, fg=NAV).pack(anchor="w", padx=20, pady=(18, 10))

        form = tk.Frame(win, bg=WHITE)
        form.pack(fill="x", padx=20)
        form.columnconfigure(0, weight=1)

        code_var    = StringVar(value=code)
        name_var    = StringVar(value=name)
        college_var = StringVar(value=college)
        is_edit     = bool(code)

        tk.Label(form, text="Code", font=("Segoe UI", 10),
                 bg=WHITE, fg=GREY).grid(row=0, column=0, sticky="w", pady=(0,2))
        code_entry = styled_entry(form, code_var, width=36)
        code_entry.grid(row=1, column=0, pady=(0, 8), ipady=5, sticky="ew")
        if is_edit:
            code_entry.configure(state="disabled", bg="#e8ecf3")

        tk.Label(form, text="Name", font=("Segoe UI", 10),
                 bg=WHITE, fg=GREY).grid(row=2, column=0, sticky="w", pady=(0,2))
        styled_entry(form, name_var, width=36).grid(
            row=3, column=0, pady=(0, 8), ipady=5, sticky="ew")

        tk.Label(form, text="College", font=("Segoe UI", 10),
                 bg=WHITE, fg=GREY).grid(row=4, column=0, sticky="w", pady=(0,2))
        college_cb = tb.Combobox(form, textvariable=college_var,
                                 values=get_college_codes(),
                                 width=34, state="readonly",
                                 bootstyle="secondary")
        college_cb.grid(row=5, column=0, pady=(0, 12), sticky="ew")

        def save():
            data = {"code":    code_var.get().strip(),
                    "name":    name_var.get().strip(),
                    "college": college_var.get().strip()}
            err = validate_program(data)
            if err:
                return messagebox.showwarning("Warning", err, parent=win)
            rows = load_programs()
            if is_edit:
                found = False
                for r in rows:
                    if r["code"] == data["code"]:
                        r.update(data); found = True
                if not found:
                    return messagebox.showerror("Error", "Program not found.", parent=win)
            else:
                if is_duplicate(rows, "code", data["code"]):
                    return messagebox.showerror("Error", "Code already exists.", parent=win)
                rows.append(data)
            save_programs(rows)
            self.refresh()
            win.destroy()

        tb.Button(win, text="Save", bootstyle="dark",
                  command=save, width=12).pack(pady=4)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Warning", "Select a row first.")
        code = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete program '{code}'?"):
            return
        rows = [r for r in load_programs() if r["code"] != code]
        save_programs(rows)
        self.refresh()