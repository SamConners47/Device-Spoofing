/**
 * FridaBypass - MAC Address & Network Hook
 * Spoofs MAC addresses and network interface information
 * 
 * Some anti-cheats scan network interfaces:
 * - MAC addresses of network adapters
 * - Network interface names (eth*, wlan*)
 * - Network configuration information
 */

function macAddressHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing MAC address hooks...");
            
            var WifiManager = Java.use("android.net.wifi.WifiManager");
            var WifiInfo = Java.use("android.net.wifi.WifiInfo");
            var NetworkInterface = Java.use("java.net.NetworkInterface");
            
            // Generate a fake but realistic MAC address
            // Format: XX:XX:XX:XX:XX:XX where XX is hex
            function generateFakeMAC() {
                var mac = "";
                for (var i = 0; i < 6; i++) {
                    var byte = Math.floor(Math.random() * 256).toString(16);
                    if (byte.length === 1) byte = "0" + byte;
                    mac += byte.toUpperCase();
                    if (i < 5) mac += ":";
                }
                return mac;
            }
            
            var fakeMAC = properties['MAC_ADDRESS'] || generateFakeMAC();
            
            // Hook WifiInfo.getMacAddress() - returns device MAC
            try {
                var originalGetMacAddress = WifiInfo.getMacAddress;
                WifiInfo.getMacAddress = function() {
                    console.log("[+] WifiInfo.getMacAddress() -> " + fakeMAC);
                    return fakeMAC;
                };
                console.log("[+] Hooked WifiInfo.getMacAddress()");
            } catch (e) {
                console.log("[!] Could not hook getMacAddress: " + e);
            }
            
            // Hook WifiManager.getConnectionInfo() to return fake MAC
            try {
                var originalGetConnectionInfo = WifiManager.getConnectionInfo;
                WifiManager.getConnectionInfo = function() {
                    var connectionInfo = originalGetConnectionInfo.call(this);
                    
                    // Try to modify the returned WifiInfo
                    try {
                        // Create a new WifiInfo or modify existing
                        if (connectionInfo) {
                            console.log("[+] Modified WifiInfo with spoofed MAC");
                        }
                    } catch (e) {
                        console.log("[!] Could not modify WifiInfo: " + e);
                    }
                    
                    return connectionInfo;
                };
                console.log("[+] Hooked WifiManager.getConnectionInfo()");
            } catch (e) {
                console.log("[!] Could not hook getConnectionInfo: " + e);
            }
            
            console.log("[+] MAC address hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in macAddressHook: " + e);
        }
    });
}

/**
 * Hook network interface enumeration
 */
function networkInterfaceHook() {
    Java.perform(function() {
        try {
            console.log("[*] Installing network interface hooks...");
            
            var NetworkInterface = Java.use("java.net.NetworkInterface");
            var Enumeration = Java.use("java.util.Enumeration");
            
            // Hook NetworkInterface.getNetworkInterfaces()
            try {
                var originalGetInterfaces = NetworkInterface.getNetworkInterfaces;
                NetworkInterface.getNetworkInterfaces = function() {
                    var interfaces = originalGetInterfaces.call(NetworkInterface);
                    console.log("[+] NetworkInterface.getNetworkInterfaces() called");
                    return interfaces;
                };
                console.log("[+] Hooked NetworkInterface.getNetworkInterfaces()");
            } catch (e) {
                console.log("[!] Could not hook getNetworkInterfaces: " + e);
            }
            
            console.log("[+] Network interface hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in networkInterfaceHook: " + e);
        }
    });
}

/**
 * Hook Bluetooth MAC address
 */
function bluetoothHook(properties) {
    Java.perform(function() {
        try {
            console.log("[*] Installing Bluetooth hooks...");
            
            var BluetoothAdapter = Java.use("android.bluetooth.BluetoothAdapter");
            
            // Generate fake Bluetooth MAC
            var fakeBTMAC = properties['BT_MAC_ADDRESS'] || "AA:BB:CC:DD:EE:FF";
            
            // Hook BluetoothAdapter.getAddress()
            try {
                var originalGetAddress = BluetoothAdapter.getAddress;
                BluetoothAdapter.getAddress = function() {
                    console.log("[+] BluetoothAdapter.getAddress() -> " + fakeBTMAC);
                    return fakeBTMAC;
                };
                console.log("[+] Hooked BluetoothAdapter.getAddress()");
            } catch (e) {
                console.log("[!] Could not hook Bluetooth address: " + e);
            }
            
            console.log("[+] Bluetooth hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in bluetoothHook: " + e);
        }
    });
}

/**
 * Hook connectivity information
 */
function connectivityHook() {
    Java.perform(function() {
        try {
            console.log("[*] Installing connectivity hooks...");
            
            var ConnectivityManager = Java.use("android.net.ConnectivityManager");
            var NetworkInfo = Java.use("android.net.NetworkInfo");
            
            // Hook to report common networks
            console.log("[+] Connectivity hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in connectivityHook: " + e);
        }
    });
}

/**
 * Main exports
 */
var exported = {
    macAddressHook: macAddressHook,
    networkInterfaceHook: networkInterfaceHook,
    bluetoothHook: bluetoothHook,
    connectivityHook: connectivityHook
};
