import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ── DATABASE SETUP ──────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("employees.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            age       INTEGER NOT NULL,
            gender    TEXT    NOT NULL,
            dob       TEXT    NOT NULL,
            contact   TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_conn():
    return sqlite3.connect("employees.db")


# ── MAIN APPLICATION ─────────────────────────────────────────
class EMS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System")
        self.geometry("1050x640")
        self.resizable(True, True)
        self.configure(bg="#0f1117")

        # colour palette
        self.C = {
            "bg":      "#0f1117",
            "surface": "#1a1c26",
            "card":    "#22253a",
            "accent":  "#c8f055",
            "accent2": "#7ef0c0",
            "text":    "#f0eeea",
            "muted":   "#8888a0",
            "danger":  "#f05555",
            "border":  "#2e3148",
        }
        C = self.C

        init_db()
        self._build_ui()
        self._load_table()

    # ── BUILD UI ────────────────────────────────────────────
    def _build_ui(self):
        C = self.C

        # ── Title bar
        title_frame = tk.Frame(self, bg=C["surface"], pady=12)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="⚡  Employee Management System",
                 font=("Segoe UI", 16, "bold"),
                 bg=C["surface"], fg=C["accent"]).pack(side="left", padx=20)
        tk.Label(title_frame, text="Python + SQLite",
                 font=("Segoe UI", 9),
                 bg=C["surface"], fg=C["muted"]).pack(side="right", padx=20)

        # ── Main container
        main = tk.Frame(self, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # LEFT — Form
        left = tk.Frame(main, bg=C["surface"], bd=0,
                        highlightthickness=1,
                        highlightbackground=C["border"],
                        width=310)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="Employee Details",
                 font=("Segoe UI", 11, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(18, 14))

        # form fields
        fields = [
            ("Full Name",    "name_var"),
            ("Age",          "age_var"),
            ("Gender",       "gender_var"),
            ("Date of Birth","dob_var"),
            ("Contact",      "contact_var"),
        ]

        self.name_var    = tk.StringVar()
        self.age_var     = tk.StringVar()
        self.gender_var  = tk.StringVar()
        self.dob_var     = tk.StringVar()
        self.contact_var = tk.StringVar()

        for label, var_name in fields:
            frm = tk.Frame(left, bg=C["surface"])
            frm.pack(fill="x", padx=18, pady=5)

            tk.Label(frm, text=label,
                     font=("Segoe UI", 9),
                     bg=C["surface"], fg=C["muted"],
                     anchor="w").pack(fill="x")

            if var_name == "gender_var":
                cb = ttk.Combobox(frm, textvariable=getattr(self, var_name),
                                  values=["Male", "Female", "Other"],
                                  state="readonly", font=("Segoe UI", 10))
                cb.pack(fill="x", ipady=4)
                self._style_combo(cb)
            else:
                placeholder = ""
                if var_name == "dob_var":
                    placeholder = "DD-MM-YYYY"
                ent = tk.Entry(frm, textvariable=getattr(self, var_name),
                               font=("Segoe UI", 10),
                               bg=C["card"], fg=C["text"],
                               insertbackground=C["accent"],
                               relief="flat", bd=0,
                               highlightthickness=1,
                               highlightbackground=C["border"],
                               highlightcolor=C["accent"])
                ent.pack(fill="x", ipady=6)
                if placeholder:
                    self._add_placeholder(ent, placeholder, getattr(self, var_name))

        # hidden id
        self.edit_id = None

        # ── Buttons
        btn_frame = tk.Frame(left, bg=C["surface"])
        btn_frame.pack(fill="x", padx=18, pady=(20, 10))

        buttons = [
            ("➕  Add",     self._add,    C["accent"],  "#0f1117"),
            ("✏️  Update",  self._update, C["accent2"], "#0f1117"),
            ("🗑️  Delete",  self._delete, C["danger"],  "#ffffff"),
            ("🔄  Clear",   self._clear,  C["border"],  C["text"]),
        ]

        for i, (txt, cmd, bg, fg) in enumerate(buttons):
            r, c = divmod(i, 2)
            btn = tk.Button(btn_frame, text=txt, command=cmd,
                            bg=bg, fg=fg,
                            font=("Segoe UI", 9, "bold"),
                            relief="flat", bd=0,
                            activebackground=bg,
                            activeforeground=fg,
                            padx=8, pady=7,
                            cursor="hand2")
            btn.grid(row=r, column=c, sticky="ew", padx=4, pady=4)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # RIGHT — Table
        right = tk.Frame(main, bg=C["surface"],
                         highlightthickness=1,
                         highlightbackground=C["border"])
        right.pack(side="left", fill="both", expand=True)

        # Search bar
        search_frame = tk.Frame(right, bg=C["surface"])
        search_frame.pack(fill="x", padx=14, pady=(14, 6))

        tk.Label(search_frame, text="🔍",
                 bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI", 11)).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._search())
        search_ent = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=("Segoe UI", 10),
                              bg=C["card"], fg=C["text"],
                              insertbackground=C["accent"],
                              relief="flat", bd=0,
                              highlightthickness=1,
                              highlightbackground=C["border"],
                              highlightcolor=C["accent"])
        search_ent.pack(side="left", fill="x", expand=True,
                        ipady=5, padx=(6, 0))

        # Table header label
        hdr = tk.Frame(right, bg=C["surface"])
        hdr.pack(fill="x", padx=14)
        tk.Label(hdr, text="All Employees",
                 font=("Segoe UI", 10, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left", pady=4)
        self.count_lbl = tk.Label(hdr, text="",
                                  font=("Segoe UI", 9),
                                  bg=C["surface"], fg=C["muted"])
        self.count_lbl.pack(side="right", pady=4)

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=C["card"],
                        foreground=C["text"],
                        rowheight=32,
                        fieldbackground=C["card"],
                        bordercolor=C["border"],
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=C["surface"],
                        foreground=C["accent"],
                        relief="flat",
                        font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", "#2e3148")],
                  foreground=[("selected", C["accent"])])

        cols = ("ID", "Name", "Age", "Gender", "DOB", "Contact")
        tree_frame = tk.Frame(right, bg=C["surface"])
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(4, 14))

        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings",
                                 style="Custom.Treeview",
                                 selectmode="browse")

        col_widths = [50, 160, 50, 80, 100, 130]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Status bar
        self.status = tk.Label(self, text="Ready",
                               font=("Segoe UI", 8),
                               bg=C["surface"], fg=C["muted"],
                               anchor="w", padx=16)
        self.status.pack(fill="x", side="bottom")

    # ── HELPERS ─────────────────────────────────────────────
    def _style_combo(self, cb):
        C = self.C
        cb.configure(background=C["card"])

    def _add_placeholder(self, entry, text, var):
        C = self.C
        def on_focus_in(e):
            if var.get() == text:
                var.set("")
                entry.config(fg=C["text"])
        def on_focus_out(e):
            if var.get() == "":
                var.set(text)
                entry.config(fg=C["muted"])
        var.set(text)
        entry.config(fg=C["muted"])
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _set_status(self, msg, color=None):
        self.status.config(text=f"  {msg}",
                           fg=color or self.C["muted"])

    def _get_fields(self):
        name    = self.name_var.get().strip()
        age     = self.age_var.get().strip()
        gender  = self.gender_var.get().strip()
        dob     = self.dob_var.get().strip()
        contact = self.contact_var.get().strip()
        return name, age, gender, dob, contact

    def _validate(self, name, age, gender, dob, contact):
        if not name or name == "":
            raise ValueError("Name cannot be empty.")
        if not age.isdigit() or not (1 <= int(age) <= 100):
            raise ValueError("Age must be a number between 1–100.")
        if gender not in ("Male", "Female", "Other"):
            raise ValueError("Please select a gender.")
        if dob == "DD-MM-YYYY" or not dob:
            raise ValueError("Please enter a date of birth (DD-MM-YYYY).")
        try:
            datetime.strptime(dob, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date format must be DD-MM-YYYY.")
        if not contact.isdigit() or len(contact) < 10:
            raise ValueError("Contact must be at least 10 digits.")

    # ── CRUD ────────────────────────────────────────────────
    def _add(self):
        try:
            n, a, g, d, c = self._get_fields()
            self._validate(n, a, g, d, c)
            conn = get_conn()
            conn.execute(
                "INSERT INTO employees (name,age,gender,dob,contact) VALUES (?,?,?,?,?)",
                (n, int(a), g, d, c)
            )
            conn.commit(); conn.close()
            self._load_table()
            self._clear()
            self._set_status(f"✅  Employee '{n}' added successfully.", self.C["accent"])
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            self._set_status(f"❌  {e}", self.C["danger"])

    def _update(self):
        if self.edit_id is None:
            messagebox.showwarning("No Selection", "Please select an employee to update.")
            return
        try:
            n, a, g, d, c = self._get_fields()
            self._validate(n, a, g, d, c)
            conn = get_conn()
            conn.execute(
                "UPDATE employees SET name=?,age=?,gender=?,dob=?,contact=? WHERE id=?",
                (n, int(a), g, d, c, self.edit_id)
            )
            conn.commit(); conn.close()
            self._load_table()
            self._clear()
            self._set_status(f"✏️  Employee updated successfully.", self.C["accent2"])
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

    def _delete(self):
        if self.edit_id is None:
            messagebox.showwarning("No Selection", "Please select an employee to delete.")
            return
        name = self.name_var.get()
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete employee '{name}'?\nThis cannot be undone."):
            return
        conn = get_conn()
        conn.execute("DELETE FROM employees WHERE id=?", (self.edit_id,))
        conn.commit(); conn.close()
        self._load_table()
        self._clear()
        self._set_status(f"🗑️  Employee '{name}' deleted.", self.C["danger"])

    def _clear(self):
        self.name_var.set("")
        self.age_var.set("")
        self.gender_var.set("")
        self.dob_var.set("DD-MM-YYYY")
        self.contact_var.set("")
        self.edit_id = None
        self.tree.selection_remove(self.tree.selection())
        self._set_status("Form cleared.")

    # ── TABLE ───────────────────────────────────────────────
    def _load_table(self, query=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        if query:
            rows = conn.execute(
                "SELECT * FROM employees WHERE name LIKE ? OR contact LIKE ?",
                (f"%{query}%", f"%{query}%")
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM employees").fetchall()
        conn.close()
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))
        self.tree.tag_configure("even", background=self.C["card"])
        self.tree.tag_configure("odd",  background="#1e2132")
        total = len(rows)
        self.count_lbl.config(text=f"{total} record{'s' if total != 1 else ''}")

    def _search(self):
        self._load_table(self.search_var.get().strip())

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.edit_id = vals[0]
        self.name_var.set(vals[1])
        self.age_var.set(vals[2])
        self.gender_var.set(vals[3])
        self.dob_var.set(vals[4])
        self.contact_var.set(vals[5])
        self._set_status(f"Selected: {vals[1]} (ID {vals[0]})", self.C["accent2"])


# ── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    app = EMS()
    app.mainloop()
