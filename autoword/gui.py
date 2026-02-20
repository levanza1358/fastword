import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from typing import Optional

from .engine import AutoWordEngine
from .storage import load_rules, rules_path, save_rules


class RuleEditor(tk.Toplevel):
    def __init__(self, master, title: str, initial: Optional[dict]):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result = None

        trigger = ""
        replacement = ""
        image_path = ""
        enabled = True
        if initial:
            trigger = str(initial.get("trigger", ""))
            replacement = str(initial.get("replacement", ""))
            image_path = str(initial.get("image_path", ""))
            enabled = bool(initial.get("enabled", True))

        self.var_trigger = tk.StringVar(value=trigger)
        self.var_image = tk.StringVar(value=image_path)
        self.var_enabled = tk.BooleanVar(value=enabled)

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Trigger").grid(row=0, column=0, sticky="w")
        ent = ttk.Entry(frm, textvariable=self.var_trigger, width=28)
        ent.grid(row=1, column=0, sticky="ew")

        ttk.Label(frm, text="Output Text (Optional)").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.txt = tk.Text(frm, width=42, height=6, wrap="word")
        self.txt.grid(row=3, column=0, sticky="ew")
        self.txt.insert("1.0", replacement)

        ttk.Label(frm, text="Image Path (Optional)").grid(row=4, column=0, sticky="w", pady=(10, 0))
        
        img_frm = ttk.Frame(frm)
        img_frm.grid(row=5, column=0, sticky="ew")
        
        ttk.Entry(img_frm, textvariable=self.var_image).pack(side="left", fill="x", expand=True)
        ttk.Button(img_frm, text="Browse", command=self._browse_image, width=8).pack(side="right", padx=(4, 0))

        chk = ttk.Checkbutton(frm, text="Enabled", variable=self.var_enabled)
        chk.grid(row=6, column=0, sticky="w", pady=(10, 0))

        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, sticky="e", pady=(12, 0))

        ttk.Button(btns, text="Cancel", command=self._cancel).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Save", command=self._save).grid(row=0, column=1)

        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Control-Return>", lambda _e: self._save())
        ent.focus_set()
        self.transient(master)
        self.grab_set()

    def _browse_image(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Select Image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
        )
        if path:
            self.var_image.set(path)

    def _cancel(self):
        self.result = None
        self.destroy()

    def _save(self):
        trigger = self.var_trigger.get().strip()
        replacement = self.txt.get("1.0", "end-1c")
        image_path = self.var_image.get().strip()
        enabled = bool(self.var_enabled.get())

        if not trigger:
            messagebox.showerror("Invalid", "Trigger tidak boleh kosong.", parent=self)
            return

        self.result = {
            "trigger": trigger,
            "replacement": replacement,
            "image_path": image_path,
            "enabled": enabled
        }
        self.destroy()


class AutoWordGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoWord")
        self.root.geometry("800x600")

        self.engine = AutoWordEngine()
        
        # Setup logging callback
        self.engine.log_callback = self._append_log
        
        self.rules = load_rules()
        self.engine.set_rules(self.rules)

        self._build_ui()
        self._refresh_table()
        self._update_status()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _append_log(self, msg: str):
        if not hasattr(self, 'log_text'):
            return
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + "\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def run(self):
        self.root.mainloop()

    def _build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        main = ttk.Frame(root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        top = ttk.Frame(main)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        self.var_status = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.var_status).grid(row=0, column=0, sticky="w")
        ttk.Button(top, text="Start", command=self._start).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(top, text="Stop", command=self._stop).grid(row=0, column=2, padx=(8, 0))

        self.table = ttk.Treeview(main, columns=("trigger", "enabled", "replacement"), show="headings", selectmode="browse")
        self.table.heading("trigger", text="Trigger")
        self.table.heading("enabled", text="On")
        self.table.heading("replacement", text="Output")
        self.table.column("trigger", width=180, anchor="w")
        self.table.column("enabled", width=60, anchor="center")
        self.table.column("replacement", width=480, anchor="w")
        self.table.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        vsb = ttk.Scrollbar(main, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns", pady=(12, 0))

        bottom = ttk.Frame(main)
        bottom.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(bottom, text="Add", command=self._add).grid(row=0, column=0)
        ttk.Button(bottom, text="Edit", command=self._edit).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(bottom, text="Delete", command=self._delete).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(bottom, text="Toggle", command=self._toggle).grid(row=0, column=3, padx=(8, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(main, text="Logs", padding=4)
        log_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        main.rowconfigure(3, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, state='disabled', font=("Consolas", 9))
        self.log_text.pack(side="left", fill="both", expand=True)
        
        log_sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_sb.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_sb.set)

        ttk.Button(bottom, text="Open rules.json", command=self._open_rules).grid(row=0, column=4, padx=(20, 0))

        self.table.bind("<Double-1>", lambda _e: self._edit())

    def _on_close(self):
        try:
            self.engine.stop()
        finally:
            self.root.destroy()

    def _start(self):
        self.engine.set_rules(self.rules)
        self.engine.start()
        self._update_status()

    def _stop(self):
        self.engine.stop()
        self._update_status()

    def _update_status(self):
        status = "Running" if self.engine.running else "Stopped"
        self.var_status.set(f"{status} | Rules: {len(self.rules)} | File: {rules_path()}")

    def _refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for idx, r in enumerate(self.rules):
            trig = str(r.get("trigger", ""))
            rep = str(r.get("replacement", ""))
            en = "✓" if r.get("enabled", True) else ""
            rep_one = rep.replace("\r\n", "\n").replace("\n", " ⏎ ")
            if len(rep_one) > 120:
                rep_one = rep_one[:120] + "..."
            self.table.insert("", "end", iid=str(idx), values=(trig, en, rep_one))

    def _selected_index(self) -> Optional[int]:
        sel = self.table.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except Exception:
            return None

    def _add(self):
        dlg = RuleEditor(self.root, "Add Rule", None)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        self.rules.append(dlg.result)
        self._persist_and_refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        initial = dict(self.rules[idx])
        dlg = RuleEditor(self.root, "Edit Rule", initial)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        self.rules[idx] = dlg.result
        self._persist_and_refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        trig = str(self.rules[idx].get("trigger", ""))
        if not messagebox.askyesno("Delete", f"Hapus rule {trig}?", parent=self.root):
            return
        self.rules.pop(idx)
        self._persist_and_refresh()

    def _toggle(self):
        idx = self._selected_index()
        if idx is None:
            return
        r = dict(self.rules[idx])
        r["enabled"] = not bool(r.get("enabled", True))
        self.rules[idx] = r
        self._persist_and_refresh()

    def _persist_and_refresh(self):
        save_rules(self.rules)
        self.engine.set_rules(self.rules)
        self._refresh_table()
        self._update_status()

    def _open_rules(self):
        import os

        path = rules_path()
        try:
            os.startfile(path)
        except Exception:
            messagebox.showerror("Error", "Gagal membuka rules.json", parent=self.root)

