# FridaBypass Tool - PART 1: Frida Connector & Connection Test

## Overview
This part sets up the core Frida connector that handles communication between the FridaBypass tool and BlueStacks emulator.

## How It Works

### `connector.py` - The FridaConnector Class

The `FridaConnector` class manages:
- **Connection**: Establishes TCP connection to frida-server running on BlueStacks
- **Process Detection**: Finds the target game process by package name
- **Attachment**: Attaches Frida to the game process
- **Script Injection**: Injects JavaScript hooks into the process
- **Cleanup**: Safely disconnects and cleans up

### Key Methods

```python
connector = FridaConnector(frida_port=27042)

# Step 1: Connect to BlueStacks
connector.connect_to_device(host="127.0.0.1")

# Step 2: Find your game process
process = connector.get_process("com.example.game")

# Step 3: Attach to the game
connector.attach_to_process("com.example.game")

# Step 4: Inject hooks (next parts)
connector.inject_script(my_javascript_code)
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `frida`: The core Frida library
- `frida-tools`: Command-line tools and diagnostics

### 2. Setup BlueStacks + frida-server

#### a) Download frida-server
Download the correct version for your emulator:
- Go to: https://github.com/frida/frida/releases
- Download `frida-server-{version}-android-{arch}.xz`
- For most BlueStacks: use `arm64` version

#### b) Extract and Push to BlueStacks
```bash
# Extract the file
xz -d frida-server-*.xz

# Connect to BlueStacks
adb connect 127.0.0.1:5555

# Push frida-server to device
adb push frida-server /data/local/tmp/

# Make it executable
adb shell chmod +x /data/local/tmp/frida-server
```

#### c) Start frida-server
```bash
# Option 1: Start in background
adb shell /data/local/tmp/frida-server -D

# Option 2: Start with verbose output (for debugging)
adb shell /data/local/tmp/frida-server
```

#### d) Forward the Frida port
```bash
adb forward tcp:27042 tcp:27042
```

### 3. Test the Connection

```bash
# Run the test script
python test_connection.py
```

Expected output:
```
[+] Successfully connected! Found XX processes
✓ Connection test PASSED
[+] Found com.android.settings (PID: 1234)
✓ Process Detection test PASSED
```

## Architecture Diagram

```
Your Computer          BlueStacks Emulator
┌─────────────┐        ┌──────────────────┐
│ FridaBypass │        │   frida-server   │
│   (Python)  │◄──────►│  (running on     │
└─────────────┘ TCP    │   emulator)      │
              27042    └──────────────────┘
                              ▲
                              │ attaches
                              ▼
                        ┌──────────────────┐
                        │  Game Process    │
                        │ (com.example...)│
                        └──────────────────┘
```

## Troubleshooting

### "Frida server not running"
- Make sure frida-server is started: `adb shell ps | grep frida`
- Start it: `adb shell /data/local/tmp/frida-server -D`

### "Connection timed out"
- Check port forwarding: `adb forward --list`
- Re-forward if needed: `adb forward tcp:27042 tcp:27042`

### "Process not found"
- Make sure your game is actually running in BlueStacks
- Use `adb shell pm list packages | grep myapp` to verify package name

### "Permission denied"
- frida-server might need su access
- On some emulators: `adb shell su -c /data/local/tmp/frida-server -D`

## What's Next?

Once Part 1 is verified working ✓:
- **Part 2**: Create device profile JSON files (Samsung S22, Redmi Note 12, Pixel 7)
- **Part 3**: Write JavaScript hook scripts for Build properties and sensors
- **Part 4**: Build spoofer.py to load and inject profiles
- **Part 5**: Create Tkinter GUI
- **Part 6**: End-to-end testing with a real game

## Important Notes

✓ **Works fully client-side** - Only hooks run inside the game process
✓ **No network interception** - Server never sees anything unusual
✓ **Safe** - Only touches game detection code, not account data or tokens
✓ **Reversible** - When you disconnect, everything returns to normal

---

**Status**: ✓ Part 1 Complete - Connector Ready
