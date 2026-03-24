/**
 * FridaBypass - Sensor Hook
 * Fakes sensor availability to match the spoofed device profile
 * 
 * Most emulators don't have a gyroscope, so we fake sensor availability
 * This makes games think we have a "real" device with proper sensors
 */

function sensorHook(sensorConfig) {
    Java.perform(function() {
        try {
            // Get SensorManager and Sensor classes
            var SensorManager = Java.use("android.hardware.SensorManager");
            var Sensor = Java.use("android.hardware.Sensor");
            
            console.log("[*] Hooking sensor availability...");
            
            // Map sensor types to their type numbers
            var sensorTypes = {
                'accelerometer': 1,      // TYPE_ACCELEROMETER
                'magnetometer': 2,       // TYPE_MAGNETIC_FIELD
                'orientation': 3,        // TYPE_ORIENTATION (deprecated)
                'gyroscope': 4,          // TYPE_GYROSCOPE
                'light': 5,              // TYPE_LIGHT
                'pressure': 6,           // TYPE_PRESSURE
                'temperature': 7,        // TYPE_TEMPERATURE
                'proximity': 8,          // TYPE_PROXIMITY
                'gravity': 9,            // TYPE_GRAVITY
                'linear_acceleration': 10, // TYPE_LINEAR_ACCELERATION
                'rotation_vector': 11    // TYPE_ROTATION_VECTOR
            };
            
            // Create fake sensor objects
            var fakeSensors = {};
            
            for (var sensorName in sensorConfig) {
                if (sensorConfig[sensorName] === true) {
                    var sensorType = sensorTypes[sensorName];
                    
                    if (sensorType !== undefined) {
                        try {
                            // Create a fake sensor object
                            // We'll store these to return when asked
                            fakeSensors[sensorType] = {
                                name: sensorName,
                                type: sensorType
                            };
                            
                            console.log("[+] Faking sensor: " + sensorName + " (type " + sensorType + ")");
                        } catch (e) {
                            console.log("[-] Error setting up " + sensorName + ": " + e);
                        }
                    }
                }
            }
            
            // Hook SensorManager methods to return our fake sensors
            try {
                var originalGetDefaultSensor = null;
                var originalGetSensorList = null;
                
                // Try to hook getDefaultSensor
                SensorManager.getDefaultSensor = function(type, wakeUp) {
                    // Check if we're faking this sensor
                    if (fakeSensors[type] !== undefined) {
                        console.log("[+] SensorManager.getDefaultSensor(" + type + ") -> FAKED");
                        
                        // Return a fake sensor object
                        // Note: This is a simplified approach
                        // Some games may check sensor properties more deeply
                        return Java.use("android.hardware.Sensor");
                    }
                    
                    // If we're not faking it, return original or null
                    return null;
                };
                
                console.log("[+] Sensor availability hooks installed!");
                
            } catch (e) {
                console.log("[!] Could not fully hook SensorManager: " + e);
            }
            
        } catch (e) {
            console.log("[-] Error in sensorHook: " + e);
        }
    });
}

/**
 * Advanced sensor hook - intercepts actual sensor list requests
 * This is more reliable than trying to return fake sensor objects
 */
function advancedSensorHook(sensorConfig) {
    Java.perform(function() {
        try {
            var SensorEventListener = Java.use("android.hardware.SensorEventListener");
            var SensorManager = Java.use("android.hardware.SensorManager");
            
            console.log("[*] Installing advanced sensor hooks...");
            
            // Monitor registerListener calls to see which sensors games request
            var originalRegisterListener = null;
            
            try {
                // Hook SensorManager.registerListener to trace sensor requests
                var SensorManagerClass = Java.use("android.hardware.SensorManager");
                
                // Create a method override for registerListener
                SensorManager.registerListener.overload(
                    "android.hardware.SensorEventListener",
                    "android.hardware.Sensor",
                    "int"
                ).implementation = function(listener, sensor, delay) {
                    
                    try {
                        var sensorName = sensor.getName().toString();
                        var sensorType = sensor.getType();
                        
                        console.log("[*] Game requested sensor: " + sensorName + " (type " + sensorType + ")");
                        
                        // Check if we should provide this sensor
                        // If sensor not in our config, don't register it
                        // This effectively hides sensors we don't have
                        var shouldRegister = false;
                        
                        if (sensorConfig['accelerometer'] && sensorType == 1) shouldRegister = true;
                        if (sensorConfig['magnetometer'] && sensorType == 2) shouldRegister = true;
                        if (sensorConfig['gyroscope'] && sensorType == 4) shouldRegister = true;
                        if (sensorConfig['light'] && sensorType == 5) shouldRegister = true;
                        if (sensorConfig['pressure'] && sensorType == 6) shouldRegister = true;
                        if (sensorConfig['proximity'] && sensorType == 8) shouldRegister = true;
                        if (sensorConfig['gravity'] && sensorType == 9) shouldRegister = true;
                        if (sensorConfig['linear_acceleration'] && sensorType == 10) shouldRegister = true;
                        
                        if (shouldRegister) {
                            console.log("[+] Allowing sensor registration");
                            return this.registerListener(listener, sensor, delay);
                        } else {
                            console.log("[-] Blocking sensor registration (not in profile)");
                            return false;
                        }
                    } catch (e) {
                        console.log("[!] Error in registerListener hook: " + e);
                        // Fall through to original
                        return this.registerListener(listener, sensor, delay);
                    }
                };
                
                console.log("[+] Advanced sensor hooks installed!");
                
            } catch (e) {
                console.log("[!] Could not install advanced sensor hooks: " + e);
            }
            
        } catch (e) {
            console.log("[-] Error in advancedSensorHook: " + e);
        }
    });
}

/**
 * Main exports
 */
var exported = {
    sensorHook: sensorHook,
    advancedSensorHook: advancedSensorHook
};
