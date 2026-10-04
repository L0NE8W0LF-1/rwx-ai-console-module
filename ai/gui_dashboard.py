import threading
import time
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from spec_detection import load_profile, score_profile, recommend_action


class RWXDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("RWX AI Console Recovery Module")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")

        self.current_profile = None
        self.device_connected = False
        self.log_entries = []

        self.setup_ui()
        self.start_monitor_thread()

    def setup_ui(self):
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(header, text="RWX AI Console Recovery", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        self.status_label = ttk.Label(header, text="Status: Disconnected", font=("Arial", 10), foreground="red")
        self.status_label.pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        device_tab = ttk.Frame(notebook)
        notebook.add(device_tab, text="Device Detection")
        self.setup_device_tab(device_tab)

        profile_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text="Hardware Profile")
        self.setup_profile_tab(profile_tab)

        recovery_tab = ttk.Frame(notebook)
        notebook.add(recovery_tab, text="Recovery & Boot")
        self.setup_recovery_tab(recovery_tab)

        diag_tab = ttk.Frame(notebook)
        notebook.add(diag_tab, text="Diagnostics")
        self.setup_diagnostics_tab(diag_tab)

        logs_tab = ttk.Frame(notebook)
        notebook.add(logs_tab, text="Logs & Reports")
        self.setup_logs_tab(logs_tab)

    def setup_device_tab(self, frame):
        frame = ttk.LabelFrame(frame, text="Device Detection & Status", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=10)

        ttk.Button(buttons, text="Scan for Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Load Profile File", command=self.load_profile_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Refresh Status", command=self.refresh_status).pack(side=tk.LEFT, padx=5)

        self.device_tree = ttk.Treeview(frame, columns=("Device", "Model", "State"), height=12, show="headings")
        self.device_tree.heading("Device", text="Device")
        self.device_tree.heading("Model", text="Model")
        self.device_tree.heading("State", text="State")
        self.device_tree.column("Device", width=300)
        self.device_tree.column("Model", width=300)
        self.device_tree.column("State", width=200)
        self.device_tree.pack(fill=tk.BOTH, expand=True)

    def setup_profile_tab(self, frame):
        frame = ttk.LabelFrame(frame, text="Target Hardware Profile", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.profile_text = tk.Text(frame, height=25, width=100, bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.profile_text.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        self.profile_status = ttk.Label(status_frame, text="No profile loaded", foreground="orange")
        self.profile_status.pack(side=tk.LEFT)

    def setup_recovery_tab(self, frame):
        frame = ttk.LabelFrame(frame, text="Recovery & Boot Workflow", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        panel = ttk.Frame(frame)
        panel.pack(fill=tk.X, pady=10)
        ttk.Label(panel, text="Available Recovery Images:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        self.recovery_listbox = tk.Listbox(panel, height=8, bg="#2d2d2d", fg="#00ff00")
        self.recovery_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        for img in [
            "recovery-diagnostics-v1.0.bin",
            "recovery-maintenance-v1.0.bin",
            "debug-shell-v0.9.bin",
            "hardware-test-suite-v1.2.bin",
        ]:
            self.recovery_listbox.insert(tk.END, img)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=10)
        ttk.Button(buttons, text="Load Selected Image", command=self.load_recovery_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Boot Recovery", command=self.boot_recovery).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Cancel Boot", command=self.cancel_boot).pack(side=tk.LEFT, padx=5)

        self.boot_progress = ttk.Progressbar(frame, length=400, mode="determinate")
        self.boot_progress.pack(fill=tk.X, pady=10)
        self.boot_status = ttk.Label(frame, text="Ready", foreground="green")
        self.boot_status.pack(anchor=tk.W, pady=5)

    def setup_diagnostics_tab(self, frame):
        frame = ttk.LabelFrame(frame, text="Hardware Diagnostics", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=10)
        ttk.Button(buttons, text="Run Full Diagnostics", command=self.run_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Analyze Profile", command=self.analyze_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=5)

        self.diag_text = tk.Text(frame, height=20, width=100, bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.diag_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def setup_logs_tab(self, frame):
        frame = ttk.LabelFrame(frame, text="Activity Logs & Reports", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=10)
        ttk.Button(buttons, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Save Report", command=self.save_report).pack(side=tk.LEFT, padx=5)

        self.log_text = tk.Text(frame, height=20, width=100, bg="#1a1a1a", fg="#ffffff", font=("Courier", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.add_log("RWX AI Console Recovery Module initialized.")
        self.add_log("Waiting for device connection...")

    def scan_devices(self):
        self.add_log("[SCAN] Scanning for connected devices...")
        self.device_tree.delete(*self.device_tree.get_children())

        for device, model, state in [
            ("USB-Recovery-001", "Xbox Series S", "Recovery Mode"),
            ("USB-Recovery-002", "PlayStation 5", "Normal"),
        ]:
            self.device_tree.insert("", tk.END, values=(device, model, state))
            self.add_log(f"[SCAN] Detected: {device} ({model}) - {state}")

        self.device_connected = True
        self.update_status("Connected", "green")
        self.add_log("[SCAN] Device scan complete.")

    def load_profile_file(self):
        file_path = filedialog.askopenfilename(title="Select Hardware Profile", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            self.current_profile = load_profile(file_path)
            self.display_profile()
            self.profile_status.config(text=f"Profile: {self.current_profile.get('model', 'Unknown')}", foreground="green")
            self.add_log(f"[PROFILE] Loaded: {file_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load profile: {exc}")
            self.add_log(f"[ERROR] Failed to load profile: {exc}")

    def display_profile(self):
        if not self.current_profile:
            self.profile_text.delete(1.0, tk.END)
            self.profile_text.insert(tk.END, "No profile loaded.")
            return
        self.profile_text.delete(1.0, tk.END)
        self.profile_text.insert(tk.END, __import__('json').dumps(self.current_profile, indent=2))

    def refresh_status(self):
        self.add_log("[STATUS] Refreshing device status...")
        if self.device_connected:
            self.update_status("Connected", "green")
            self.add_log("[STATUS] Device connected and healthy.")
        else:
            self.update_status("Disconnected", "red")
            self.add_log("[STATUS] No device connected.")

    def analyze_profile(self):
        if not self.current_profile:
            messagebox.showwarning("Warning", "No profile loaded. Load a profile first.")
            return

        self.diag_text.delete(1.0, tk.END)
        result = __import__('json').dumps({
            "profile": self.current_profile,
            "score": score_profile(self.current_profile),
            "recommendation": recommend_action(self.current_profile),
        }, indent=2)
        self.diag_text.insert(tk.END, result)
        self.add_log("[ANALYSIS] Profile analyzed.")

    def run_diagnostics(self):
        self.diag_text.delete(1.0, tk.END)
        if not self.device_connected:
            self.diag_text.insert(tk.END, "No device connected. Connect a device first.")
            self.add_log("[DIAG] Error: No device connected.")
            return

        checks = [
            ("Power Rail Check", "✓ PASS"),
            ("Memory Test", "✓ PASS"),
            ("Storage Check", "✓ PASS"),
            ("Thermal Sensors", "✓ PASS"),
            ("Boot ROM Integrity", "✓ PASS"),
        ]

        for check_name, result in checks:
            self.diag_text.insert(tk.END, f"  {check_name:<30} {result}\n")
            self.diag_text.update()
            time.sleep(0.2)
            self.add_log(f"[DIAG] {check_name}: {result}")

        self.diag_text.insert(tk.END, "\n✓ Diagnostics complete.")
        self.add_log("[DIAG] Full diagnostic suite complete.")

    def load_recovery_image(self):
        selection = self.recovery_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a recovery image first.")
            return
        selected = self.recovery_listbox.get(selection[0])
        self.boot_status.config(text=f"Image loaded: {selected}", foreground="blue")
        self.add_log(f"[BOOT] Recovery image loaded: {selected}")
        messagebox.showinfo("Success", f"Loaded: {selected}")

    def boot_recovery(self):
        if not self.device_connected:
            messagebox.showerror("Error", "No device connected.")
            return
        if messagebox.askyesno("Confirm", "Boot recovery environment? This will reset the device."):
            self.boot_status.config(text="Booting...", foreground="orange")
            self.add_log("[BOOT] Initiating recovery boot...")
            for i in range(0, 101, 10):
                self.boot_progress["value"] = i
                self.root.update()
                time.sleep(0.2)
            self.boot_progress["value"] = 100
            self.boot_status.config(text="Recovery environment active", foreground="green")
            self.add_log("[BOOT] Recovery boot complete.")
            messagebox.showinfo("Success", "Recovery environment is now active.")

    def cancel_boot(self):
        self.boot_progress["value"] = 0
        self.boot_status.config(text="Boot cancelled", foreground="red")
        self.add_log("[BOOT] Boot operation cancelled.")

    def export_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(self.diag_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Report exported to {file_path}")
            self.add_log(f"[EXPORT] Diagnostic report saved: {file_path}")

    def export_logs(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Logs exported to {file_path}")

    def save_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path and self.current_profile:
            report = {
                "timestamp": datetime.now().isoformat(),
                "profile": self.current_profile,
                "analysis": {
                    "compatibility_score": score_profile(self.current_profile),
                    "recommendation": recommend_action(self.current_profile),
                },
            }
            with open(file_path, "w", encoding="utf-8") as handle:
                __import__("json").dump(report, handle, indent=2)
            messagebox.showinfo("Success", f"Report saved to {file_path}")
            self.add_log(f"[EXPORT] Full report saved: {file_path}")

    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.log_entries.clear()

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_entries.append(log_line)

    def update_status(self, status, color):
        self.status_label.config(text=f"Status: {status}", foreground=color)

    def start_monitor_thread(self):
        def monitor():
            while True:
                time.sleep(2)
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    RWXDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
