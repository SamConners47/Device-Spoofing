"""
FridaBypass Spoofer Module
Loads device profiles and JavaScript hooks, then injects them into the target game
"""

import os
import json
from typing import Optional, Dict
from connector import FridaConnector
from profiles_manager import ProfileManager


class FridaSpoofer:
    """Handles spoofing by loading profiles and injecting hooks"""
    
    def __init__(self, profiles_dir: str = "profiles", hooks_dir: str = "hooks"):
        """
        Initialize spoofer
        
        Args:
            profiles_dir (str): Directory with device profiles
            hooks_dir (str): Directory with JavaScript hooks
        """
        self.profiles_dir = profiles_dir
        self.hooks_dir = hooks_dir
        self.profile_manager = ProfileManager(profiles_dir)
        self.connector = None
        self.hooks = {}
        self.active_profile = None
        
        # Load all hook scripts
        self._load_hooks()
    
    def _load_hooks(self):
        """Load all JavaScript hook files"""
        hook_files = {
            'build_hook': 'build_hook.js',
            'sensor_hook': 'sensor_hook.js',
            'qemu_hook': 'qemu_hook.js',
            'filesystem_hook': 'filesystem_hook.js',
            'device_id_hook': 'device_id_hook.js',
            'network_hook': 'network_hook.js',
            'process_hook': 'process_hook.js'
        }
        
        for hook_name, filename in hook_files.items():
            filepath = os.path.join(self.hooks_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        self.hooks[hook_name] = f.read()
                    print(f"[+] Loaded hook: {hook_name}")
                except Exception as e:
                    print(f"[-] Error loading {hook_name}: {e}")
            else:
                # Advanced hooks are optional
                if hook_name in ['filesystem_hook', 'device_id_hook', 'network_hook', 'process_hook']:
                    print(f"[!] Optional advanced hook not found: {hook_name}")
                else:
                    print(f"[-] Hook not found: {filepath}")
    
    def connect_to_bluestacks(self, host: str = "127.0.0.1", port: int = 27042) -> bool:
        """
        Connect to BlueStacks via Frida
        
        Args:
            host (str): IP address of BlueStacks
            port (int): Frida server port
            
        Returns:
            bool: True if connection successful
        """
        self.connector = FridaConnector(frida_port=port)
        return self.connector.connect_to_device(host=host)
    
    def select_profile(self, profile_name: str) -> bool:
        """
        Select a device profile to spoof
        
        Args:
            profile_name (str): Profile display name or key
            
        Returns:
            bool: True if profile found and selected
        """
        # Try as display name first
        profile = self.profile_manager.get_profile_by_display_name(profile_name)
        
        # Try as key if not found
        if not profile:
            profile = self.profile_manager.get_profile(profile_name)
        
        if profile:
            self.active_profile = profile
            print(f"[+] Selected profile: {profile.get('displayName', profile_name)}")
            return True
        else:
            print(f"[-] Profile not found: {profile_name}")
            print(f"    Available: {', '.join(self.profile_manager.list_profiles())}")
            return False
    
    def _build_injection_code(self) -> str:
        """
        Build the complete JavaScript code to inject
        Combines all hooks with the profile properties
        
        Returns:
            str: Complete JavaScript code ready for injection
        """
        if not self.active_profile:
            raise ValueError("No profile selected. Call select_profile() first.")
        
        # Get property map from profile
        properties = self.profile_manager.build_property_map(self.active_profile)
        sensors = self.profile_manager.get_sensor_config(self.active_profile)
        
        # Convert properties dict to JavaScript object
        properties_json = json.dumps(properties)
        sensors_json = json.dumps(sensors)
        
        # Build the complete script
        script = f"""
// FridaBypass - Complete Injection Script
// This script applies all spoofing hooks together

var properties = {properties_json};
var sensors = {sensors_json};

console.log("[*] ========================================");
console.log("[*] FridaBypass Device Spoofer v2 (Advanced)");
console.log("[*] Profile: {self.active_profile.get('displayName')}");
console.log("[*] ========================================");

// Load hook functions inline
{self.hooks.get('build_hook', '')}

{self.hooks.get('qemu_hook', '')}

{self.hooks.get('sensor_hook', '')}

{self.hooks.get('filesystem_hook', '')}

{self.hooks.get('device_id_hook', '')}

{self.hooks.get('network_hook', '')}

{self.hooks.get('process_hook', '')}

// Execute all hooks in sequence
console.log("[*] Applying spoofing hooks...");

// Layer 1: Build properties
try {{
    buildHook(properties);
    hookSystemProperties(properties);
    console.log("[+] Build property hooks applied!");
}} catch (e) {{
    console.log("[-] Build hook error: " + e);
}}

// Layer 2: QEMU detection
try {{
    qemuHook(properties);
    fingerprintHook(properties);
    deviceIdentifierHook(properties);
    console.log("[+] QEMU detection hooks applied!");
}} catch (e) {{
    console.log("[-] QEMU hook error: " + e);
}}

// Layer 3: Sensors
try {{
    sensorHook(sensors);
    console.log("[+] Sensor hooks applied!");
}} catch (e) {{
    console.log("[-] Sensor hook error: " + e);
}}

// Layer 4: Advanced - File System
try {{
    fileSystemHook();
    fileReadingHook();
    processExecutionHook();
    console.log("[+] File system hooks applied!");
}} catch (e) {{
    console.log("[!] File system hook error (optional): " + e);
}}

// Layer 5: Advanced - Device IDs
try {{
    deviceIdHook(properties);
    uuidHook();
    secureIdHook(properties);
    console.log("[+] Device ID hooks applied!");
}} catch (e) {{
    console.log("[!] Device ID hook error (optional): " + e);
}}

// Layer 6: Advanced - Network
try {{
    macAddressHook(properties);
    networkInterfaceHook();
    bluetoothHook(properties);
    connectivityHook();
    console.log("[+] Network hooks applied!");
}} catch (e) {{
    console.log("[!] Network hook error (optional): " + e);
}}

// Layer 7: Advanced - Processes
try {{
    processTableHook();
    appProcessListHook();
    packageManagerHook();
    console.log("[+] Process hooks applied!");
}} catch (e) {{
    console.log("[!] Process hook error (optional): " + e);
}}

console.log("[+] ========================================");
console.log("[+] FridaBypass Advanced Spoofing Complete!");
console.log("[+] Device is fully spoofed as real phone");
console.log("[+] ========================================");

send({{
    type: "spoofing_complete",
    profile: "{self.active_profile.get('displayName')}",
    version: "advanced",
    properties_applied: Object.keys(properties).length,
    hooks_count: 7
}});
"""
        return script
    
    def spoof_game(self, package_name: str) -> bool:
        """
        Attach to game and apply spoofing
        
        Args:
            package_name (str): Android package name of the game
            
        Returns:
            bool: True if spoofing successful
        """
        if not self.connector or not self.connector.is_connected:
            print("[-] Not connected to BlueStacks. Call connect_to_bluestacks() first.")
            return False
        
        if not self.active_profile:
            print("[-] No profile selected. Call select_profile() first.")
            return False
        
        try:
            # Attach to the game process
            print(f"[*] Attaching to game: {package_name}")
            if not self.connector.attach_to_process(package_name):
                return False
            
            # Build and inject the spoofing code
            print(f"[*] Injecting spoofing hooks...")
            injection_code = self._build_injection_code()
            
            if not self.connector.inject_script(injection_code):
                return False
            
            print(f"[+] Spoofing active! Game think it's on real device.")
            return True
            
        except Exception as e:
            print(f"[-] Error during spoofing: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Frida"""
        if self.connector:
            self.connector.disconnect()
            print("[+] Disconnected from Frida")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("FridaBypass Spoofer - Test Mode")
    print("="*60)
    
    # Initialize spoofer
    spoofer = FridaSpoofer()
    
    # List available profiles
    print("\nAvailable profiles:")
    for profile in spoofer.profile_manager.list_profiles():
        print(f"  - {profile}")
    
    # Show hook information
    print(f"\nLoaded hooks: {', '.join(spoofer.hooks.keys())}")
    
    print("\n" + "="*60)
    print("Usage Example:")
    print("="*60)
    print("""
# Initialize
spoofer = FridaSpoofer()

# Connect to BlueStacks
spoofer.connect_to_bluestacks("127.0.0.1", 27042)

# Select device to spoof
spoofer.select_profile("Samsung Galaxy S22")

# Attach to your game and spoof it
spoofer.spoof_game("com.example.game")

# Disconnect when done
spoofer.disconnect()
    """)
