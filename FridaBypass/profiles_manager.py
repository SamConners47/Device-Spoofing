"""
FridaBypass Profile Manager
Loads and manages device spoofing profiles
"""

import json
import os
from typing import Dict, Optional, List


class ProfileManager:
    """Manages device spoofing profiles"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        """
        Initialize profile manager
        
        Args:
            profiles_dir (str): Directory containing device profiles
        """
        self.profiles_dir = profiles_dir
        self.profiles = {}
        self.load_all_profiles()
    
    def load_all_profiles(self) -> Dict[str, Dict]:
        """
        Load all profiles from the profiles directory
        
        Returns:
            Dict: Dictionary of profile name -> profile data
        """
        if not os.path.exists(self.profiles_dir):
            print(f"[-] Profiles directory not found: {self.profiles_dir}")
            return {}
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                profile_name = filename[:-5]  # Remove .json
                self.load_profile(profile_name)
        
        print(f"[+] Loaded {len(self.profiles)} device profiles")
        return self.profiles
    
    def load_profile(self, profile_name: str) -> Optional[Dict]:
        """
        Load a single profile by name
        
        Args:
            profile_name (str): Name of the profile (without .json)
            
        Returns:
            Dict: Profile data if successful, None otherwise
        """
        filepath = os.path.join(self.profiles_dir, f"{profile_name}.json")
        
        if not os.path.exists(filepath):
            print(f"[-] Profile not found: {profile_name}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                profile = json.load(f)
            
            self.profiles[profile_name] = profile
            print(f"[+] Loaded profile: {profile.get('displayName', profile_name)}")
            return profile
            
        except json.JSONDecodeError:
            print(f"[-] Invalid JSON in profile: {profile_name}")
            return None
        except Exception as e:
            print(f"[-] Error loading profile {profile_name}: {e}")
            return None
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """
        Get a profile by name
        
        Args:
            profile_name (str): Name of the profile
            
        Returns:
            Dict: Profile data if found, None otherwise
        """
        return self.profiles.get(profile_name)
    
    def get_all_profiles(self) -> Dict[str, Dict]:
        """Get all loaded profiles"""
        return self.profiles
    
    def list_profiles(self) -> List[str]:
        """
        List all available profiles
        
        Returns:
            List: List of profile display names
        """
        profiles_list = []
        for name, data in self.profiles.items():
            display_name = data.get('displayName', data.get('name', name))
            profiles_list.append(display_name)
        
        return sorted(profiles_list)
    
    def get_profile_by_display_name(self, display_name: str) -> Optional[Dict]:
        """
        Get profile by its display name
        
        Args:
            display_name (str): Display name of the profile
            
        Returns:
            Dict: Profile data if found, None otherwise
        """
        for profile_data in self.profiles.values():
            if profile_data.get('displayName') == display_name or profile_data.get('name') == display_name:
                return profile_data
        
        return None
    
    def build_property_map(self, profile: Dict) -> Dict[str, str]:
        """
        Create a map of Android system properties from profile
        
        Args:
            profile (Dict): Device profile
            
        Returns:
            Dict: Map of property names to values for spoofing
        """
        properties = {}
        
        # Build properties (read-only properties that games check)
        build_properties = {
            'MODEL': profile.get('model', 'UNKNOWN'),
            'BRAND': profile.get('brand', 'UNKNOWN'),
            'MANUFACTURER': profile.get('manufacturer', 'UNKNOWN'),
            'HARDWARE': profile.get('hardware', 'UNKNOWN'),
            'DEVICE': profile.get('device', 'UNKNOWN'),
            'PRODUCT': profile.get('product', 'UNKNOWN'),
            'BOARD': profile.get('board', 'UNKNOWN'),
            'FINGERPRINT': profile.get('fingerprint', ''),
            'TYPE': 'user',
            'DISPLAY': profile.get('buildVersion', ''),
            'ID': profile.get('buildId', ''),
            'VERSION': profile.get('buildVersion', ''),
        }
        
        # Prefix with Build.
        for key, value in build_properties.items():
            properties[f'Build.{key}'] = value
        
        # System properties (ro.* properties)
        system_properties = {
            'ro.kernel.qemu': profile.get('ro.kernel.qemu', '0'),
            'ro.product.cpu.abi': profile.get('ro.product.cpu.abi', 'arm64-v8a'),
            'ro.product.cpu.abilist': profile.get('ro.product.cpu.abilist', 'arm64-v8a'),
            'ro.build.display.id': profile.get('buildVersion', ''),
            'ro.build.id': profile.get('buildId', ''),
            'ro.build.version.release': profile.get('androidVersion', '13'),
            'ro.build.version.sdk': profile.get('sdkVersion', '33'),
            'ro.hardware': profile.get('hardware', 'UNKNOWN'),
            'ro.biometric.face': profile.get('ro.biometric.face', '0'),
            'ro.biometric.fingerprint': profile.get('ro.biometric.fingerprint', '0'),
        }
        
        properties.update(system_properties)
        
        return properties
    
    def get_sensor_config(self, profile: Dict) -> Dict[str, bool]:
        """
        Get sensor configuration from profile
        
        Args:
            profile (Dict): Device profile
            
        Returns:
            Dict: Sensor name -> availability
        """
        return profile.get('sensors', {
            'accelerometer': True,
            'magnetometer': True,
            'gyroscope': True,
            'proximity': True,
            'light': True,
            'pressure': True,
        })


# Simple test
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ProfileManager Test")
    print("="*60)
    
    # Load profiles
    manager = ProfileManager()
    
    # List available profiles
    print("\nAvailable profiles:")
    for profile in manager.list_profiles():
        print(f"  - {profile}")
    
    # Get Samsung S22 profile
    print("\n" + "="*60)
    print("Samsung S22 Profile Details")
    print("="*60)
    
    profile = manager.get_profile("samsung_s22")
    if profile:
        print(f"Name: {profile.get('displayName')}")
        print(f"Model: {profile.get('model')}")
        print(f"Brand: {profile.get('brand')}")
        print(f"Hardware: {profile.get('hardware')}")
        print(f"Fingerprint: {profile.get('fingerprint')}")
        
        # Show property map
        print("\nBuild Properties:")
        prop_map = manager.build_property_map(profile)
        for key, value in sorted(prop_map.items()):
            if 'Build.' in key:
                print(f"  {key}: {value}")
        
        # Show sensors
        print("\nSensors:")
        sensors = manager.get_sensor_config(profile)
        for sensor, available in sensors.items():
            status = "✓" if available else "✗"
            print(f"  {status} {sensor}")
