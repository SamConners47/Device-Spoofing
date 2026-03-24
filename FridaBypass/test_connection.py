"""
Test script for FridaBypass Connector
Tests connection to BlueStacks and basic process detection
"""

from connector import FridaConnector


def test_basic_connection():
    """Test 1: Basic connection to Frida server"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Frida Connection")
    print("=" * 60)
    
    connector = FridaConnector(frida_port=27042)
    
    if connector.connect_to_device(host="127.0.0.1"):
        print("✓ Connection test PASSED")
        return connector
    else:
        print("✗ Connection test FAILED")
        print("\nMake sure to:")
        print("  1. Start BlueStacks emulator")
        print("  2. Connect: adb connect 127.0.0.1:5555")
        print("  3. Push frida-server: adb push frida-server /data/local/tmp/")
        print("  4. Start server: adb shell /data/local/tmp/frida-server -D")
        print("  5. Forward: adb forward tcp:27042 tcp:27042")
        return None


def test_process_detection(connector):
    """Test 2: Detect specific process"""
    print("\n" + "=" * 60)
    print("TEST 2: Process Detection")
    print("=" * 60)
    
    # Try to find a common app
    test_packages = [
        "com.android.settings",      # Settings always exists
        "com.android.systemui",      # System UI
        "com.google.android.gms"     # Google Play Services (usually present)
    ]
    
    for package in test_packages:
        process = connector.get_process(package)
        if process:
            print(f"✓ Found {package} (PID: {process.pid})")
            return
    
    print("✗ Could not find test processes")
    print("Note: This is OK - your target game just needs to be running")


def test_injection_code():
    """Test 3: Show example injection code"""
    print("\n" + "=" * 60)
    print("TEST 3: Example Hook Code")
    print("=" * 60)
    
    example_hook = """
    Java.perform(function() {
        var Build = Java.use("android.os.Build");
        
        // Hook Build.MODEL
        Build.MODEL.value = "SM-S901B";
        
        // Hook Build.BRAND
        Build.BRAND.value = "samsung";
        
        send({
            "type": "info",
            "message": "Device spoofed to Samsung S22"
        });
    });
    """
    
    print("Example JavaScript hook:")
    print(example_hook)
    print("✓ This is what gets injected into the game process")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "FridaBypass Tool - Connection Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Test 1: Basic connection
    connector = test_basic_connection()
    
    if connector is None:
        print("\n[-] Cannot continue without successful connection")
        return
    
    # Test 2: Process detection
    test_process_detection(connector)
    
    # Test 3: Show hook example
    test_injection_code()
    
    # Cleanup
    connector.disconnect()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\n[i] Next steps:")
    print("    1. Make sure your game is running in BlueStacks")
    print("    2. Update test_packages list with your game's package name")
    print("    3. Verify process is detected")
    print("    4. Then move to Part 2: Device Profiles")


if __name__ == "__main__":
    main()
