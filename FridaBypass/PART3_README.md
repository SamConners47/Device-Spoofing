# FridaBypass Tool - PART 3: JavaScript Hook Scripts

## Overview
This part contains the JavaScript hook scripts that will be injected into the game process. These scripts intercept and spoof device properties in real-time.

## The Three Hooks

### 1. build_hook.js - Build Property Spoofing

**What it does:** Hooks into Android's `Build` class to spoof device properties.

**Properties spoofed:**
- `Build.MODEL` - Device model (e.g., SM-S901B)
- `Build.BRAND` - Manufacturer (samsung, google, xiaomi)
- `Build.MANUFACTURER` - OEM name
- `Build.HARDWARE` - Hardware identifier
- `Build.DEVICE` - Device codename
- `Build.PRODUCT` - Product name
- `Build.FINGERPRINT` - Complete device fingerprint
- `Build.ID` and `Build.VERSION` - Build identifiers

**Also hooks:**
- `SystemProperties.get()` - For `ro.*` system properties
  - `ro.kernel.qemu` - Set to "0" (not emulator)
  - `ro.product.cpu.abi` - CPU architecture
  - `ro.build.version.release` - Android version
  - `ro.hardware` - Hardware type

**Example:**
```javascript
// Before hook: Build.MODEL = "generic"
// Game check: if (Build.MODEL.equals("generic")) REJECT()
// After hook: Build.MODEL = "SM-S901B"  
// Game passes!
```

### 2. qemu_hook.js - Emulator Detection Hiding

**What it does:** Hides telltale signs that we're running on an emulator.

**Detects and hides:**
- `Build.HARDWARE = "goldfish"` or `"ranchu"` → Changes to real value
- `Build.FINGERPRINT = "unknown"` → Replaces with real fingerprint
- `Build.DEVICE = "generic"` → Changes to real device codename
- `ro.kernel.qemu = "1"` → Sets to "0"
- `ro.serialno = "UNKNOWN"` → Generates realistic serial

**Why it matters:**
Most games check basic emulator flags:
```java
// Typical game anti-cheat check
String hardware = Build.HARDWARE;
if (hardware.contains("goldfish") || hardware.contains("ranchu")) {
    return false; // Detected emulator, crash or block game
}
```

Our hook intercepts this BEFORE the game runs the check.

**Example:**
```javascript
// Before: Build.HARDWARE = "ranchu" (BlueStacks emulator)
// After hook: Build.HARDWARE = "qcom" (real device)
// Game anti-cheat: ✓ PASSED
```

### 3. sensor_hook.js - Sensor Availability Spoofing

**What it does:** Fakes which sensors are available on the device.

**Sensor types:**
```javascript
1  = Accelerometer     (motion detection)
2  = Magnetometer      (compass)
4  = Gyroscope         (rotation sensing)
5  = Light             (brightness sensor)
6  = Pressure          (barometer)
8  = Proximity         (phone in pocket detector)
```

**Why it matters:**
Some games require specific sensors:
```java
// Games might check for gyroscope
SensorManager sm = (SensorManager) getSystemService(SENSOR_SERVICE);
Sensor gyro = sm.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
if (gyro == null) {
    showError("This game requires a gyroscope");
}
```

Our hook makes non-existent sensors available.

**Two modes:**
1. **Simple mode** - Returns fake sensor objects
2. **Advanced mode** - Hooks SensorManager to return faked sensor data

## The Spoofer Module (spoofer.py)

**FridaSpoofer** combines all hooks with a device profile and injects them.

### Usage Flow

```python
from spoofer import FridaSpoofer

# 1. Initialize spoofer (loads profiles and hooks)
spoofer = FridaSpoofer()

# 2. Connect to BlueStacks
spoofer.connect_to_bluestacks("127.0.0.1", 27042)

# 3. Select the device to spoof
spoofer.select_profile("Samsung Galaxy S22")

# 4. Attach to game and apply spoofing
spoofer.spoof_game("com.example.mygame")

# 5. Disconnect when done
spoofer.disconnect()
```

### What Happens During Spoofing

1. **Load Profile** - Gets Samsung S22 properties from JSON
2. **Build Injection Code** - Combines profiles + all hooks + properties into one JavaScript file
3. **Attach to Process** - Frida attaches to the game process (PID)
4. **Inject Script** - JavaScript is loaded into game's memory space
5. **Hooks Activate** - All property accesses are intercepted
6. **Spoofing Active** - Game sees all fake properties as real

