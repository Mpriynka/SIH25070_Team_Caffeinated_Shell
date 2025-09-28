import os
import time
from PySide6.QtCore import QThread, Signal
from datetime import datetime

class WipeThread(QThread):
    """
    A QThread to handle the data wiping process without freezing the GUI.
    This is a SIMULATION. It writes to a temporary file instead of a real device.
    """
    progress = Signal(int)
    finished = Signal(bool, str, dict)  # success (bool), message (str), report_data (dict)

    def __init__(self, device_list, block_size=1024*1024, passes=3):
        super().__init__()
        self.device_list = device_list
        self.block_size = block_size
        self.passes = passes
        self.is_running = True
        self.start_time = None
        self.end_time = None

    def run(self):
        """Main thread execution logic for multiple devices."""
        self.start_time = datetime.utcnow()
        total_devices = len(self.device_list)
        devices_wiped_successfully = []
        
        try:
            for i, device in enumerate(self.device_list):
                if not self.is_running:
                    raise Exception("Wipe process was cancelled by user.")
                
                # Use device name for simulation file to avoid conflicts
                simulated_device_path = f"wipe_sim_{device.get('name', 'unknown').replace('/', '_')}.tmp"
                
                # --- SIMULATION SETUP ---
                file_size = 50 * 1024 * 1024  # 50 MB simulation file
                with open(simulated_device_path, "wb") as f:
                    f.truncate(file_size)
                # --- END SIMULATION SETUP ---
                
                total_size = os.path.getsize(simulated_device_path)

                # Perform passes
                for pass_num in range(self.passes):
                    pattern = b'\x00' if pass_num == 0 else (b'\xFF' if pass_num == 1 else os.urandom(1))
                    self._perform_pass(simulated_device_path, total_size, pass_num, i, total_devices, pattern)
                
                devices_wiped_successfully.append(device.get('name'))

                # --- SIMULATION CLEANUP ---
                if os.path.exists(simulated_device_path):
                    os.remove(simulated_device_path)
                # --- END SIMULATION CLEANUP ---

            self.end_time = datetime.utcnow()
            report = self._generate_report(True, "Wipe completed successfully.", devices_wiped_successfully)
            self.finished.emit(True, "Success", report)

        except Exception as e:
            self.end_time = datetime.utcnow()
            error_message = f"An error occurred: {e}"
            report = self._generate_report(False, error_message, devices_wiped_successfully)
            self.finished.emit(False, error_message, report)

    def _perform_pass(self, device_path, total_size, pass_num, device_idx, total_devices, pattern):
        """Simulates a single pass of writing data to a device."""
        written = 0
        with open(device_path, "wb") as f:
            while written < total_size and self.is_running:
                data_block = pattern * self.block_size
                f.write(data_block)
                written += self.block_size
                
                # Calculate overall progress across all devices and passes
                pass_progress = (written / total_size)
                device_progress = (pass_num + pass_progress) / self.passes
                overall_progress = ((device_idx + device_progress) / total_devices) * 100
                
                self.progress.emit(int(overall_progress))
                time.sleep(0.01) # Simulate I/O delay

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
            "method_used": f"{self.passes}-pass overwrite (NIST 800-88 Clear)",
            "passes_completed": self.passes if success else "N/A"
        }

    def stop(self):
        """Stops the wiping process."""
        self.is_running = False
