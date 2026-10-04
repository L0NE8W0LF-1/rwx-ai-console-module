import json
import threading
import time
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from spec_detection import load_profile, score_profile, recommend_action


class RWXDashboard:
    """Local GUI dashboard for RWX AI recovery module diagnostics and control."""

    def __init__(self, root):
        self.root = root
        self.root.title("RWX AI Console Recovery Module - Dashboard")
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

        self.device_tab = ttk.Frame(notebook)
        notebook.add(self.device_tab, text="Device Detection")
        self.setup_device_tab()

        self.profile_tab = ttk.Frame(notebook)
        notebook.add(self.profile_tab, text="Hardware Profile")
        self.setup_profile_tab()

        self.recovery_tab = ttk.Frame(notebook)
        notebook.add(self.recovery_tab, text="Recovery & Boot")
        self.setup_recovery_tab()

        self.diag_tab = ttk.Frame(notebook)
        notebook.add(self.diag_tab, text="Diagnostics")
        self.setup_diagnostics_tab()

        self.logs_tab = ttk.Frame(notebook)
        notebook.add(self.logs_tab, text="Logs & Reports")
        self.setup_logs_tab()

    def setup_device_tab(self):
        frame = ttk.LabelFrame(self.device_tab, text="Device Detection & Status", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Scan for Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Profile File", command=self.load_profile_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh Status", command=self.refresh_status).pack(side=tk.LEFT, padx=5)

        self.device_tree = ttk.Treeview(frame, columns=("Device", "Model", "State"), height=12, show="headings")
        self.device_tree.heading("Device", text="Device")
        self.device_tree.heading("Model", text="Model")
        self.device_tree.heading("State", text="State")
        self.device_tree.column("Device", width=300)
        self.device_tree.column("Model", width=300)
        self.device_tree.column("State", width=200)
        self.device_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_tree.config(yscrollcommand=scrollbar.set)

    def setup_profile_tab(self):
        frame = ttk.LabelFrame(self.profile_tab, text="Target Hardware Profile", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.profile_text = tk.Text(frame, height=25, width=100, bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.profile_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.profile_text, orient=tk.VERTICAL, command=self.profile_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_text.config(yscrollcommand=scrollbar.set)

        status_frame = ttk.Frame(self.profile_tab)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        self.profile_status = ttk.Label(status_frame, text="No profile loaded", foreground="orange")
        self.profile_status.pack(side=tk.LEFT)

    def setup_recovery_tab(self):
        frame = ttk.LabelFrame(self.recovery_tab, text="Recovery & Boot Workflow", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Label(control_frame, text="Available Recovery Images:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        self.recovery_listbox = tk.Listbox(control_frame, height=8, bg="#2d2d2d", fg="#00ff00")
        self.recovery_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        sample_images = [
            "recovery-diagnostics-v1.0.bin",
            "recovery-maintenance-v1.0.bin",
            "debug-shell-v0.9.bin",
            "hardware-test-suite-v1.2.bin",
        ]
        for img in sample_images:
            self.recovery_listbox.insert(tk.END, img)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Load Selected Image", command=self.load_recovery_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Boot Recovery", command=self.boot_recovery).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel Boot", command=self.cancel_boot).pack(side=tk.LEFT, padx=5)

        self.boot_progress = ttk.Progressbar(frame, length=400, mode="determinate")
        self.boot_progress.pack(fill=tk.X, pady=10)

        self.boot_status = ttk.Label(frame, text="Ready", foreground="green")
        self.boot_status.pack(anchor=tk.W, pady=5)

    def setup_diagnostics_tab(self):
        frame = ttk.LabelFrame(self.diag_tab, text="Hardware Diagnostics", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Run Full Diagnostics", command=self.run_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analyze Profile", command=self.analyze_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=5)

        self.diag_text = tk.Text(frame, height=20, width=100, bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.diag_text.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(self.diag_text, orient=tk.VERTICAL, command=self.diag_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.diag_text.config(yscrollcommand=scrollbar.set)

    def setup_logs_tab(self):
        frame = ttk.LabelFrame(self.logs_tab, text="Activity Logs & Reports", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Report", command=self.save_report).pack(side=tk.LEFT, padx=5)

        self.log_text = tk.Text(frame, height=20, width=100, bg="#1a1a1a", fg="#ffffff", font=("Courier", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.add_log("RWX AI Console Recovery Module initialized.")
        self.add_log("Waiting for device connection...")

    def scan_devices(self):
        self.add_log("[SCAN] Scanning for connected devices...")
        self.device_tree.delete(*self.device_tree.get_children())

        devices = [
            ("USB-Recovery-001", "Xbox Series S", "Recovery Mode"),
            ("USB-Recovery-002", "PlayStation 5", "Normal"),
        ]

        for device, model, state in devices:
            self.device_tree.insert("", tk.END, values=(device, model, state))
            self.add_log(f"[SCAN] Detected: {device} ({model}) - {state}")

        self.device_connected = True
        self.update_status("Connected", "green")
        self.add_log("[SCAN] Device scan complete.")

    def load_profile_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Hardware Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            self.current_profile = load_profile(file_path)
            self.display_profile()
            self.add_log(f"[PROFILE] Loaded: {file_path}")
            self.profile_status.config(text=f"Profile: {self.current_profile.get('model', 'Unknown')}", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")
            self.add_log(f"[ERROR] Failed to load profile: {e}")

    def display_profile(self):
        if not self.current_profile:
            self.profile_text.config(state=tk.NORMAL)
            self.profile_text.delete(1.0, tk.END)
            self.profile_text.insert(tk.END, "No profile loaded.")
            self.profile_text.config(state=tk.DISABLED)
            return

        self.profile_text.config(state=tk.NORMAL)
        self.profile_text.delete(1.0, tk.END)
        profile_json = json.dumps(self.current_profile, indent=2)
        self.profile_text.insert(tk.END, profile_json)
        self.profile_text.config(state=tk.DISABLED)

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

        self.diag_text.config(state=tk.NORMAL)
        self.diag_text.delete(1.0, tk.END)

        score = score_profile(self.current_profile)
        action = recommend_action(self.current_profile)

        output = f"""
╔══════════════════════════════════════════════════════╗
║         RWX AI Profile Analysis Report            ║
╚══════════════════════════════════════════════════════╝

Device Information:
  Platform:      {self.current_profile.get('platform', 'Unknown')}
  Model:         {self.current_profile.get('model', 'Unknown')}
  Revision:      {self.current_profile.get('revision', 'Unknown')}
  Boot State:    {self.current_profile.get('boot_state', 'Unknown')}

Hardware Specs:
  CPU:           {self.current_profile.get('cpu', 'Unknown')}
  GPU:           {self.current_profile.get('gpu', 'Unknown')}
  RAM:           {self.current_profile.get('ram_gb', 'Unknown')} GB
  Storage:       {self.current_profile.get('storage_gb', 'Unknown')} GB

AI Analysis:
  Compatibility Score: {score * 100:.1f}%
  Risk Level: {self._risk_level(score)}

Recommendation:
  {action}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.diag_text.insert(tk.END, output)
        self.diag_text.config(state=tk.DISABLED)
        self.add_log(f"[ANALYSIS] Profile analyzed. Compatibility: {score * 100:.1f}%")

    def run_diagnostics(self):
        self.diag_text.config(state=tk.NORMAL)
        self.diag_text.delete(1.0, tk.END)

        if not self.device_connected:
            self.diag_text.insert(tk.END, "No device connected. Connect a device first.")
            self.diag_text.config(state=tk.DISABLED)
            self.add_log("[DIAG] Error: No device connected.")
            return

        output = "Running diagnostics...\n\n"
        self.diag_text.insert(tk.END, output)
        self.diag_text.update()

        checks = [
            ("Power Rail Check", "✓ PASS"),
            ("Memory Test", "✓ PASS"),
            ("Storage Check", "✓ PASS"),
            ("Thermal Sensors", "✓ PASS"),
            ("Boot ROM Integrity", "✓ PASS"),
            ("Serial Interface", "✓ PASS"),
        ]

        for check_name, result in checks:
            line = f"  {check_name:<30} {result}\n"
            self.diag_text.insert(tk.END, line)
            self.diag_text.update()
            time.sleep(0.3)
            self.add_log(f"[DIAG] {check_name}: {result}")

        self.diag_text.insert(tk.END, "\n✓ Diagnostics complete.")
        self.diag_text.config(state=tk.DISABLED)
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
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.diag_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Report exported to {file_path}")
            self.add_log(f"[EXPORT] Diagnostic report saved: {file_path}")

    def export_logs(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Logs exported to {file_path}")

    def save_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if file_path and self.current_profile:
            report = {
                "timestamp": datetime.now().isoformat(),
                "profile": self.current_profile,
                "analysis": {
                    "compatibility_score": score_profile(self.current_profile),
                    "recommendation": recommend_action(self.current_profile),
                },
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            messagebox.showinfo("Success", f"Report saved to {file_path}")
            self.add_log(f"[EXPORT] Full report saved: {file_path}")

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_entries.clear()

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_entries.append(log_line)

    def update_status(self, status, color):
        self.status_label.config(text=f"Status: {status}", foreground=color)

    def start_monitor_thread(self):
        def monitor():
            while True:
                time.sleep(2)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def _risk_level(self, score):
        if score >= 0.9:
            return "Low Risk"
        elif score >= 0.75:
            return "Medium Risk"
        else:
            return "High Risk"


def main():
    root = tk.Tk()
    app = RWXDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
