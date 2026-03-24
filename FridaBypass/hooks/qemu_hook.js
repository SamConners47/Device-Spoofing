/**
 * FridaBypass - QEMU/Emulator Detection Hook
 * Hides emulator detection flags and QEMU-specific properties
 * 
 * Android emulators set various flags that games check to detect emulation:
 * - ro.kernel.qemu = 1 (identifies QEMU emulator)
 * - ro.hardware = goldfish/ranchu (emulator-specific hardware)
 * - Various ro.product.* properties that identify emulators
 */

function qemuHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing QEMU detection hooks...");
            
            // Hook Build.HARDWARE to hide emulator hardware names
            try {
                var Build = Java.use("android.os.Build");
                
                // Hide goldfish (Android emulator)
                var hardwareValue = Build.HARDWARE.value;
                if (hardwareValue && (hardwareValue.includes("goldfish") || hardwareValue.includes("ranchu"))) {
                    Build.HARDWARE.value = properties['Build.HARDWARE'] || "qcom";
                    console.log("[+] Hidden HARDWARE: goldfish/ranchu -> " + Build.HARDWARE.value);
                }
                
                // Hide "unknown" or other emulator indicators
                if (hardwareValue === "unknown") {
                    Build.HARDWARE.value = properties['Build.HARDWARE'] || "qcom";
                    console.log("[+] Hidden HARDWARE: unknown -> " + Build.HARDWARE.value);
                }
            } catch (e) {
                console.log("[!] Could not modify Build.HARDWARE: " + e);
            }
            
            // Hook SystemProperties.get() for ro.kernel.qemu and related properties
            try {
                var SystemProperties = Java.use("android.os.SystemProperties");
                var originalGet = SystemProperties.get;
                
                SystemProperties.get = function(key, defaultValue) {
                    var result = originalGet.call(SystemProperties, key, defaultValue);
                    
                    // Check for QEMU detection properties
                    switch(key) {
                        case "ro.kernel.qemu":
                            // Set to "0" to indicate real device
                            console.log("[+] Spoofed ro.kernel.qemu: 1 -> 0");
                            return "0";
                            
                        case "ro.hardware":
                            // Hide goldfish/ranchu hardware
                            if (result && (result.includes("goldfish") || result.includes("ranchu"))) {
                                var fakeHardware = properties['ro.hardware'] || "qcom";
                                console.log("[+] Spoofed ro.hardware: " + result + " -> " + fakeHardware);
                                return fakeHardware;
                            }
                            break;
                            
                        case "ro.bootloader":
                            // Emulators might have "unknown" bootloader
                            if (result === "unknown") {
                                console.log("[+] Hidden ro.bootloader: unknown");
                                return properties['ro.bootloader'] || result;
                            }
                            break;
                            
                        case "ro.serialno":
                            // Some emulators have "UNKNOWN" serial
                            if (result === "UNKNOWN") {
                                console.log("[+] Hidden ro.serialno: UNKNOWN");
                                return "N" + Math.random().toString(36).substring(2, 15);
                            }
                            break;
                    }
                    
                    return result;
                };
                
                console.log("[+] SystemProperties.get() hooked for QEMU detection!");
                
            } catch (e) {
                console.log("[!] Could not hook SystemProperties: " + e);
            }
            
        } catch (e) {
            console.log("[-] Error in qemuHook: " + e);
        }
    });
}

/**
 * Hook Build fingerprint to ensure it looks real
 * Fingerprints follow format: brand/product/device:android/build/id:user/build-type
 */
function fingerprintHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing fingerprint hooks...");
            
            var Build = Java.use("android.os.Build");
            
            try {
                // Get current fingerprint
                var currentFingerprint = Build.FINGERPRINT.value;
                console.log("[*] Current fingerprint: " + currentFingerprint);
                
                // Replace with real device fingerprint
                if (properties['Build.FINGERPRINT']) {
                    Build.FINGERPRINT.value = properties['Build.FINGERPRINT'];
                    console.log("[+] Set FINGERPRINT to real device value");
                } else if (currentFingerprint && currentFingerprint.includes("x86") || currentFingerprint.includes("unknown")) {
                    // Hide x86 or unknown fingerprints
                    Build.FINGERPRINT.value = "samsung/s22/s22:13/TP1A.220624.014/S901BXXS2AVF1:user/release-keys";
                    console.log("[+] Hidden emulator fingerprint");
                }
                
            } catch (e) {
                console.log("[!] Could not modify fingerprint: " + e);
            }
            
        } catch (e) {
            console.log("[-] Error in fingerprintHook: " + e);
        }
    });
}

/**
 * Hook Build.PRODUCT and Build.DEVICE to hide emulator identifiers
 */
function deviceIdentifierHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing device identifier hooks...");
            
            var Build = Java.use("android.os.Build");
            
            // List of known emulator identifiers
            var emulatorIdentifiers = [
                "generic", "generic_x86", "generic_arm64",
                "emulator", "vbox86", "vbox86p",
                "ranchu", "goldfish", "qemu",
                "unknown"
            ];
            
            // Check DEVICE
            try {
                var deviceValue = Build.DEVICE.value;
                if (deviceValue && emulatorIdentifiers.includes(deviceValue)) {
                    Build.DEVICE.value = properties['Build.DEVICE'] || "s22";
                    console.log("[+] Spoofed DEVICE: " + deviceValue + " -> " + Build.DEVICE.value);
                }
            } catch (e) {
                console.log("[!] Could not modify Build.DEVICE: " + e);
            }
            
            // Check PRODUCT
            try {
                var productValue = Build.PRODUCT.value;
                if (productValue && emulatorIdentifiers.includes(productValue)) {
                    Build.PRODUCT.value = properties['Build.PRODUCT'] || "s22";
                    console.log("[+] Spoofed PRODUCT: " + productValue + " -> " + Build.PRODUCT.value);
                }
            } catch (e) {
                console.log("[!] Could not modify Build.PRODUCT: " + e);
            }
            
        } catch (e) {
            console.log("[-] Error in deviceIdentifierHook: " + e);
        }
    });
}

/**
 * Main exports
 */
var exported = {
    qemuHook: qemuHook,
    fingerprintHook: fingerprintHook,
    deviceIdentifierHook: deviceIdentifierHook
};
