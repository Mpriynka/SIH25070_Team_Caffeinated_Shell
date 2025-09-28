import os
import time
import subprocess
import stat
from datetime import datetime
from PySide6.QtCore import QThread, Signal

# --- IMPORTANT SECURITY NOTE ---
# This script requires root/administrator privileges to access block devices directly.
# It must be launched with 'sudo python3 main.py'.
# Misuse of these commands can lead to PERMANENT DATA LOSS.

class WipeThread(QThread):
    """
    A QThread to handle the data wiping process using real command-line tools.
    It selects the appropriate tool based on the device type.
    """
    progress = Signal(int)
    finished = Signal(bool, str, dict)  # success (bool), message (str), report_data (dict)

    def __init__(self, device_list, passes=1):
        super().__init__()
        self.device_list = device_list
        self.passes = passes # Used for shred fallback
        self.is_running = True
        self.start_time = None
        self.end_time = None
        self.methods_used = {} # To track the method used for each device

    def run(self):
        """
        Main thread execution logic. Iterates through devices and calls the
        appropriate wiping function based on device type.
        """
        self.start_time = datetime.utcnow()
        total_devices = len(self.device_list)
        devices_wiped_successfully = []
        
        try:
            for i, device in enumerate(self.device_list):
                if not self.is_running:
                    raise Exception("Wipe process was cancelled by the user.")

                device_path = device.get('name')
                if not device_path:
                    raise Exception("Could not find device path in device data.")
                
                # Safety Check: ensure we are dealing with a block device
                try:
                    mode = os.stat(device_path).st_mode
                    if not stat.S_ISBLK(mode):
                        raise Exception(f"Path {device_path} is not a block device. Halting for safety.")
                except FileNotFoundError:
                     raise Exception(f"Device path {device_path} does not exist.")

                # Dispatch to the correct wiping method
                self._wipe_device(device)
                
                # If wipe was successful
                devices_wiped_successfully.append(device_path)
                
                # Update overall progress after each device is done
                progress_val = int(((i + 1) / total_devices) * 100)
                self.progress.emit(progress_val)

            self.end_time = datetime.utcnow()
            report = self._generate_report(True, "Wipe completed successfully.", devices_wiped_successfully)
            self.finished.emit(True, "Success", report)

        except Exception as e:
            self.end_time = datetime.utcnow()
            error_message = f"An error occurred: {e}"
            report = self._generate_report(False, error_message, devices_wiped_successfully)
            self.finished.emit(False, error_message, report)

    def _run_command(self, command):
        """
        Helper to run a command, stream its output for real-time
        logging, and raise a detailed exception on error. This function
        assumes the parent script is already running with sudo.
        """
        print(f"Executing: {' '.join(command)}")
        
        process = subprocess.Popen(
            command, # No longer prepending 'sudo' here
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )

        # Real-time logging from stdout
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Wait for the command to finish and check the return code
        return_code = process.wait()

        if return_code != 0:
            # If there was an error, capture stderr
            stderr_output = process.stderr.read()
            error_message = (
                f"Command '{' '.join(command)}' failed with exit code {return_code}.\n"
                f"Error: {stderr_output.strip()}"
            )
            raise subprocess.CalledProcessError(return_code, command, stderr=error_message)


    def _wipe_device(self, device):
        """
        Selects the correct wiping strategy based on the device name and type.
        Hierarchy: NVMe Sanitize > SATA Secure Erase > Shred Overwrite
        """
        device_path = device['name']
        
        if 'nvme' in device_path:
            # It's an NVMe drive
            try:
                print(f"Attempting NVMe Sanitize on {device_path}...")
                # Using crypto erase (ses=2), which is fast and secure.
                self._run_command(["nvme", "sanitize", device_path, "-a", "2"])
                self.methods_used[device_path] = "NVMe Sanitize (Cryptographic Erase)"
                return
            except Exception as e:
                print(f"NVMe Sanitize failed: {e}. Falling back to NVMe Format.")
                try:
                    # Fallback to a standard format with secure erase settings
                    self._run_command(["nvme", "format", device_path, "-s", "1"])
                    self.methods_used[device_path] = "NVMe Format (User Data Erase)"
                    return
                except Exception as e_fmt:
                    raise Exception(f"NVMe Format also failed on {device_path}: {e_fmt}")

        elif 'sd' in device_path:
            # It's a SATA device (SSD or HDD)
            try:
                # Check if drive is rotational (HDD) or not (SSD)
                rotational_path = f"/sys/block/{os.path.basename(device_path)}/queue/rotational"
                with open(rotational_path, 'r') as f:
                    is_hdd = f.read().strip() == '1'

                # For SSDs, strongly prefer Secure Erase. For HDDs, it's an option but shred is also fine.
                if not is_hdd:
                    print(f"Attempting SATA Secure Erase on SSD {device_path}...")
                    self._wipe_sata_secure_erase(device_path)
                    self.methods_used[device_path] = "ATA Secure Erase"
                    return
            except Exception as e_sec:
                print(f"SATA Secure Erase failed or was skipped: {e_sec}. Falling back to shred.")
            
            # Fallback for HDDs or if Secure Erase fails
            print(f"Using shred (software overwrite) on {device_path}...")
            self._wipe_with_shred(device_path)
            self.methods_used[device_path] = f"{self.passes}-Pass Overwrite (shred)"
            return
            
        raise Exception(f"Unsupported device type for {device_path}")


    def _wipe_sata_secure_erase(self, device_path):
        """
        Performs an ATA Secure Erase on a SATA device.
        NOTE: This is a complex operation. Drives are often in a 'frozen' state
        which prevents this from working without a power cycle. This implementation
        assumes the drive is not frozen.
        """
        password = "p"
        # 1. Check if security is supported and not enabled.
        # This is a simplified check. A full one would parse `hdparm -I` output.
        
        # 2. Set a temporary password.
        self._run_command(["hdparm", "--user-master", "user", "--security-set-pass", password, device_path])

        # 3. Issue the erase command.
        # --security-erase is for standard erase. --security-erase-enhanced is better if supported.
        try:
            self._run_command(["hdparm", "--user-master", "user", "--security-erase", password, device_path])
        except subprocess.TimeoutExpired:
            # Secure erase commands often don't return until done, which can take hours.
            # For the purpose of this app, we assume it has started successfully.
            # A more robust solution would monitor the drive's state.
            print("Secure Erase command sent. Assuming it is in progress.")
        except Exception as e:
            # If it fails, try to disable security so the drive isn't locked.
            self._run_command(["hdparm", "--user-master", "user", "--security-disable", password, device_path])
            raise e

    def _wipe_with_shred(self, device_path):
        """
        Wipes a device using the 'shred' command, forced into line-buffering
        mode with 'stdbuf' to ensure real-time progress output is visible.
        """
        # -n 2: 2 passes of random data
        # -v: verbose, show progress
        # -z: final pass of zeros to hide shredding
        #
        # 'stdbuf -oL' forces the command's standard output to be line-buffered.
        command = ["stdbuf", "-oL", "shred", "-n", "2", "-v", "-z", device_path]
        self._run_command(command)
        
    def _generate_report(self, success, message, wiped_devices):
        """Generates a dictionary with wipe results."""
        return {
            "devices_targeted": [d.get('name') for d in self.device_list],
            "devices_wiped_successfully": wiped_devices,
            "status": "Success" if success else "Failed",
            "message": message,
            "start_time_utc": self.start_time.isoformat() + "Z",
            "end_time_utc": self.end_time.isoformat() + "Z" if self.end_time else "N/A",
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "methods_used": self.methods_used,
        }

    def stop(self):
        """Stops the wiping process if possible."""
        # NOTE: Stopping a low-level format command that is already running is
        # non-trivial and can be dangerous. This provides a basic flag to
        # prevent new wipe operations from starting.
        print("Stop signal received. Will halt after the current device operation.")
        self.is_running = False