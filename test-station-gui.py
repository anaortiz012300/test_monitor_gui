import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime

# ----------------------------
# Fake Database Layer (placeholders)
# ----------------------------

def save_test_run_to_db(device, environment):
    """
    This would create a new test run in the database.
    For example:
    INSERT INTO test_runs (device, environment, started_at)
    """
    print("DB QUERY -> INSERT test_run")
    print(f"  device={device}, environment={environment}")
    print("-" * 50)


def save_test_result_to_db(test_name, status, device, environment):
    """
    This would save an individual test result.
    For example:
    INSERT INTO test_results (test_name, status, device, environment)
    """
    print("DB QUERY -> INSERT test_result")
    print(f"  test={test_name}, status={status}")
    print(f"  device={device}, environment={environment}")
    print("-" * 50)


def get_tests_from_db():
    """
    This would fetch tests from database.
    For example:
    SELECT name FROM test_definitions
    """
    print("DB QUERY -> SELECT tests")
    print("-" * 50)

    # For now we return the same hardcoded list
    return [
        {"name": "Initial Test", "status": "PENDING"},
        {"name": "Calibration", "status": "PENDING"},
        {"name": "Vibration", "status": "PENDING"},
        {"name": "Radiation", "status": "PENDING"},
        {"name": "Final Test", "status": "PENDING"},
    ]

def get_env_from_db():
    """
    This would fetch tests from database.
    For example:
    SELECT name FROM environments
    """
    print("DB QUERY -> SELECT env")
    print("-" * 50)

    # For now we return the same hardcoded list
    return ["Ambient", "Thermal - Hot", "Thermal - Cold"]

def get_devices_from_db():
    """
    This would fetch tests from database.
    For example:
    SELECT name FROM devices
    """
    print("DB QUERY -> SELECT device")
    print("-" * 50)

    # For now we return the same hardcoded list
    return ["FPGA" , "Microprocessor", "Microcontroller", "NVME"]

# ----------------------------
# Data: tests + selectable options
# ----------------------------

tests = get_tests_from_db()
DEVICES = get_devices_from_db()
ENVIRONMENTS = get_env_from_db()

running = False
current = 0  # which test index we're on

# ----------------------------
# Helper functions
# ----------------------------
def update_table():
    table.delete(*table.get_children())
    for i, t in enumerate(tests, start=1):
        table.insert("", "end", values=(i, t["name"], t["status"]))

    done = sum(1 for t in tests if t["status"] in ("PASS", "FAIL"))
    progress["value"] = done
    summary_var.set(f"Done: {done}/{len(tests)}")


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    log_box.configure(state="normal")
    log_box.insert(tk.END, f"[{ts}] {msg}\n")
    log_box.see(tk.END)
    log_box.configure(state="disabled")


def selected_device():
    return device_var.get().strip() or "Unknown Device"


def selected_env():
    return env_var.get().strip() or "Unknown Environment"


def set_selectors_state(state: str):
    """state is 'normal' or 'disabled'"""
    device_combo.config(state=state)
    env_combo.config(state=state)

# ----------------------------
# Simulation functions
# ----------------------------
def start():
    global running, current
    if running:
        return

    running = True
    current = 0

    # Disable controls while running
    start_btn.config(state="disabled")
    reset_btn.config(state="disabled")
    set_selectors_state("disabled")

    save_test_run_to_db(selected_device(), selected_env())

    log(f"Starting test run on Device='{selected_device()}', Env='{selected_env()}'")
    run_next_test()


def run_next_test():
    global current

    if current >= len(tests):
        finish_all()
        return

    tests[current]["status"] = "RUNNING"
    update_table()
    log(f"Running: {tests[current]['name']}")

    # highlight current row
    children = table.get_children()
    if current < len(children):
        table.selection_set(children[current])
        table.see(children[current])

    root.after(900, finish_current_test)


def finish_current_test():
    global current

    result = random.choices(["PASS", "FAIL"], weights=[80, 20], k=1)[0]
    tests[current]["status"] = result
    update_table()
    log(f"Finished: {tests[current]['name']} -> {result}")

       # 🔥 Database hook
    save_test_result_to_db(
        test_name=tests[current]["name"],
        status=result,
        device=selected_device(),
        environment=selected_env()
    )

    current += 1
    root.after(250, run_next_test)