## Injection Code Structure

The final injected code looks like:

```javascript
// Properties from profile
var properties = {
    "Build.MODEL": "SM-S901B",
    "Build.BRAND": "samsung",
    "ro.kernel.qemu": "0",
    ...
};

// Sensor configuration
var sensors = {
    "accelerometer": true,
    "gyroscope": true,
    "magnetometer": true,
    ...
};

// Load all hook functions
[build_hook.js contents]
[qemu_hook.js contents]  
[sensor_hook.js contents]

// Execute hooks in sequence
buildHook(properties);
hookSystemProperties(properties);
qemuHook(properties);
fingerprintHook(properties);
sensorHook(sensors);

console.log("[+] Spoofing complete!");
```

## Testing the Hooks

### Test 1: Build Property Hooking
```bash
python spoofer.py
# Should show loaded profiles and hooks
```

### Test 2: Full Spoofing (when you have a game running)
```python
from spoofer import FridaSpoofer

spoofer = FridaSpoofer()
spoofer.connect_to_bluestacks()
spoofer.select_profile("Samsung Galaxy S22")
spoofer.spoof_game("com.example.mygame")

# Wait while game runs spoofed...
# Then:
spoofer.disconnect()
```

## How Games Detect Emulators

Games use several methods to detect they're on an emulator:

### Method 1: Property Checks
```java
if (Build.FINGERPRINT.contains("unknown") || Build.FINGERPRINT.contains("generic")) {
    return false; // Detected
}
```
**Our defense:** `build_hook.js` changes fingerprint ✓

### Method 2: Hardware Checks  
```java
if (Build.HARDWARE.equals("goldfish") || Build.HARDWARE.equals("ranchu")) {
    return false;
}
```
**Our defense:** `qemu_hook.js` hides these ✓

### Method 3: Sensor Checks
```java
if (getSystemService(SENSOR_SERVICE).getDefaultSensor(Sensor.TYPE_GYROSCOPE) == null) {
    showError("Gyroscope required");
}
```
**Our defense:** `sensor_hook.js` fakes sensors ✓

### Method 4: File System Checks
```java
if (new File("/system/xbin/qemu-props").exists()) {
    return false; // QEMU detected
}
```
**Note:** We don't hook filesystem (out of scope for Part 3)

### Method 5: Process/System Checks
```java
if (System.getProperty("ro.kernel.qemu").equals("1")) {
    return false;
}
```
**Our defense:** `build_hook.js` sets to "0" ✓

## Advanced: Customizing Hooks

You can modify the hook scripts for specific games:

### Example: Add Custom Property Check
Edit `build_hook.js` and add:
```javascript
// Custom property for specific game
try {
    var MyGameClass = Java.use("com.example.game.DeviceChecker");
    MyGameClass.isEmulator.implementation = function() {
        return false; // Always return "not emulator"
    };
    console.log("[+] Custom game hook installed");
} catch (e) {
    console.log("[!] Custom hook not needed for this game");
}
```

### Example: Add Game-Specific Sensor
Edit `sensor_hook.js` to add:
```javascript
// Fake a specific sensor this game checks for
if (sensorName === "com.game.custom_sensor") {
    console.log("[+] Faking game-specific sensor");
    return true;
}
```

## Important Notes

✓ **Works fully client-side** - Only in-game memory affected
✓ **No network changes** - Server sees normal traffic
✓ **Real property values** - All from actual devices
✓ **Layered approach** - Multiple hooks catch different detection methods
✓ **Reversible** - Disconnect returns everything to normal

## Common Issues

**Q: Hook says "Java.perform not called"**
A: The hook didn't load properly. Check browser console for errors.

**Q: Game still detects emulator**
A: Some games use additional checks (filesystem, processes). We only spoof Java properties.

**Q: Sensor hook isn't working**
A: Try uncommenting the "advancedSensorHook" line in the injection code for deeper hooking.

**Q: Build properties changed but game still rejects**
A: Game might be caching properties. We need to hook before game initialization.

## What's Next (Part 4)

Part 4 will create the **hook injector script** that:
- Loads profiles + hooks automatically
- Handles multiple simultaneous games
- Manages hook lifecycle
- Provides status monitoring

---

**Status**: ✓ Part 3 Complete - Hook Scripts Ready

**Next**: Part 4 - Build Hook Injection System
