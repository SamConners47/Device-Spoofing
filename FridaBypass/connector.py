"""
FridaBypass Connector Module
Connects to BlueStacks via Frida and manages the session with target game process.
"""

import frida
import time
from typing import Optional, Any


class FridaConnector:
    """Manages Frida connection to BlueStacks emulator"""
    
    def __init__(self, frida_port: int = 27042):
        """
        Initialize Frida connector
        
        Args:
            frida_port (int): Port where frida-server is running on BlueStacks (default 27042)
        """
        self.frida_port = frida_port
        self.device = None
        self.session = None
        self.script = None
        self.is_connected = False
        self.target_process = None
        
    def connect_to_device(self, host: str = "127.0.0.1") -> bool:
        """
        Establish connection to frida-server on BlueStacks
        
        Args:
            host (str): IP address of BlueStacks (usually localhost)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"[*] Connecting to Frida server at {host}:{self.frida_port}...")
            
            # Method 1: Try USB device (for ADB connected devices)
            try:
                print("[*] Attempting connection via USB/ADB device...")
                self.device = frida.get_usb_device()
                print("[+] Connected via USB device")
            except:
                # Method 2: Try remote device with TCP connection
                print("[*] USB method failed, trying TCP remote connection...")
                device_uri = f"tcp://{host}:{self.frida_port}"
                self.device = frida.get_device_manager().add_remote_device(device_uri)
                print(f"[+] Connected via TCP: {device_uri}")
            
            # Test connection by enumerating processes
            print("[*] Enumerating processes...")
            processes = self.device.enumerate_processes()
            
            if processes:
                print(f"[+] Successfully connected! Found {len(processes)} processes")
                self.is_connected = True
                return True
            else:
                print("[-] Connected but no processes found. Check frida-server status.")
                return False
                
        except frida.ServerNotRunningError:
            print(f"[-] Error: Frida server not running")
            print("[!] Make sure frida-server is running on BlueStacks:")
            print("    1. adb shell /data/local/tmp/frida-server -D")
            print("    2. adb forward tcp:27042 tcp:27042")
            print("    3. Verify: adb shell ps | grep frida-server")
            return False
            
        except frida.TimedOutError:
            print(f"[-] Error: Connection timed out")
            print("[!] Check that BlueStacks is running and frida-server is accessible")
            print("    adb forward --list")
            return False
            
        except Exception as e:
            print(f"[-] Error connecting to Frida: {type(e).__name__}: {e}")
            print("[!] Troubleshooting steps:")
            print("    1. Check BlueStacks is running: adb devices")
            print("    2. Check frida-server: adb shell ps | grep frida")
            print("    3. Check port forward: adb forward --list")
            print("    4. Try restarting: adb kill-server && adb devices")
            return False
    
    def get_process(self, package_name: str) -> Optional[Any]:
        """
        Find and return the target process by package name
        
        Args:
            package_name (str): Android package name (e.g., com.example.game)
            
        Returns:
            Process object if found, None otherwise
        """
        if not self.is_connected:
            print("[-] Not connected to device. Call connect_to_device() first.")
            return None
            
        try:
            print(f"[*] Looking for process: {package_name}")
            processes = self.device.enumerate_processes()
            
            for process in processes:
                if package_name in process.name or process.name == package_name:
                    print(f"[+] Found process: {process.name} (PID: {process.pid})")
                    self.target_process = process
                    return process
            
            print(f"[-] Process '{package_name}' not found")
            print(f"[!] Available processes containing keyword:")
            
            # Show first 20 processes for debugging
            for process in processes[:20]:
                print(f"    - {process.name} (PID: {process.pid})")
            
            return None
            
        except Exception as e:
            print(f"[-] Error finding process: {e}")
            return None
    
    def attach_to_process(self, package_name: str) -> bool:
        """
        Attach Frida to the target game process
        
        Args:
            package_name (str): Android package name
            
        Returns:
            bool: True if attachment successful, False otherwise
        """
        if not self.is_connected:
            print("[-] Not connected to device")
            return False
        
        try:
            process = self.get_process(package_name)
            
            if not process:
                print(f"[-] Could not find process {package_name}")
                return False
            
            print(f"[*] Attaching to process {package_name} (PID: {process.pid})...")
            self.session = self.device.attach(process.pid)
            print(f"[+] Successfully attached to process!")
            return True
            
        except frida.ProcessNotFoundError:
            print(f"[-] Process {package_name} not found or crashed")
            return False
            
        except frida.PermissionDeniedError:
            print(f"[-] Permission denied: Cannot attach to {package_name}")
            print("[!] frida-server might need higher privileges")
            return False
            
        except Exception as e:
            print(f"[-] Error attaching to process: {e}")
            return False
    
    def inject_script(self, js_code: str) -> bool:
        """
        Inject JavaScript code into the attached process
        
        Args:
            js_code (str): JavaScript code to inject
            
        Returns:
            bool: True if injection successful, False otherwise
        """
        if not self.session:
            print("[-] Not attached to any process. Call attach_to_process() first.")
            return False
        
        try:
            print("[*] Injecting JavaScript hook...")
            self.script = self.session.create_script(js_code)
            self.script.on("message", self._on_message)
            self.script.load()
            print("[+] Script injected successfully!")
            return True
            
        except Exception as e:
            print(f"[-] Error injecting script: {e}")
            return False
    
    def send_message(self, message_data: dict):
        """
        Send a message to the injected script
        
        Args:
            message_data (dict): Message data to send
        """
        if self.script:
            self.script.post(message_data)
    
    def _on_message(self, message, data):
        """Handle messages from injected script"""
        if message["type"] == "send":
            print(f"[Script] {message['payload']}")
        elif message["type"] == "error":
            print(f"[Script Error] {message['stack']}")
    
    def disconnect(self):
        """Clean up and disconnect from Frida"""
        try:
            if self.script:
                self.script.unload()
            if self.session:
                self.session.detach()
            if self.device:
                self.device = None
            self.is_connected = False
            print("[+] Disconnected from Frida")
        except Exception as e:
            print(f"[-] Error during disconnect: {e}")
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.disconnect()


# Simple test/demo code
if __name__ == "__main__":
    print("=" * 60)
    print("FridaBypass - Connector Test")
    print("=" * 60)
    
    # Test connection
    connector = FridaConnector(frida_port=27042)
    
    if connector.connect_to_device():
        print("\n[*] Connection test passed!")
        print("[*] Ready for spoof injection")
    else:
        print("\n[-] Connection test failed")
        print("[!] Setup checklist:")
        print("    1. Start BlueStacks emulator")
        print("    2. Connect ADB: adb connect 127.0.0.1:5555")
        print("    3. Push frida-server: adb push frida-server /data/local/tmp/")
        print("    4. Start frida-server: adb shell /data/local/tmp/frida-server -D")
        print("    5. Forward port: adb forward tcp:27042 tcp:27042")
