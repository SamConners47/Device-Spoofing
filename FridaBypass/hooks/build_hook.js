/**
 * FridaBypass - Build Properties Hook
 * Spoofs Android Build.* properties to fake a real device
 * 
 * This script hooks into the Android Build class and replaces
 * device properties like MODEL, BRAND, HARDWARE with real device values
 */

function buildHook(properties) {
    Java.perform(function() {
        try {
            // Get the Build class
            var Build = Java.use("android.os.Build");
            
            console.log("[*] Hooking Build properties...");
            
            // Dictionary of property names and their Java property names
            var propertyMap = {
                'Build.MODEL': 'MODEL',
                'Build.BRAND': 'BRAND',
                'Build.MANUFACTURER': 'MANUFACTURER',
                'Build.HARDWARE': 'HARDWARE',
                'Build.DEVICE': 'DEVICE',
                'Build.PRODUCT': 'PRODUCT',
                'Build.BOARD': 'BOARD',
                'Build.FINGERPRINT': 'FINGERPRINT',
                'Build.TYPE': 'TYPE',
                'Build.DISPLAY': 'DISPLAY',
                'Build.ID': 'ID',
                'Build.VERSION': 'VERSION'
            };
            
            // Hook each Build property
            for (var fullProp in propertyMap) {
                var javaProperty = propertyMap[fullProp];
                
                // Check if this property is in our properties map
                if (properties[fullProp]) {
                    var fakeValue = properties[fullProp];
                    
                    try {
                        // Try to hook the property
                        if (Build[javaProperty] && Build[javaProperty].value !== undefined) {
                            var realValue = Build[javaProperty].value;
                            Build[javaProperty].value = fakeValue;
                            console.log("[+] Build." + javaProperty + ": " + realValue + " -> " + fakeValue);
                        }
                    } catch (e) {
                        console.log("[-] Could not hook Build." + javaProperty + ": " + e);
                    }
                }
            }
            
            // Also hook Build.VERSION.BASE_OS if available
            try {
                var VERSION = Java.use("android.os.Build$VERSION");
                if (VERSION && properties['ro.build.version.release']) {
                    Version.RELEASE.value = properties['ro.build.version.release'];
                    console.log("[+] Build.VERSION.RELEASE: " + properties['ro.build.version.release']);
                }
            } catch (e) {
                // Silently ignore if VERSION not available
            }
            
            console.log("[+] Build properties hooked successfully!");
            
        } catch (e) {
            console.log("[-] Error in buildHook: " + e);
        }
    });
}

/**
 * Hook system properties using SystemProperties class
 * Some games check ro.* properties directly
 */
function hookSystemProperties(properties) {
    Java.perform(function() {
        try {
            // Try to get SystemProperties class
            var SystemProperties = Java.use("android.os.SystemProperties");
            
            console.log("[*] Hooking system properties...");
            
            // List of system properties to spoof
            var systemProps = [
                'ro.kernel.qemu',
                'ro.product.cpu.abi',
                'ro.product.cpu.abilist',
                'ro.build.display.id',
                'ro.build.id',
                'ro.build.version.release',
                'ro.build.version.sdk',
                'ro.hardware',
                'ro.biometric.face',
                'ro.biometric.fingerprint'
            ];
            
            // Hook SystemProperties.get() to return our fake values
            var originalGet = SystemProperties.get;
            SystemProperties.get = function(key, defaultValue) {
                // Check if this is a property we want to spoof
                if (properties[key]) {
                    var fakeValue = properties[key];
                    console.log("[+] SystemProperties.get('" + key + "'): -> " + fakeValue);
                    return fakeValue;
                }
                
                // Otherwise return original value
                return originalGet.call(SystemProperties, key, defaultValue);
            };
            
            console.log("[+] System properties hooked!");
            
        } catch (e) {
            console.log("[!] SystemProperties not available: " + e);
        }
    });
}

/**
 * Main hook function - exported
 */
var exported = {
    buildHook: buildHook,
    hookSystemProperties: hookSystemProperties
};