def finish_all():
    global running
    running = False

    start_btn.config(state="normal")
    reset_btn.config(state="normal")
    set_selectors_state("readonly")

    log("All tests completed.")


def reset():
    global running, current
    running = False
    current = 0

    for t in tests:
        t["status"] = "PENDING"

    log_box.configure(state="normal")
    log_box.delete("1.0", tk.END)
    log_box.configure(state="disabled")

    update_table()
    log("Ready.")

    start_btn.config(state="normal")
    reset_btn.config(state="normal")
    set_selectors_state("readonly")


# ----------------------------
# UI setup
# ----------------------------
root = tk.Tk()
root.title("Test Monitor")
root.geometry("760x560")
root.minsize(700, 520)

style = ttk.Style(root)
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
style.configure("Sub.TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

app = ttk.Frame(root, padding=14)
app.pack(fill="both", expand=True)

# Header
header = ttk.Frame(app)
header.pack(fill="x")
ttk.Label(header, text="Test Monitor", style="Title.TLabel").pack(anchor="w")

summary_var = tk.StringVar(value="")
ttk.Label(header, textvariable=summary_var, style="Sub.TLabel").pack(anchor="w", pady=(2, 0))

# NEW: Device + Env selectors row
selectors = ttk.Frame(app)
selectors.pack(fill="x", pady=(12, 6))
selectors.columnconfigure(1, weight=1)
selectors.columnconfigure(3, weight=1)

device_var = tk.StringVar(value=DEVICES[0])
env_var = tk.StringVar(value=ENVIRONMENTS[0])

ttk.Label(selectors, text="Device:").grid(row=0, column=0, sticky="w", padx=(0, 6))
device_combo = ttk.Combobox(selectors, textvariable=device_var, values=DEVICES, state="readonly")
device_combo.grid(row=0, column=1, sticky="ew", padx=(0, 14))

ttk.Label(selectors, text="Environment:").grid(row=0, column=2, sticky="w", padx=(0, 6))
env_combo = ttk.Combobox(selectors, textvariable=env_var, values=ENVIRONMENTS, state="readonly")
env_combo.grid(row=0, column=3, sticky="ew")

# Controls row
controls = ttk.Frame(app)
controls.pack(fill="x", pady=(6, 10))

progress = ttk.Progressbar(controls, mode="determinate", maximum=len(tests))
progress.pack(side="left", fill="x", expand=True)

start_btn = ttk.Button(controls, text="Start", command=start)
start_btn.pack(side="left", padx=(10, 6))

reset_btn = ttk.Button(controls, text="Reset", command=reset)
reset_btn.pack(side="left")

# Main split area
main = ttk.Frame(app)
main.pack(fill="both", expand=True)
main.columnconfigure(0, weight=3)
main.columnconfigure(1, weight=2)
main.rowconfigure(0, weight=1)

# Left: table
left = ttk.Frame(main)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
left.rowconfigure(0, weight=1)
left.columnconfigure(0, weight=1)

columns = ("#", "Test", "Status")
table = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
table.heading("#", text="#")
table.heading("Test", text="Test")
table.heading("Status", text="Status")

table.column("#", width=40, anchor="center", stretch=False)
table.column("Test", width=360, anchor="w")
table.column("Status", width=120, anchor="center", stretch=False)

table.grid(row=0, column=0, sticky="nsew")
scroll = ttk.Scrollbar(left, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scroll.set)
scroll.grid(row=0, column=1, sticky="ns")

# Right: logs
right = ttk.LabelFrame(main, text="Live Log")
right.grid(row=0, column=1, sticky="nsew")
right.rowconfigure(0, weight=1)
right.columnconfigure(0, weight=1)

log_box = tk.Text(right, height=10, wrap="word", font=("Consolas", 10))
log_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
log_scroll = ttk.Scrollbar(right, orient="vertical", command=log_box.yview)
log_box.configure(yscrollcommand=log_scroll.set)
log_scroll.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))
log_box.configure(state="disabled")

# Initial UI state
update_table()
log("Ready.")

root.mainloop()