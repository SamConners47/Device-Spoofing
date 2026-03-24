/**
 * FridaBypass - Device ID Hook
 * Spoofs IMEI, Serial Number, Android ID, and other device identifiers
 * 
 * Many anti-cheats and analytics track:
 * - IMEI (phone's unique identifier)
 * - Serial Number
 * - Android ID
 * - Device fingerprint
 * - MAC addresses
 */

function deviceIdHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing device ID hooks...");
            
            var TelephonyManager = Java.use("android.telephony.TelephonyManager");
            var Settings = Java.use("android.provider.Settings");
            var Build = Java.use("android.os.Build");
            
            // Generate realistic IMEI if not in properties
            // Real IMEIs are 15 digits starting with country code
            var fakeIMEI = properties['IMEI'] || "358009071234567"; // Sample valid IMEI
            var fakeSerialNumber = properties['SERIAL'] || "N" + Math.random().toString(36).substring(2, 20).toUpperCase();
            
            // Hook TelephonyManager.getDeviceId() - returns IMEI
            try {
                var originalGetDeviceId = TelephonyManager.getDeviceId;
                TelephonyManager.getDeviceId = function() {
                    console.log("[+] TelephonyManager.getDeviceId() -> " + fakeIMEI);
                    return fakeIMEI;
                };
                console.log("[+] Hooked TelephonyManager.getDeviceId()");
            } catch (e) {
                console.log("[!] Could not hook getDeviceId: " + e);
            }
            
            // Hook TelephonyManager.getImei() (Android 8+)
            try {
                var originalGetImei = TelephonyManager.getImei;
                TelephonyManager.getImei = function(slotIndex) {
                    console.log("[+] TelephonyManager.getImei() -> " + fakeIMEI);
                    return fakeIMEI;
                };
                console.log("[+] Hooked TelephonyManager.getImei()");
            } catch (e) {
                console.log("[!] Could not hook getImei: " + e);
            }
            
            // Hook Build.SERIAL
            try {
                Build.SERIAL.value = fakeSerialNumber;
                console.log("[+] Spoofed Build.SERIAL to " + fakeSerialNumber);
            } catch (e) {
                console.log("[!] Could not spoof Build.SERIAL: " + e);
            }
            
            // Hook Settings.Secure.getString() for ANDROID_ID
            try {
                var fakeAndroidId = properties['ANDROID_ID'] || "a" + Math.random().toString(36).substring(2, 18);
                
                var originalGetStringSecure = Settings.Secure.getString;
                Settings.Secure.getString = function(contentResolver, name) {
                    if (name === "android_id") {
                        console.log("[+] Settings.Secure.getString(ANDROID_ID) -> " + fakeAndroidId);
                        return fakeAndroidId;
                    }
                    return originalGetStringSecure.call(Settings.Secure, contentResolver, name);
                };
                console.log("[+] Hooked Settings.Secure.getString()");
            } catch (e) {
                console.log("[!] Could not hook Settings.Secure.getString: " + e);
            }
            
            console.log("[+] Device ID hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in deviceIdHook: " + e);
        }
    });
}

/**
 * Hook UUID generation for device identifiers
 */
function uuidHook() {
    Java.perform(function() {
        try {
            console.log("[*] Installing UUID hooks...");
            
            var UUID = Java.use("java.util.UUID");
            var fakeUUID = null;
            
            // Hook UUID.randomUUID()
            var originalRandomUUID = UUID.randomUUID;
            UUID.randomUUID = function() {
                // Generate a fake but consistent UUID
                if (!fakeUUID) {
                    fakeUUID = originalRandomUUID.call(UUID);
                }
                return fakeUUID;
            };
            
            console.log("[+] UUID hooks installed!");
            
        } catch (e) {
            console.log("[!] Could not hook UUID: " + e);
        }
    });
}

/**
 * Hook device identification methods
 */
function secureIdHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing secure ID hooks...");
            
            // Some apps use secure random combined with hardware info
            // We try to spoof at multiple levels
            
            var SecureRandom = Java.use("java.security.SecureRandom");
            var originalNextBytes = SecureRandom.nextBytes;
            
            SecureRandom.nextBytes = function(bytes) {
                // This generates predictable but different bytes
                for (var i = 0; i < bytes.length; i++) {
                    bytes[i] = (i * 37 + 73) % 256;
                }
                return bytes;
            };
            
            console.log("[+] Secure ID hooks installed!");
            
        } catch (e) {
            console.log("[!] Could not hook secure IDs: " + e);
        }
    });
}

/**
 * Generate realistic device identifiers based on profile
 */
function generateDeviceIdentifiers(profile) {
    return {
        "IMEI": "358009" + Math.random().toString().substring(2, 16),
        "SERIAL": "N" + Math.random().toString(36).substring(2, 20).toUpperCase(),
        "ANDROID_ID": "a" + Math.random().toString(36).substring(2, 18),
        "model": profile.model,
        "brand": profile.brand
    };
}

/**
 * Main exports
 */
var exported = {
    deviceIdHook: deviceIdHook,
    uuidHook: uuidHook,
    secureIdHook: secureIdHook,
    generateDeviceIdentifiers: generateDeviceIdentifiers
};
