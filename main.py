import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as mpl

# ---------------- PROFESSIONAL DESIGN SYSTEM ----------------
CLR_TOOL     = "#ffffff" 
CLR_BG       = "#f8fafc" 
CLR_CARD     = "#ffffff" 
CLR_ACCENT   = "#3b82f6" # Modern Electric Blue
CLR_BORDER   = "#e2e8f0" 
CLR_TEXT     = "#1e293b" 
CLR_MUTE     = "#94a3b8"
CLR_DANGER   = "#f43f5e"
CLR_SUCCESS  = "#10b981"

class EnterpriseBI:
    def __init__(self, root):
        self.root = root
        self.root.title("BI Analytics Pro - Modern Insights")
        self.root.geometry("1600x950")
        self.root.configure(bg=CLR_BG)
        
        self.df = None
        self.filtered_df = None
        self.filter_widgets = []

        self._setup_styles()
        self._create_layout()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CLR_CARD, foreground=CLR_TEXT, rowheight=30, font=("Inter", 9))
        style.configure("Treeview.Heading", background="#f1f5f9", font=("Inter", 9, "bold"), borderwidth=0)
        style.map("Treeview", background=[('selected', CLR_ACCENT)])

    def _create_layout(self):
        # 1. TOP NAVIGATION
        self.ribbon = tk.Frame(self.root, bg=CLR_TOOL, height=70, highlightbackground=CLR_BORDER, highlightthickness=1)
        self.ribbon.pack(side="top", fill="x")
        self.ribbon.pack_propagate(False)
        
        # Logo / Title
        tk.Label(self.ribbon, text="INSIGHTS PRO", fg=CLR_ACCENT, bg=CLR_TOOL, font=("Inter Black", 12)).pack(side="left", padx=20)
        
        # File Actions
        tk.Button(self.ribbon, text="📂 Import Data", command=self.load_data, bg=CLR_BG, relief="flat", font=("Inter Medium", 9), padx=15).pack(side="left", padx=5)

        # Graph Settings Group
        settings_frame = tk.Frame(self.ribbon, bg=CLR_TOOL)
        settings_frame.pack(side="left", padx=40)

        tk.Label(settings_frame, text="ANALYSIS METRIC", bg=CLR_TOOL, font=("Inter", 7, "bold"), fg=CLR_MUTE).grid(row=0, column=0, sticky="w", padx=5)
        self.chart_y = ttk.Combobox(settings_frame, state="readonly", width=18)
        self.chart_y.grid(row=1, column=0, padx=5)

        tk.Label(settings_frame, text="VISUALIZATION", bg=CLR_TOOL, font=("Inter", 7, "bold"), fg=CLR_MUTE).grid(row=0, column=1, sticky="w", padx=5)
        self.chart_type = ttk.Combobox(settings_frame, state="readonly", width=18, values=["Modern Bar", "Smooth Area", "Lollipop Chart", "Scatter Trend"])
        self.chart_type.set("Modern Bar")
        self.chart_type.grid(row=1, column=1, padx=5)
        
        tk.Button(self.ribbon, text="GENERATE REPORT", bg=CLR_ACCENT, fg="white", font=("Inter Bold", 9), 
                  command=self.refresh_charts, relief="flat", padx=20, pady=8).pack(side="left", padx=10)

        # Right Side Actions
        tk.Button(self.ribbon, text="Reset Filters", bg=CLR_DANGER, fg="white", font=("Inter Medium", 9), command=self.full_reset, relief="flat", padx=15).pack(side="right", padx=20)

        # 2. FILTER BAR
        self.filter_bar = tk.Frame(self.root, bg=CLR_TOOL, highlightbackground=CLR_BORDER, highlightthickness=1, pady=10)
        self.filter_bar.pack(side="top", fill="x")
        
        for i in range(4):
            f_container = tk.Frame(self.filter_bar, bg=CLR_TOOL)
            f_container.pack(side="left", padx=20)
            tk.Label(f_container, text=f"SEGMENT {i+1}", bg=CLR_TOOL, font=("Inter", 7, "bold"), fg=CLR_MUTE).pack(anchor="w")
            c_col = ttk.Combobox(f_container, state="readonly", width=15)
            c_col.pack(side="top")
            c_col.bind("<<ComboboxSelected>>", lambda e, idx=i: self.on_filter_col_change(idx))
            c_val = ttk.Combobox(f_container, state="readonly", width=15)
            c_val.pack(side="top", pady=2)
            self.filter_widgets.append({"col": c_col, "val": c_val})

        # 3. WORKSPACE
        self.workspace = tk.Frame(self.root, bg=CLR_BG, padx=25, pady=20)
        self.workspace.pack(fill="both", expand=True)

        # KPI Metrics
        self.kpi_frame = tk.Frame(self.workspace, bg=CLR_BG)
        self.kpi_frame.pack(fill="x", pady=(0, 20))

        # Main Content Split
        self.paned = tk.PanedWindow(self.workspace, orient="horizontal", bg=CLR_BG, sashwidth=4)
        self.paned.pack(fill="both", expand=True)

        self.table_pane = tk.Frame(self.paned, bg=CLR_CARD, highlightbackground=CLR_BORDER, highlightthickness=1)
        self.paned.add(self.table_pane, stretch="always")

        self.chart_pane = tk.Frame(self.paned, bg=CLR_CARD, width=600, highlightbackground=CLR_BORDER, highlightthickness=1)
        self.paned.add(self.chart_pane, stretch="never")

    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path: return
        self.df = pd.read_csv(path)
        self.filtered_df = self.df.copy()
        
        num_cols = self.df.select_dtypes(include="number").columns.tolist()
        self.chart_y["values"] = num_cols
        if num_cols: self.chart_y.set(num_cols[0])
        
        cols = list(self.df.columns)
        for f in self.filter_widgets:
            f["col"]["values"] = ["(None)"] + cols
            f["col"].set("(None)")
            
        self.refresh_dashboard()

    def apply_multi_filters(self):
        if self.df is None: return
        temp_df = self.df.copy()
        for f in self.filter_widgets:
            col, val = f["col"].get(), f["val"].get()
            if col != "(None)" and val not in ["(All)", ""]:
                temp_df = temp_df[temp_df[col].astype(str) == str(val)]
        self.filtered_df = temp_df
        self.refresh_dashboard()

    def on_filter_col_change(self, idx):
        col = self.filter_widgets[idx]["col"].get()
        if col != "(None)":
            vals = sorted(self.df[col].dropna().unique().astype(str))
            self.filter_widgets[idx]["val"]["values"] = ["(All)"] + vals
            self.filter_widgets[idx]["val"].set("(All)")
        self.apply_multi_filters() # Auto-update on selection

    def full_reset(self):
        if self.df is not None:
            self.filtered_df = self.df.copy()
            for f in self.filter_widgets:
                f["col"].set("(None)")
                f["val"].set("")
            self.refresh_dashboard()

    def refresh_dashboard(self):
        self._render_kpis()
        self._render_table()

    def refresh_charts(self):
        if self.df is None: return
        self._render_charts()

    def _render_kpis(self):
        for w in self.kpi_frame.winfo_children(): w.destroy()
        y = self.chart_y.get()
        val = self.filtered_df[y].sum() if y in self.filtered_df else 0
        
        for label, value, color in [("TOTAL RECORDS", len(self.filtered_df), CLR_TEXT), 
                                     (f"TOTAL {y}", f"{val:,.0f}", CLR_ACCENT)]:
            card = tk.Frame(self.kpi_frame, bg=CLR_CARD, padx=20, pady=15, highlightbackground=CLR_BORDER, highlightthickness=1)
            card.pack(side="left", expand=True, fill="x", padx=5)
            tk.Label(card, text=label, font=("Inter Bold", 8), fg=CLR_MUTE, bg=CLR_CARD).pack(anchor="w")
            tk.Label(card, text=value, font=("Inter Black", 16), fg=color, bg=CLR_CARD).pack(anchor="w")

    def _render_table(self):
        for w in self.table_pane.winfo_children(): w.destroy()
        tree = ttk.Treeview(self.table_pane, show="headings", columns=list(self.filtered_df.columns))
        tree.pack(fill="both", expand=True)
        for c in self.filtered_df.columns:
            tree.heading(c, text=c.upper())
            tree.column(c, width=120)
        for row in self.filtered_df.head(50).values:
            tree.insert("", "end", values=list(row))

    def _render_charts(self):
        for w in self.chart_pane.winfo_children(): w.destroy()
        y_col = self.chart_y.get()
        style = self.chart_type.get()
        
        # Determine grouping (categorical column)
        cat_cols = self.df.select_dtypes(exclude='number').columns
        grp_col = cat_cols[0] if len(cat_cols) > 0 else self.df.columns[0]

        # Process data for large sets (Top 15 items)
        plot_data = self.filtered_df.groupby(grp_col)[y_col].sum().sort_values(ascending=True).tail(15)

        # Modern Matplotlib Styling
        plt.rcParams['font.family'] = 'sans-serif'
        fig, ax = plt.subplots(figsize=(6, 8), dpi=100)
        fig.patch.set_facecolor(CLR_CARD)
        ax.set_facecolor(CLR_CARD)

        if style == "Modern Bar":
            plot_data.plot(kind='barh', ax=ax, color=CLR_ACCENT, width=0.8, edgecolor=CLR_CARD, linewidth=2)
            for i, v in enumerate(plot_data):
                ax.text(v, i, f'  {v:,.0f}', va='center', fontsize=8, fontweight='bold', color=CLR_TEXT)

        elif style == "Smooth Area":
            plot_data = plot_data.sort_index()
            ax.fill_between(range(len(plot_data)), plot_data.values, color=CLR_ACCENT, alpha=0.3)
            ax.plot(range(len(plot_data)), plot_data.values, color=CLR_ACCENT, lw=3, marker='o', markersize=8, mfc='white')
            ax.set_xticks(range(len(plot_data)))
            ax.set_xticklabels(plot_data.index, rotation=45, ha='right')

        elif style == "Lollipop Chart":
            ax.hlines(y=range(len(plot_data)), xmin=0, xmax=plot_data.values, color=CLR_BORDER, lw=2)
            ax.plot(plot_data.values, range(len(plot_data)), "o", markersize=10, color=CLR_ACCENT, mec=CLR_ACCENT)
            ax.set_yticks(range(len(plot_data)))
            ax.set_yticklabels(plot_data.index)

        else: # Scatter Trend
            ax.scatter(range(len(self.filtered_df[:500])), self.filtered_df[y_col][:500], alpha=0.4, color=CLR_ACCENT, s=30)
            ax.set_xlabel("Data Sampling Index", fontsize=8, color=CLR_MUTE)

        # Clean UI finishing
        ax.set_title(f"{style.upper()}: {y_col.upper()} by {grp_col.upper()}", loc='left', fontsize=10, fontweight='black', color=CLR_TEXT, pad=25)
        ax.tick_params(axis='both', which='major', labelsize=8, colors=CLR_MUTE)
        ax.grid(axis='x', color=CLR_BORDER, linestyle='--', alpha=0.5)
        
        for s in ['top', 'right', 'left', 'bottom']:
            ax.spines[s].set_visible(False)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.chart_pane)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        print("All Process is completed")



if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    EnterpriseBI(root)
    root.mainloop()