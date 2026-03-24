# FridaBypass Tool - PART 5: Tkinter GUI Application

## Overview
This is the final part of FridaBypass - a complete graphical user interface (GUI) that brings all the spoofing functionality together in an easy-to-use application.

## User Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│           FridaBypass - Device Spoofer                  │
├─────────────────────────────────────────────────────────┤
│ BlueStacks Connection                                   │
│ Frida Server Port: [27042    ]  [Connect to BlueStacks] │
│ Status: Not connected                                   │
├─────────────────────────────────────────────────────────┤
│ Spoofing Configuration                                  │
│ Device Profile:     [Samsung Galaxy S22        ▼]      │
│ Game Package Name:  [com.example.game         ]        │
│                                    [Apply Spoof]       │
│ Spoof Status: Idle                                      │
├─────────────────────────────────────────────────────────┤
│ Selected Profile Details                                │
│ Model: SM-S901B                                         │
│ Brand: samsung                                          │
│ Hardware: qcom                                          │
│ Android Version: 13                                     │
├─────────────────────────────────────────────────────────┤
│ Activity Logs                                           │
│ [========================================]              │
│ [*] FridaBypass Tool - Initialized                    │
│ [+] Successfully connected to BlueStacks!             │
│ [*] Profile: Samsung Galaxy S22                       │
│ [+] SPOOFING SUCCESSFUL!                              │
│                                    [Clear Logs]        │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. Connection Management
- **Port Configuration**: Set Frida server port (default 27042)
- **Connect Button**: Establishes connection to BlueStacks
- **Status Display**: Shows connection state with visual indicator
- **Error Handling**: Display helpful error messages

### 2. Device Profile Selection
- **Profile Dropdown**: Choose from 3 pre-configured device profiles
  - Samsung Galaxy S22
  - Xiaomi Redmi Note 12
  - Google Pixel 7
- **Profile Details**: Shows selected device info below
- **Easy Selection**: Simple dropdown interface

### 3. Game Configuration
- **Package Name Input**: Enter your Andorid game package name
  - Example: `com.example.mygame`
  - Example: `com.supercell.clashroyale`
- **Real-time Validation**: Input field for easy entry

### 4. Spoofing Control
- **Apply Spoof Button**: Activates spoofing hooks
- **Status Updates**: Real-time feedback during application
- **Thread-based**: Doesn't freeze UI during operations

### 5. Activity Logs
- **Real-time Updates**: Shows all operations as they happen
- **Scrolling Display**: Auto-scrolls to show latest entries
- **Clear Functionality**: Clear logs when needed
- **Detailed Output**: Shows hook loading, connection steps, etc.

## How to Use

### Step 1: Launch the Application
```bash
cd FridaBypass
python main.py
```

Expected output:
```
============================================================
FridaBypass Tool - Initialized
============================================================
[*] Welcome to FridaBypass!
[*] Device Spoofer for Android Games
[*] 
[*] Steps:
[*] 1. Enter Frida server port (default 27042)
[*] 2. Click 'Connect to BlueStacks'
[*] 3. Select a device profile
[*] 4. Enter your game package name
[*] 5. Start your game in BlueStacks
[*] 6. Click 'Apply Spoof'
[*] 7. Watch logs to verify hooking
============================================================
```

### Step 2: Connect to BlueStacks
1. Make sure BlueStacks is running
2. Make sure frida-server is running on BlueStacks:
   ```bash
   adb shell /data/local/tmp/frida-server -D
   adb forward tcp:27042 tcp:27042
   ```
3. Enter port (default 27042) in the GUI
4. Click "Connect to BlueStacks"
5. Status should change to "✓ Connected"

### Step 3: Configure Spoofing
1. **Select Device Profile**: Choose from dropdown
   - Samsung Galaxy S22 (premium flagship)
   - Xiaomi Redmi Note 12 (mid-range)
   - Google Pixel 7 (stock Android)

2. **Enter Game Package**: Type your game's package name
   - Find it with: `adb shell pm list packages | grep myapp`

### Step 4: Start Your Game
1. Launch your game in BlueStacks
2. Wait for it to fully load

### Step 5: Apply Spoofing
1. Click "Apply Spoof" button
2. Watch the logs for verification:
   ```
   [*] Attaching to process com.example.game
   [+] Successfully attached!
   [*] Injecting spoofing hooks...
   [+] Build property hooks applied!
   [+] QEMU detection hooks applied!
   [+] Sensor hooks applied!
   [+] File system hooks applied!
   [+] Device ID hooks applied!
   [+] Network hooks applied!
   [+] Process hooks applied!
   [+] SPOOFING SUCCESSFUL!
   ```

### Step 6: Play Your Game
- Game now sees spoofed device properties
- All 7 layers of hooking are active
- Enjoy playing!

## GUI Components

### FridaBypassGUI Class

**Initialization:**
```python
gui = FridaBypassGUI(root)
```

Initializes:
- Spoofer instance (loads all profiles + hooks)
- Profile manager (manages device profiles)
- Log queue (captures print statements)
- Tkinter UI components

**Threading Model:**
- Main UI thread: Responsive GUI
- Connection thread: Handles BlueStacks connection
- Spoofing thread: Applies hooks without freezing UI
- Log thread: Updates display from queue

### Key Methods

**`_connect_bluestacks()`**
- Runs connection in separate thread
- Updates status display
- Enables/disables buttons based on state

**`_apply_spoof()`**
- Validates input (profile selected, package entered)
- Runs spoofing in separate thread
- Updates spoof status in real-time

**`_update_logs()`**
- Checks log queue every 100ms
- Displays messages in log text area
- Auto-scrolls to bottom

**`_update_profile_info()`**
- Shows details of selected profile
- Displays: model, brand, hardware, Android version, fingerprint

