import subprocess
import json
import platform

class SystemInfo:
    """
    Gathers system and storage device information.
    Focuses on Linux commands suitable for a bootable environment.
    """

    def get_storage_devices(self):
        """
        Retrieves information about storage devices using lsblk.
        Returns a list of dictionaries, one for each device.
        """
        if platform.system() != "Linux":
            # Provide mock data for non-Linux systems (Windows/macOS for development)
            return [
                {'name': '/dev/sda', 'model': 'Mock SSD', 'serial': 'MOCK12345', 'size': '256G', 'type': 'disk'},
                {'name': '/dev/sdb', 'model': 'Mock HDD', 'serial': 'MOCK67890', 'size': '1T', 'type': 'disk'},
            ]

        try:
            # -d: no slaves, -J: JSON output, -o: specify columns
            command = ["lsblk", "-d", "-J", "-o", "NAME,MODEL,SERIAL,SIZE,TYPE"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Filter for disks only and prepend /dev/ if necessary
            devices = []
            for device in data.get("blockdevices", []):
                if device.get("type") == "disk":
                    if not device['name'].startswith('/dev/'):
                        device['name'] = f"/dev/{device['name']}"
                    devices.append(device)
            return devices
            
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error getting storage devices: {e}")
            return []

    def get_system_details(self):
        """
        Retrieves basic system details like manufacturer and model.
        """
        if platform.system() != "Linux":
            return {'vendor': 'Mock Computer Inc.', 'model': 'System 9000'}

        try:
            vendor = self._read_sys_file('/sys/class/dmi/id/sys_vendor').strip()
            model = self._read_sys_file('/sys/class/dmi/id/product_name').strip()
            return {'vendor': vendor, 'model': model}
        except Exception as e:
            print(f"Could not read system details from /sys: {e}")
            return {'vendor': 'N/A', 'model': 'N/A'}
            
    def _read_sys_file(self, path):
        """Helper to read a file from the /sys filesystem."""
        with open(path, 'r') as f:
            return f.read()

    def get_all_info(self):
        """Convenience method to get all information at once."""
        return {
            "system_details": self.get_system_details(),
            "storage_devices": self.get_storage_devices(),
        }

if __name__ == '__main__':
    # For testing the module directly
    info = SystemInfo()
    print("--- System Details ---")
    print(info.get_system_details())
    print("\n--- Storage Devices ---")
    print(info.get_storage_devices())
