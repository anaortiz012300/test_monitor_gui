import tkinter as tk
from tkinter import ttk
from datetime import datetime

# =========================================================
# IN-MEMORY SAMPLE DATA (stand-in for database data)
# =========================================================
# Later, this "data store" would be replaced by DB queries.
RUNS = [
    {
        "run_id": 101,
        "device": "Pixel 7",
        "environment": "QA",
        "started_at": "2026-02-23 09:12:10",
        "results": [
            {"test_name": "Login", "status": "PASS", "finished_at": "2026-02-23 09:12:30"},
            {"test_name": "API Healthcheck", "status": "PASS", "finished_at": "2026-02-23 09:12:50"},
            {"test_name": "Upload File", "status": "FAIL", "finished_at": "2026-02-23 09:13:20"},
        ],
    },
    {
        "run_id": 102,
        "device": "iPhone 14",
        "environment": "STAGING",
        "started_at": "2026-02-23 10:05:00",
        "results": [
            {"test_name": "Login", "status": "PASS", "finished_at": "2026-02-23 10:05:20"},
            {"test_name": "Create User", "status": "PASS", "finished_at": "2026-02-23 10:05:45"},
            {"test_name": "Logout", "status": "PASS", "finished_at": "2026-02-23 10:06:05"},
        ],
    },
    {
        "run_id": 103,
        "device": "Web (Chrome)",
        "environment": "DEV",
        "started_at": "2026-02-23 11:30:10",
        "results": [
            {"test_name": "API Healthcheck", "status": "FAIL", "finished_at": "2026-02-23 11:30:40"},
            {"test_name": "Create User", "status": "PASS", "finished_at": "2026-02-23 11:31:10"},
        ],
    },
]


# =========================================================
# DATABASE PLACEHOLDERS (commented places where DB would be called)
# =========================================================

def db_get_distinct_devices():
    """
    DB PLACEHOLDER:
      SELECT DISTINCT device FROM test_runs ORDER BY device;
    """
    return sorted({r["device"] for r in RUNS})


def db_get_distinct_environments():
    """
    DB PLACEHOLDER:
      SELECT DISTINCT environment FROM test_runs ORDER BY environment;
    """
    return sorted({r["environment"] for r in RUNS})


def db_query_results(device="All", environment="All", status="All"):
    """
    DB PLACEHOLDER (example join):
      SELECT r.run_id, r.started_at, r.device, r.environment, tr.test_name, tr.status, tr.finished_at
      FROM test_runs r
      JOIN test_results tr ON tr.run_id = r.run_id
      WHERE (device filter...) AND (environment filter...) AND (status filter...)
      ORDER BY r.run_id DESC, tr.id ASC;
    """
    rows = []
    for run in RUNS:
        if device != "All" and run["device"] != device:
            continue
        if environment != "All" and run["environment"] != environment:
            continue

        for res in run["results"]:
            if status != "All" and res["status"] != status:
                continue
            rows.append((
                run["run_id"],
                run["started_at"],
                run["device"],
                run["environment"],
                res["test_name"],
                res["status"],
                res["finished_at"],
            ))

    # Newest runs first
    rows.sort(key=lambda x: (-int(x[0]), x[6]))
    return rows


# =========================================================
# DASHBOARD GUI
# =========================================================

def build_dashboard():
    root = tk.Tk()
    root.title("Simple Dashboard")
    root.geometry("980x560")
    root.minsize(900, 520)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Sub.TLabel", font=("Segoe UI", 10))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    container = ttk.Frame(root, padding=12)
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=1)
    container.rowconfigure(2, weight=1)

    # Header