## Technical Architecture

```
┌──────────────────┐
│  main.py (GUI)   │
└────────┬─────────┘
         │
    ┌────┴──────┬──────────┬─────────────┐
    │            │          │             │
   ▼            ▼          ▼             ▼
┌────────┐  ┌────────┐  ┌──────────┐  ┌────────────┐
│Tkinter │  │Spoofer │  │Connector │  │ProfileMgr  │
│  GUI   │  │        │  │          │  │            │
└────────┘  └────────┘  └──────────┘  └────────────┘
    │            │          │             │
    │            └────┬─────┘             │
    │                 │                   │
    │            ┌────▼────┐              │
    │            │  Frida   │             │
    │            │ (7 Hooks)│             │
    │            └────┬────┘              │
    │                 │                   │
    └─────────────────┼───────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │  BlueStacks App  │
              │  (Spoofed Game)  │
              └──────────────────┘
```

## Running Multiple Games

**Note:** Each spoofing session is independent. To spoof a different game:

1. Click "Apply Spoof" again with a different package name
2. Or in code:
   ```python
   spoofer.spoof_game("com.game.one")
   # Game 1 running spoofed...
   
   spoofer.spoof_game("com.game.two")  
   # Game 2 running spoofed...
   ```

## Troubleshooting

### Connection Issues

**Problem:** "Not connected" after clicking Connect
```
[*] Connecting to BlueStacks on port 27042...
[!] ServerNotRunningError: Frida server not running
```

**Solution:**
```bash
# Start frida-server
adb shell /data/local/tmp/frida-server -D

# Forward port
adb forward tcp:27042 tcp:27042

# Try again in GUI
```

### Package Not Found

**Problem:** "Process not found" in logs after clicking Apply Spoof
```
[-] Process 'com.example.game' not found
```

**Solution:**
1. Verify package name: `adb shell pm list packages | grep game`
2. Ensure game is actually running in BlueStacks
3. Check spelling in GUI input

### Spoofing Not Working

**Problem:** Game still says it's on emulator despite spoofing

**Causes:**
1. Game uses native code detection (out of scope)
2. Game uses server-side validation
3. Hooks didn't fully load

**Solutions:**
- Check logs for hook loading errors
- Try different device profile
- Some games require Magisk + custom hooks

## Customization

### Adding New Device Profiles

1. Create new JSON in `profiles/`:
   ```json
   {
     "name": "iPhone Simulator",
     "displayName": "iPhone Simulator",
     "model": "iPhone14,2",
     "brand": "apple",
     ...
   }
   ```

2. It automatically appears in dropdown next launch

### Modifying Hook Behavior

1. Edit hook scripts in `hooks/`:
   ```javascript
   // Example: Add custom property
   Build.CUSTOM_PROP.value = "my_value";
   ```

2. Changes take effect on next "Apply Spoof"

### Extending the GUI

Add new features by extending `FridaBypassGUI`:
```python
def _add_custom_feature(self):
    """Your new feature"""
    pass
```

## Advanced Features

### Logging to File

```python
# In PART5 of main.py, add:
log_file = open("spoof.log", "w")

def logged_print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    log_file.write(message + "\n")
    log_file.flush()
    # ... send to queue
```

### Save/Load Configuration

```python
# Save settings
config = {
    'port': self.port_var.get(),
    'profile': self.profile_var.get(),
    'package': self.package_var.get()
}
with open('config.json', 'w') as f:
    json.dump(config, f)

# Load on startup
with open('config.json', 'r') as f:
    config = json.load(f)
    self.port_var.set(config['port'])
```

### Multiple Device Sessions

```python
spoofer1 = FridaSpoofer()
spoofer2 = FridaSpoofer()

spoofer1.spoof_game("com.game.one")
spoofer2.spoof_game("com.game.two")
# Both games running simultaneously, each spoofed
```

## Performance Considerations

- **Thread Safety**: All Frida operations run in separate threads
- **UI Responsiveness**: Main thread never blocks
- **Memory**: Each spoofer instance ~2-5MB
- **Log Display**: Auto-truncates after 10,000 lines (configurable)

## Safety & Security

✓ **No account data touched** - Only game process memory
✓ **No network modification** - All local
✓ **Reversible** - Disconnect to restore normal behavior
✓ **Safe** - Can't crash device, only game process
✓ **Isolated** - Other apps completely unaffected

## Final Checklist

Before using:
- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] BlueStacks running
- [ ] frida-server running on emulator
- [ ] Port forwarded (adb forward tcp:27042 tcp:27042)
- [ ] Game package name correct

When spoofing:
- [ ] Logs show "Successfully connected!"
- [ ] Profile details display correctly
- [ ] Game is running in BlueStacks
- [ ] Logs show "SPOOFING SUCCESSFUL!"

## The Complete FridaBypass Experience

```
You write code → FridaBypass transforms your Android game experience
                ↓
         ┌──────────────────────┐
         │    Your Game         │
         │  (Thinks it's on     │
         │   Samsung S22)       │
         └──────────────────────┘
                ↑
         ┌──────────────────────┐
         │  7-Layer Spoofing    │
         │  (Transparent)       │
         └──────────────────────┘
                ↑
         ┌──────────────────────┐
         │  BlueStacks          │
         │  (Emulator)          │
         └──────────────────────┘
```

---

**Status**: ✓ Part 5 Complete - Full GUI Application Ready

**Project Complete!** 🎉

All 5 parts are now ready:
- Part 1: ✓ Frida Connector
- Part 2: ✓ Device Profiles
- Part 3: ✓ JavaScript Hooks
- Part 4: ✓ Advanced Features
- Part 5: ✓ GUI Application

**To start using FridaBypass:**
```bash
python main.py
```

Enjoy spoofing! 🚀
