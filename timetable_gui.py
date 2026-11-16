"""
College Timetable Generator - Desktop GUI (Tkinter)
University Lecture Schedule Planner
- Max 2 lectures per course per day
- Total weekly lectures == Working Days * Lectures per day
- Greedy prioritization (course with most remaining lectures scheduled first)
"""

import tkinter as tk
from tkinter import ttk, messagebox

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

PALETTE = [
    ("#eff6ff", "#1e40af", "#3b82f6"),  # Blue
    ("#ecfdf5", "#065f46", "#10b981"),  # Emerald
    ("#e0e7ff", "#3730a3", "#6366f1"),  # Indigo
    ("#fef3c7", "#92400e", "#f59e0b"),  # Amber
    ("#f3e8ff", "#6b21a8", "#a855f7"),  # Purple
    ("#cffafe", "#155e75", "#06b6d4"),  # Cyan
    ("#ffe4e6", "#9f1239", "#f43f5e"),  # Rose
    ("#ffedd5", "#9a3412", "#f97316"),  # Orange
]


class CollegeTimetableApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("College Timetable Generator - Lecture Planner")
        self.geometry("1000x700")
        self.minsize(880, 560)

        # Default College Courses (6 days x 5 lectures = 30 slots)
        self.subjects = [
            ("Data Structures & Algorithms", 6),
            ("Operating Systems", 5),
            ("Database Management Systems", 5),
            ("Computer Networks", 5),
            ("Linear Algebra & Probability", 4),
            ("Software Engineering", 3),
            ("CS Lab Practical", 2),
        ]

        self.setup_ui()
        self.update_stats()
        self.generate()

    def setup_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass

        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left panel (Controls)
        left_frame = ttk.Frame(main_paned, width=360)
        main_paned.add(left_frame, weight=1)

        # Right panel (Timetable view)
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # --- LEFT PANEL CONTENTS ---
        lbl_settings = ttk.Label(left_frame, text="🎓 College Schedule Config", font=("Segoe UI", 12, "bold"))
        lbl_settings.pack(anchor="w", pady=(0, 10))

        # Days & Lectures per day
        cfg_frame = ttk.LabelFrame(left_frame, text="Academic Hours", padding=10)
        cfg_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(cfg_frame, text="Working Days (1-6):").grid(row=0, column=0, sticky="w", pady=4)
        self.var_days = tk.IntVar(value=6)
        self.spin_days = ttk.Spinbox(cfg_frame, from_=1, to=6, textvariable=self.var_days, width=6, command=self.update_stats)
        self.spin_days.grid(row=0, column=1, sticky="e", pady=4)

        ttk.Label(cfg_frame, text="Lectures per day:").grid(row=1, column=0, sticky="w", pady=4)
        self.var_per_day = tk.IntVar(value=5)
        self.spin_per_day = ttk.Spinbox(cfg_frame, from_=1, to=10, textvariable=self.var_per_day, width=6, command=self.update_stats)
        self.spin_per_day.grid(row=1, column=1, sticky="e", pady=4)

        # Slot Metrics & Status
        self.lbl_stats = ttk.Label(cfg_frame, text="Slots: 30 / 30", font=("Segoe UI", 9, "bold"), foreground="#2563eb")
        self.lbl_stats.grid(row=2, column=0, columnspan=2, pady=6)

        self.lbl_status = ttk.Label(cfg_frame, text="All lecture slots allocated.", font=("Segoe UI", 8), wraplength=280)
        self.lbl_status.grid(row=3, column=0, columnspan=2)

        # Add Course Frame
        sub_add_frame = ttk.LabelFrame(left_frame, text="Add College Course", padding=10)
        sub_add_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(sub_add_frame, text="Course:").grid(row=0, column=0, sticky="w")
        self.entry_name = ttk.Entry(sub_add_frame, width=18)
        self.entry_name.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(sub_add_frame, text="Weekly Lectures:").grid(row=1, column=0, sticky="w")
        self.entry_periods = ttk.Spinbox(sub_add_frame, from_=1, to=20, width=6)
        self.entry_periods.set(4)
        self.entry_periods.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        btn_add = ttk.Button(sub_add_frame, text="+ Add Course", command=self.add_subject)
        btn_add.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        # Course List
        sub_list_frame = ttk.LabelFrame(left_frame, text="Enrolled Courses", padding=10)
        sub_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.tree_subjects = ttk.Treeview(sub_list_frame, columns=("Course", "Lectures"), show="headings", height=7)
        self.tree_subjects.heading("Course", text="Course Name")
        self.tree_subjects.heading("Lectures", text="Lectures/Wk")
        self.tree_subjects.column("Course", width=160)
        self.tree_subjects.column("Lectures", width=70, anchor="center")
        self.tree_subjects.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(sub_list_frame)
        btn_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(btn_row, text="- Remove", command=self.remove_subject).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(btn_row, text="Auto-Balance", command=self.auto_fill).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Generate Button
        self.btn_gen = tk.Button(
            left_frame,
            text="⚡ Generate College Timetable",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            pady=8,
            command=self.generate
        )
        self.btn_gen.pack(fill=tk.X)

        # --- RIGHT PANEL CONTENTS ---
        top_bar = ttk.Frame(right_frame)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_bar, text="College Lecture Schedule", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="📋 Copy Text", command=self.copy_text).pack(side=tk.RIGHT, padx=4)

        # Timetable Treeview
        self.table_frame = ttk.Frame(right_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_table = ttk.Treeview(self.table_frame, show="headings")
        self.tree_table.pack(fill=tk.BOTH, expand=True)

        # Text output box
        text_frame = ttk.LabelFrame(right_frame, text="Text Output (Copy-friendly)", padding=8)
        text_frame.pack(fill=tk.X, pady=(10, 0))

        self.txt_output = tk.Text(text_frame, height=7, font=("Consolas", 10), bg="#0f172a", fg="#f8fafc", relief="flat")
        self.txt_output.pack(fill=tk.X)

        self.populate_subject_tree()

    def populate_subject_tree(self):
        for item in self.tree_subjects.get_children():
            self.tree_subjects.delete(item)
        for name, periods in self.subjects:
            self.tree_subjects.insert("", tk.END, values=(name, periods))

    def update_stats(self):
        days = self.var_days.get()
        per_day = self.var_per_day.get()
        required = days * per_day
        allocated = sum(p for _, p in self.subjects)
        max_allowed = days * 2

        self.lbl_stats.config(text=f"Lectures: {allocated} / {required} (Req: {required})")

        over_limit = [name for name, p in self.subjects if p > max_allowed]
        if over_limit:
            self.lbl_status.config(
                text=f"⚠️ '{over_limit[0]}' exceeds max limit of {max_allowed} ({days} days × 2/day)",
                foreground="#ef4444"
            )
            self.btn_gen.config(state="disabled", bg="#94a3b8")
        elif allocated == required:
            self.lbl_status.config(
                text="✓ Perfect! All lecture slots allocated. Ready to generate.",
                foreground="#10b981"
            )
            self.btn_gen.config(state="normal", bg="#2563eb")
        elif allocated < required:
            self.lbl_status.config(
                text=f"⏳ Need {required - allocated} more lectures.",
                foreground="#f59e0b"
            )
            self.btn_gen.config(state="disabled", bg="#94a3b8")
        else:
            self.lbl_status.config(
                text=f"✕ Overallocated by {allocated - required} lectures.",
                foreground="#ef4444"
            )
            self.btn_gen.config(state="disabled", bg="#94a3b8")

    def add_subject(self):
        name = self.entry_name.get().strip()
        try:
            periods = int(self.entry_periods.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Lectures count must be an integer.")
            return

        if not name:
            messagebox.showerror("Invalid Input", "Course name cannot be empty.")
            return

        self.subjects.append((name, periods))
        self.entry_name.delete(0, tk.END)
        self.entry_periods.set(4)
        self.populate_subject_tree()
        self.update_stats()

    def remove_subject(self):
        selected = self.tree_subjects.selection()
        if not selected:
            return
        idx = self.tree_subjects.index(selected[0])
        del self.subjects[idx]
        self.populate_subject_tree()
        self.update_stats()

    def auto_fill(self):
        days = self.var_days.get()
        per_day = self.var_per_day.get()
        required = days * per_day
        allocated = sum(p for _, p in self.subjects)
        diff = required - allocated
        max_allowed = days * 2

        if diff == 0:
            return

        new_subs = []
        left = diff
        if diff > 0:
            for name, p in self.subjects:
                room = max_allowed - p
                if room > 0 and left > 0:
                    add = min(room, left)
                    new_subs.append((name, p + add))
                    left -= add
                else:
                    new_subs.append((name, p))
            if left > 0:
                new_subs.append(("Seminar / Library Research", left))
        else:
            to_sub = abs(diff)
            for name, p in reversed(self.subjects):
                if p > 1 and to_sub > 0:
                    sub = min(p - 1, to_sub)
                    new_subs.append((name, p - sub))
                    to_sub -= sub
                else:
                    new_subs.append((name, p))
            new_subs.reverse()

        self.subjects = new_subs
        self.populate_subject_tree()
        self.update_stats()

    def generate(self):
        days_count = self.var_days.get()
        per_day_count = self.var_per_day.get()
        required = days_count * per_day_count
        allocated = sum(p for _, p in self.subjects)

        if allocated != required:
            messagebox.showerror("Error", f"Total weekly lectures ({allocated}) must equal slots ({required}).")
            return

        for name, p in self.subjects:
            if p > days_count * 2:
                messagebox.showerror(
                    "Error",
                    f"Timetable cannot be generated: {name} needs {p} lectures in {days_count} days, limit is 2 per day."
                )
                return

        grid = [[None] * per_day_count for _ in range(days_count)]
        remaining = {name: p for name, p in self.subjects}
        order = [name for name, _ in self.subjects]

        def search(d, p):
            if d == days_count:
                return True
            next_d = d + 1 if p + 1 == per_day_count else d
            next_p = 0 if p + 1 == per_day_count else p + 1

            today = [grid[d][i] for i in range(p)]
            options = [s for s in order if remaining[s] > 0 and today.count(s) < 2]

            options.sort(key=lambda s: (-remaining[s], order.index(s)))

            for cand in options:
                grid[d][p] = cand
                remaining[cand] -= 1
                if search(next_d, next_p):
                    return True
                grid[d][p] = None
                remaining[cand] += 1
            return False

        if not search(0, 0):
            messagebox.showerror("Error", "Could not generate valid timetable with daily limit constraint.")
            return

        cols = ["Day"] + [f"Lecture {i + 1}" for i in range(per_day_count)]
        self.tree_table.config(columns=cols)
        for col in cols:
            self.tree_table.heading(col, text=col)
            self.tree_table.column(col, width=120, anchor="center")

        for item in self.tree_table.get_children():
            self.tree_table.delete(item)

        raw_text_lines = []
        for d in range(days_count):
            day_label = DAYS[d]
            row_vals = [day_label] + grid[d]
            self.tree_table.insert("", tk.END, values=row_vals)
            raw_text_lines.append(f"{day_label}: {', '.join(grid[d])}")

        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "\n".join(raw_text_lines))

    def copy_text(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Copied", "Timetable text copied to clipboard!")


if __name__ == "__main__":
    app = CollegeTimetableApp()
    app.mainloop()