# Header
    ttk.Label(container, text="Dashboard", style="Title.TLabel").grid(row=0, column=0, sticky="w")

    ttk.Label(
        container,
        text="Devices • Environments • Test Results",
        style="Sub.TLabel"
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
    # Filters
    filters = ttk.LabelFrame(container, text="Filters", padding=10)
    filters.grid(row=1, column=0, sticky="ew", pady=(10, 10))
    filters.columnconfigure(1, weight=1)
    filters.columnconfigure(3, weight=1)
    filters.columnconfigure(5, weight=1)

    device_var = tk.StringVar(value="All")
    env_var = tk.StringVar(value="All")
    status_var = tk.StringVar(value="All")

    ttk.Label(filters, text="Device:").grid(row=0, column=0, sticky="w", padx=(0, 6))
    device_cb = ttk.Combobox(filters, textvariable=device_var, state="readonly")
    device_cb.grid(row=0, column=1, sticky="ew", padx=(0, 12))

    ttk.Label(filters, text="Environment:").grid(row=0, column=2, sticky="w", padx=(0, 6))
    env_cb = ttk.Combobox(filters, textvariable=env_var, state="readonly")
    env_cb.grid(row=0, column=3, sticky="ew", padx=(0, 12))

    ttk.Label(filters, text="Status:").grid(row=0, column=4, sticky="w", padx=(0, 6))
    status_cb = ttk.Combobox(filters, textvariable=status_var, state="readonly",
                             values=["All", "PASS", "FAIL"])
    status_cb.grid(row=0, column=5, sticky="ew")

    # Summary
    summary_var = tk.StringVar(value="")
    ttk.Label(container, textvariable=summary_var, style="Sub.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))

    # Results table
    table_frame = ttk.Frame(container)
    table_frame.grid(row=2, column=0, sticky="nsew")
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    cols = ("run_id", "started_at", "device", "environment", "test_name", "status", "finished_at")
    tv = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
    for c, title in zip(cols, ["Run", "Run Start", "Device", "Env", "Test", "Status", "Finished At"]):
        tv.heading(c, text=title)

    tv.column("run_id", width=60, anchor="center", stretch=False)
    tv.column("started_at", width=150, anchor="w", stretch=False)
    tv.column("device", width=160, anchor="w")
    tv.column("environment", width=120, anchor="center", stretch=False)
    tv.column("test_name", width=240, anchor="w")
    tv.column("status", width=90, anchor="center", stretch=False)
    tv.column("finished_at", width=150, anchor="w", stretch=False)

    tv.grid(row=0, column=0, sticky="nsew")

    scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=scroll_y.set)
    scroll_y.grid(row=0, column=1, sticky="ns")

    def refresh_filter_values():
        # DB PLACEHOLDER: these would come from SELECT DISTINCT queries
        devices = ["All"] + db_get_distinct_devices()
        envs = ["All"] + db_get_distinct_environments()

        device_cb["values"] = devices
        env_cb["values"] = envs

        # keep selections valid
        if device_var.get() not in devices:
            device_var.set("All")
        if env_var.get() not in envs:
            env_var.set("All")

    def refresh_results():
        refresh_filter_values()

        # DB PLACEHOLDER: this would be a single DB query with filters
        rows = db_query_results(
            device=device_var.get(),
            environment=env_var.get(),
            status=status_var.get()
        )

        tv.delete(*tv.get_children())
        for row in rows:
            tv.insert("", "end", values=row)

        total = len(rows)
        passed = sum(1 for r in rows if r[5] == "PASS")
        failed = sum(1 for r in rows if r[5] == "FAIL")
        pass_rate = (passed / total * 100) if total else 0.0
        summary_var.set(f"Rows: {total}   PASS: {passed}   FAIL: {failed}   Pass Rate: {pass_rate:.1f}%")

    def on_filter_change(_=None):
        refresh_results()

    # Buttons
    btn_row = ttk.Frame(filters)
    btn_row.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(10, 0))
    btn_row.columnconfigure(0, weight=1)

    ttk.Button(btn_row, text="Refresh", command=refresh_results).grid(row=0, column=0, sticky="ew")

    # Auto refresh on filter change
    device_cb.bind("<<ComboboxSelected>>", on_filter_change)
    env_cb.bind("<<ComboboxSelected>>", on_filter_change)
    status_cb.bind("<<ComboboxSelected>>", on_filter_change)

    refresh_results()
    root.mainloop()


if __name__ == "__main__":
    build_dashboard()