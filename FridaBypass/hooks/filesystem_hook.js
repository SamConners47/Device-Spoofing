/**
 * FridaBypass - File System Hook
 * Hides emulator-specific files and directories
 * 
 * Emulators often create files/directories that identify them:
 * - /system/xbin/qemu-props
 * - /system/bin/qemu-props
 * - /system/lib/libqemu.so
 * - /data/local.prop (contains qemu properties)
 */

function fileSystemHook() {
    Java.perform(function() {
        try {
            console.log("[*] Installing file system hooks...");
            
            // Hook java.io.File class
            var File = Java.use("java.io.File");
            
            // List of emulator-identifying files to hide
            var emulatorFiles = [
                "/system/xbin/qemu-props",
                "/system/bin/qemu-props",
                "/system/lib/libqemu.so",
                "/data/local.prop",
                "/system/lib64/libqemu.so",
                "/data/dalvik-cache/",
                "/.emulator_console_auth",
                "/qemu_socket",
                "/fstab.goldfish",
                "/fstab.ranchu"
            ];
            
            // Hook File.exists()
            var originalExists = File.exists;
            File.exists = function() {
                var path = this.getAbsolutePath().toString();
                
                // Check if this is an emulator file
                for (var i = 0; i < emulatorFiles.length; i++) {
                    if (path.includes(emulatorFiles[i])) {
                        console.log("[+] Hidden file check: " + path + " -> false");
                        return false;
                    }
                }
                
                // Otherwise return original result
                return originalExists.call(this);
            };
            
            // Hook File.isFile()
            var originalIsFile = File.isFile;
            File.isFile = function() {
                var path = this.getAbsolutePath().toString();
                
                for (var i = 0; i < emulatorFiles.length; i++) {
                    if (path.includes(emulatorFiles[i])) {
                        return false;
                    }
                }
                
                return originalIsFile.call(this);
            };
            
            // Hook File.canRead()
            var originalCanRead = File.canRead;
            File.canRead = function() {
                var path = this.getAbsolutePath().toString();
                
                for (var i = 0; i < emulatorFiles.length; i++) {
                    if (path.includes(emulatorFiles[i])) {
                        console.log("[+] Hidden file read: " + path + " -> false");
                        return false;
                    }
                }
                
                return originalCanRead.call(this);
            };
            
            console.log("[+] File system hooks installed!");
            
        } catch (e) {
            console.log("[-] Error in fileSystemHook: " + e);
        }
    });
}

/**
 * Hook file reading operations
 */
function fileReadingHook() {
    Java.perform(function() {
        try {
            var FileInputStream = Java.use("java.io.FileInputStream");
            var FileReader = Java.use("java.io.FileReader");
            
            console.log("[*] Hooking file reading...");
            
            // Hook FileInputStream constructor
            var originalFISInit = FileInputStream.$init;
            FileInputStream.$init.overload("java.io.File").implementation = function(file) {
                var path = file.getAbsolutePath().toString();
                
                if (path.includes("qemu") || path.includes("goldfish") || path.includes("ranchu")) {
                    console.log("[!] Attempted read of emulator file: " + path);
                    throw new Error("File not found: " + path);
                }
                
                return originalFISInit.call(this, file);
            };
            
            console.log("[+] File reading hooks installed!");
            
        } catch (e) {
            console.log("[!] Could not hook file reading: " + e);
        }
    });
}

/**
 * Hook Runtime.exec() to hide emulator processes
 */
function processExecutionHook() {
    Java.perform(function() {
        try {
            var Runtime = Java.use("java.lang.Runtime");
            var originalExec = Runtime.exec;
            
            console.log("[*] Hooking process execution...");
            
            // Block dangerous getprop commands
            Runtime.exec = function(command) {
                if (typeof command === 'string') {
                    if (command.includes("getprop ro.kernel.qemu") ||
                        command.includes("getprop ro.hardware") ||
                        command.includes("qemu")) {
                        console.log("[!] Blocked suspicious command: " + command);
                        throw new Error("Command not found");
                    }
                }
                
                return originalExec.call(this, command);
            };
            
            console.log("[+] Process execution hooks installed!");
            
        } catch (e) {
            console.log("[!] Could not hook process execution: " + e);
        }
    });
}

/**
 * Main exports
 */
var exported = {
    fileSystemHook: fileSystemHook,
    fileReadingHook: fileReadingHook,
    processExecutionHook: processExecutionHook
};
