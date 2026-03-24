"""
FridaBypass Tool - Main GUI Application
A user-friendly Tkinter interface for spoofing device properties in Android games
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from connector import FridaConnector
from spoofer import FridaSpoofer
from profiles_manager import ProfileManager


class FridaBypassGUI:
    """Main Tkinter GUI for FridaBypass"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FridaBypass Tool - Device Spoofer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initialize managers
        self.spoofer = FridaSpoofer()
        self.profile_manager = self.spoofer.profile_manager
        
        # State variables
        self.connection_status = tk.StringVar(value="Not connected")
        self.spoof_status = tk.StringVar(value="Idle")
        self.log_queue = queue.Queue()
        
        # Redirect print to log
        self._setup_logging()
        
        # Build UI
        self._build_ui()
        
        # Start log update thread
        self._update_logs()
    
    def _setup_logging(self):
        """Redirect print statements to log queue"""
        original_print = print
        
        def logged_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)
            self.log_queue.put(message)
            original_print(*args, **kwargs)
        
        import builtins
        builtins.print = logged_print
    
    def _build_ui(self):
        """Build the Tkinter UI"""
        
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_container,
            text="FridaBypass - Android Game Device Spoofer",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # ============================================================
        # Connection Section
        # ============================================================
        connection_frame = ttk.LabelFrame(main_container, text="BlueStacks Connection", padding="10")
        connection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        # Port input
        ttk.Label(connection_frame, text="Frida Server Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="27042")
        port_entry = ttk.Entry(connection_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        # Connect button
        self.connect_btn = ttk.Button(
            connection_frame,
            text="Connect to BlueStacks",
            command=self._connect_bluestacks
        )
        self.connect_btn.grid(row=0, column=2, sticky=tk.E)
        
        # Connection status
        ttk.Label(connection_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        status_label = ttk.Label(
            connection_frame,
            textvariable=self.connection_status,
            font=("Arial", 10, "bold"),
            foreground="red"
        )
        status_label.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # ============================================================
        # Spoof Configuration Section
        # ============================================================
        config_frame = ttk.LabelFrame(main_container, text="Spoofing Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Device profile selector
        ttk.Label(config_frame, text="Device Profile:").grid(row=0, column=0, sticky=tk.W)
        self.profile_var = tk.StringVar()
        profile_combo = ttk.Combobox(
            config_frame,
            textvariable=self.profile_var,
            values=self.profile_manager.list_profiles(),
            state="readonly",
            width=40
        )
        profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        if self.profile_manager.list_profiles():
            profile_combo.current(0)
        
        # Game package name
        ttk.Label(config_frame, text="Game Package Name:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.package_var = tk.StringVar(value="com.example.game")
        package_entry = ttk.Entry(config_frame, textvariable=self.package_var)
        package_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(10, 0))
        
        # Spoof button
        self.spoof_btn = ttk.Button(
            config_frame,
            text="Apply Spoof",
            command=self._apply_spoof,
            state=tk.DISABLED
        )
        self.spoof_btn.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
        # Spoof status
        ttk.Label(config_frame, text="Spoof Status:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        status_label = ttk.Label(
            config_frame,
            textvariable=self.spoof_status,
            font=("Arial", 10, "bold"),
            foreground="red"
        )
        status_label.grid(row=3, column=1, sticky=tk.W, pady=(10, 0))
        
        # ============================================================
        # Device Profile Info Section
        # ============================================================
        info_frame = ttk.LabelFrame(main_container, text="Selected Profile Details", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.profile_info_var = tk.StringVar()
        self.profile_info_label = ttk.Label(
            info_frame,
            textvariable=self.profile_info_var,
            font=("Courier", 9),
            justify=tk.LEFT
        )
        self.profile_info_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Update profile info when selection changes
        profile_combo.bind("<<ComboboxSelected>>", self._update_profile_info)
        self._update_profile_info()
        
        # ============================================================
        # Logs Section
        # ============================================================
        logs_frame = ttk.LabelFrame(main_container, text="Activity Logs", padding="10")
        logs_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=15,
            width=100,
            font=("Courier", 8),
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear logs button
        clear_btn = ttk.Button(
            logs_frame,
            text="Clear Logs",
            command=self._clear_logs
        )
        clear_btn.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
    
    def _update_profile_info(self, event=None):
        """Update profile info display"""
        profile_name = self.profile_var.get()
        profile = self.profile_manager.get_profile_by_display_name(profile_name)
        
        if profile:
            info = f"""
Model: {profile.get('model', 'N/A')}
Brand: {profile.get('brand', 'N/A')}
Manufacturer: {profile.get('manufacturer', 'N/A')}
Hardware: {profile.get('hardware', 'N/A')}
Android Version: {profile.get('androidVersion', 'N/A')}
Fingerprint: {profile.get('fingerprint', 'N/A')[:50]}...
            """.strip()
            self.profile_info_var.set(info)
    
    def _connect_bluestacks(self):
        """Connect to BlueStacks in a separate thread"""
        self.connect_btn.config(state=tk.DISABLED)
        
        def connect_thread():
            try:
                port = int(self.port_var.get())
                print(f"[*] Connecting to BlueStacks on port {port}...")
                
                if self.spoofer.connect_to_bluestacks("127.0.0.1", port):
                    self.connection_status.set("✓ Connected")
                    self.spoof_btn.config(state=tk.NORMAL)
                    print("[+] Successfully connected to BlueStacks!")
                else:
                    self.connection_status.set("✗ Connection Failed")
                    print("[-] Failed to connect to BlueStacks")
            except ValueError:
                self.connection_status.set("✗ Invalid Port")
                print("[-] Invalid port number")
            except Exception as e:
                self.connection_status.set("✗ Error")
                print(f"[-] Error: {e}")
            finally:
                self.connect_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def _apply_spoof(self):
        """Apply spoofing in a separate thread"""
        if not self.spoofer.connector or not self.spoofer.connector.is_connected:
            messagebox.showerror("Error", "Not connected to BlueStacks")
            return
        
        profile_name = self.profile_var.get()
        package_name = self.package_var.get()
        
        if not profile_name:
            messagebox.showerror("Error", "Please select a device profile")
            return
        
        if not package_name or not package_name.strip():
            messagebox.showerror("Error", "Please enter a game package name")
            return
        
        self.spoof_btn.config(state=tk.DISABLED)
        
        def spoof_thread():
            try:
                print(f"\n[*] ========================================")
                print(f"[*] Applying Spoof")
                print(f"[*] ========================================")
                print(f"[*] Profile: {profile_name}")
                print(f"[*] Package: {package_name}")
                
                self.spoof_status.set("⏳ Spoofing...")
                
                # Select profile
                if not self.spoofer.select_profile(profile_name):
                    self.spoof_status.set("✗ Profile Selection Failed")
                    return
                
                # Apply spoof
                if self.spoofer.spoof_game(package_name):
                    self.spoof_status.set("✓ Spoofing Active")
                    print("\n[+] ========================================")
                    print("[+] SPOOFING SUCCESSFUL!")
                    print("[+] Game is now running with spoofed device")
                    print("[+] ========================================\n")
                else:
                    self.spoof_status.set("✗ Spoofing Failed")
                    print("\n[-] Spoofing failed - check game is running")
                    
            except Exception as e:
                self.spoof_status.set("✗ Error")
                print(f"[-] Error during spoofing: {e}")
            finally:
                self.spoof_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=spoof_thread, daemon=True)
        thread.start()
    
    def _update_logs(self):
        """Update log display from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)  # Auto-scroll to bottom
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self._update_logs)
    
    def _clear_logs(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    # Create GUI
    gui = FridaBypassGUI(root)
    
    # Welcome message
    print("\n" + "="*60)
    print("FridaBypass Tool - Initialized")
    print("="*60)
    print("[*] Welcome to FridaBypass!")
    print("[*] Device Spoofer for Android Games")
    print("[*] ")
    print("[*] Steps:")
    print("[*] 1. Enter Frida server port (default 27042)")
    print("[*] 2. Click 'Connect to BlueStacks'")
    print("[*] 3. Select a device profile")
    print("[*] 4. Enter your game package name")
    print("[*] 5. Start your game in BlueStacks")
    print("[*] 6. Click 'Apply Spoof'")
    print("[*] 7. Watch logs to verify hooking")
    print("="*60 + "\n")
    
    # Start GUI
    root.mainloop()


if __name__ == "__main__":
    main()
