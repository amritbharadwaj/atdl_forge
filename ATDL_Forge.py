import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
import os
import xml.etree.ElementTree as ET
import io

class ATDLRenderer:
    def __init__(self, root):
        self.root = root
        self.root.title("ATDL Forge")
        self.set_window_icon()
        self.fields = {}

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.load_button = ttk.Button(self.frame, text="Load ATDL XML", command=self.load_file)
        self.load_button.pack(pady=10, anchor=tk.W)

        self.strategy_frame = ttk.Frame(self.frame)
        self.strategy_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(self.strategy_frame, text="Strategies").pack(side=tk.LEFT, padx=(0, 8))
        self.strategy_combo = ttk.Combobox(self.strategy_frame, state="disabled")
        self.strategy_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.strategy_combo.bind("<<ComboboxSelected>>", self.on_strategy_selected)

        self.form_frame = ttk.Frame(self.frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        self.submit_button = ttk.Button(self.frame, text="Generate FIX Message", command=self.generate_fix)
        self.submit_button.pack(pady=10, anchor=tk.W)

        self.output = tk.Text(self.frame, height=10)
        self.output.pack(fill=tk.BOTH, expand=True)
        self.strategies = {}
        self.param_tags = {}
        self.param_const = {}
        self.field_width = 22

    def clear_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.fields.clear()

    def set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.png")
        if os.path.exists(icon_path):
            self.icon_image = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, self.icon_image)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if not file_path:
            return

        self.clear_form()
        try:
            with open(file_path, "rb") as handle:
                raw = handle.read()
            xml_text = raw.decode("utf-8-sig")
            root = ET.fromstring(xml_text)
        except (OSError, UnicodeDecodeError) as exc:
            messagebox.showerror("Load Error", f"Failed to read XML file:\n{exc}")
            return
        except ET.ParseError as exc:
            messagebox.showerror(
                "XML Parse Error",
                f"The XML is not well-formed.\n{exc}\n\n"
                "Please fix the XML and try again.",
            )
            return

        ns = {'atdl': 'http://www.fixprotocol.org/FIXatdl-1-1/Core'}
        self.strategies.clear()

        for strategy in root.findall('.//atdl:Strategy', ns):
            name = strategy.get('name')
            if name:
                self.strategies[name] = strategy

        strategy_names = list(self.strategies.keys())
        if not strategy_names:
            messagebox.showerror("Load Error", "No <Strategy> elements found in the XML.")
            self.strategy_combo.configure(state="disabled", values=[])
            return

        self.strategy_combo.configure(state="readonly", values=strategy_names)
        self.strategy_combo.set(strategy_names[0])
        self.render_strategy(strategy_names[0])

    def on_strategy_selected(self, _event):
        name = self.strategy_combo.get()
        if name:
            self.render_strategy(name)

    def render_strategy(self, name):
        self.clear_form()
        strategy = self.strategies.get(name)
        if strategy is None:
            return

        ns = {
            'atdl': 'http://www.fixprotocol.org/FIXatdl-1-1/Core',
            'lay': 'http://www.fixprotocol.org/FIXatdl-1-1/Layout',
        }
        self.param_tags.clear()
        self.param_const.clear()
        for param in strategy.findall('.//atdl:Parameter', ns):
            param_name = param.get('name')
            if not param_name:
                continue
            fix_tag = param.get('fixTag') or param.get('tag')
            if fix_tag:
                self.param_tags[param_name] = fix_tag
            const_value = param.get('constValue')
            if const_value is not None:
                self.param_const[param_name] = const_value

        left_row = 0
        right_row = 0
        for control in strategy.findall('.//lay:Control', ns):
            param_ref = control.get('parameterRef')
            if not param_ref:
                continue

            label = control.get('label', param_ref)
            control_type = control.get('{http://www.w3.org/2001/XMLSchema-instance}type')
            is_time = self.is_time_field(param_ref, label)

            if is_time:
                label_col = 2
                field_col = 3
                row = right_row
                right_row += 1
            else:
                label_col = 0
                field_col = 1
                row = left_row
                left_row += 1

            ttk.Label(self.form_frame, text=label).grid(row=row, column=label_col, sticky=tk.W, padx=5, pady=5)

            if control_type in ['lay:TextField_t', 'TextField_t']:
                entry = tk.Entry(self.form_frame, relief="solid", borderwidth=1, width=self.field_width)
                entry.grid(row=row, column=field_col, padx=5, pady=5)
                if is_time:
                    entry.bind("<Button-1>", lambda _e, w=entry: self.on_time_entry_interact(w))
                    entry.bind("<FocusIn>", lambda _e, w=entry: self.on_time_entry_interact(w))
                self.fields[param_ref] = entry
            elif control_type in ['lay:DropDownList_t', 'DropDownList_t']:
                combo = ttk.Combobox(self.form_frame, values=['LOW', 'MEDIUM', 'HIGH'], width=self.field_width)
                combo.grid(row=row, column=field_col, padx=5, pady=5)
                self.fields[param_ref] = combo
            elif control_type in ['lay:CheckBox_t', 'CheckBox_t']:
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.form_frame, variable=var)
                chk.grid(row=row, column=field_col)
                self.fields[param_ref] = var

    def is_time_field(self, param_ref, label):
        text = f"{param_ref} {label}".lower()
        return "time" in text or "timestamp" in text

    def on_time_entry_interact(self, entry):
        if getattr(entry, "_datetime_picker_open", False):
            return
        if getattr(entry, "_datetime_picker_cooldown", False):
            return
        self.open_datetime_picker(entry)

    def open_datetime_picker(self, entry):
        entry._datetime_picker_open = True
        top = tk.Toplevel(self.root)
        top.title("Select Time")
        top.transient(self.root)
        top.grab_set()

        now = datetime.datetime.now()
        initial = self.parse_time_entry(entry.get()) or now

        form = ttk.Frame(top, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text="Time").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))

        time_frame = ttk.Frame(form)
        time_frame.grid(row=0, column=1, sticky=tk.W, pady=(0, 6))

        hour_var = tk.IntVar(value=initial.hour)
        minute_var = tk.IntVar(value=initial.minute)
        second_var = tk.IntVar(value=initial.second)

        hour_spin = tk.Spinbox(time_frame, from_=0, to=23, width=4, textvariable=hour_var)
        minute_spin = tk.Spinbox(time_frame, from_=0, to=59, width=4, textvariable=minute_var)
        second_spin = tk.Spinbox(time_frame, from_=0, to=59, width=4, textvariable=second_var)
        hour_spin.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT, padx=2)
        minute_spin.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT, padx=2)
        second_spin.pack(side=tk.LEFT)

        def on_ok():
            value = f"{hour_var.get():02d}:{minute_var.get():02d}:{second_var.get():02d}"
            entry.delete(0, tk.END)
            entry.insert(0, value)
            self.close_datetime_picker(entry, top)

        def on_cancel():
            self.close_datetime_picker(entry, top)

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=2, sticky=tk.E, pady=(8, 0))
        ttk.Button(buttons, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(buttons, text="OK", command=on_ok).pack(side=tk.RIGHT)

        top.update_idletasks()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_w = self.root.winfo_width()
        parent_h = self.root.winfo_height()
        win_w = top.winfo_width()
        win_h = top.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        top.geometry(f"+{x}+{y}")

    def close_datetime_picker(self, entry, top):
        entry._datetime_picker_open = False
        entry._datetime_picker_cooldown = True
        entry.after(250, lambda: setattr(entry, "_datetime_picker_cooldown", False))
        top.destroy()

    def parse_time_entry(self, value):
        try:
            return datetime.datetime.strptime(value.strip(), "%H:%M:%S")
        except (ValueError, TypeError):
            return None

    def generate_fix(self):
        fix_msg = "35=D|"
        added = set()

        for name, widget in self.fields.items():
            tag = self.param_tags.get(name, name)
            if isinstance(widget, (ttk.Entry, tk.Entry)):
                value = widget.get()
            elif isinstance(widget, ttk.Combobox):
                value = widget.get()
            elif isinstance(widget, tk.BooleanVar):
                value = 'Y' if widget.get() else 'N'
            else:
                value = ''

            if value:
                fix_msg += f"{tag}={value}|"
                added.add(name)

        for name, const_value in self.param_const.items():
            if name in added:
                continue
            tag = self.param_tags.get(name, name)
            if const_value:
                fix_msg += f"{tag}={const_value}|"

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, fix_msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = ATDLRenderer(root)
    root.mainloop()
