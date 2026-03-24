"""
FridaBypass Diagnostic Script
Helps troubleshoot Frida connection issues
"""

import frida
import subprocess
import sys


def check_adb_devices():
    """Check if ADB can see BlueStacks"""
    print("\n" + "="*60)
    print("1. Checking ADB Devices")
    print("="*60)
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        print(result.stdout)
        if "127.0.0.1" in result.stdout or "emulator" in result.stdout:
            print("✓ BlueStacks found in ADB devices")
            return True
        else:
            print("✗ BlueStacks NOT found - need to connect: adb connect 127.0.0.1:5555")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_frida_server():
    """Check if frida-server is running on BlueStacks"""
    print("\n" + "="*60)
    print("2. Checking Frida Server Status")
    print("="*60)
    try:
        result = subprocess.run(['adb', 'shell', 'ps'], capture_output=True, text=True)
        if 'frida-server' in result.stdout:
            print("✓ frida-server is RUNNING on BlueStacks")
            # Show the process line
            for line in result.stdout.split('\n'):
                if 'frida-server' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("✗ frida-server is NOT RUNNING")
            print("  Start it with: adb shell /data/local/tmp/frida-server -D")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_port_forward():
    """Check if port is forwarded"""
    print("\n" + "="*60)
    print("3. Checking Port Forward (TCP 27042)")
    print("="*60)
    try:
        result = subprocess.run(['adb', 'forward', '--list'], capture_output=True, text=True)
        print(result.stdout)
        if '27042' in result.stdout:
            print("✓ Port 27042 is FORWARDED")
            return True
        else:
            print("✗ Port NOT forwarded")
            print("  Forward it with: adb forward tcp:27042 tcp:27042")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def try_frida_connection():
    """Try different connection methods"""
    print("\n" + "="*60)
    print("4. Testing Frida Connection Methods")
    print("="*60)
    
    # Method 1: USB Device
    print("\n[A] Trying USB Device Connection...")
    try:
        device = frida.get_usb_device()
        processes = device.enumerate_processes()
        print(f"✓ USB Device Connected! Found {len(processes)} processes")
        print(f"  Device: {device}")
        return True
    except Exception as e:
        print(f"✗ USB Device failed: {type(e).__name__}: {e}")
    
    # Method 2: TCP Remote Device
    print("\n[B] Trying TCP Remote Device (127.0.0.1:27042)...")
    try:
        mgr = frida.get_device_manager()
        device = mgr.add_remote_device("tcp://127.0.0.1:27042")
        processes = device.enumerate_processes()
        print(f"✓ TCP Remote Device Connected! Found {len(processes)} processes")
        print(f"  Device: {device}")
        return True
    except Exception as e:
        print(f"✗ TCP Remote failed: {type(e).__name__}: {e}")
    
    # Method 3: Get Local Device
    print("\n[C] Trying Local Device...")
    try:
        device = frida.get_local_device()
        processes = device.enumerate_processes()
        print(f"✓ Local Device Connected! Found {len(processes)} processes")
        print(f"  Device: {device}")
        return True
    except Exception as e:
        print(f"✗ Local Device failed: {type(e).__name__}: {e}")
    
    return False


def list_frida_devices():
    """List all available Frida devices"""
    print("\n" + "="*60)
    print("5. Available Frida Devices")
    print("="*60)
    try:
        mgr = frida.get_device_manager()
        devices = mgr.enumerate_devices()
        if devices:
            for device in devices:
                print(f"  - {device.name} ({device.type}): {device.id}")
        else:
            print("✗ No devices found")
    except Exception as e:
        print(f"✗ Error: {e}")


def frida_ps_test():
    """Test frida-ps command"""
    print("\n" + "="*60)
    print("6. Testing frida-ps Command")
    print("="*60)
    try:
        result = subprocess.run(['frida-ps', '-Uai'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ frida-ps works! Showing processes...")
            lines = result.stdout.split('\n')[:10]  # Show first 10
            for line in lines:
                print(f"  {line}")
        else:
            print(f"✗ frida-ps failed: {result.stderr}")
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "FridaBypass - Diagnostic Tool".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    checks = [
        ("ADB Devices", check_adb_devices),
        ("Frida Server", check_frida_server),
        ("Port Forward", check_port_forward),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    try_frida_connection()
    list_frida_devices()
    frida_ps_test()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if all_passed:
        print("✓ All prerequisites are set up correctly")
        print("  Try running: python test_connection.py")
    else:
        print("✗ Some prerequisites are missing - see above for fixes")
    
    print()


if __name__ == "__main__":
    main()
