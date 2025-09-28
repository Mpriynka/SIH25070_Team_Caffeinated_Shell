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

    def __init__(self, device_path, block_size=1024*1024, passes=3):
        super().__init__()
        self.device_path = device_path
        self.block_size = block_size  # 1 MB
        self.passes = passes
        self.is_running = True
        self.start_time = None
        self.end_time = None

    def run(self):
        """Main thread execution logic."""
        self.start_time = datetime.utcnow()
        try:
            # --- SIMULATION SETUP ---
            # In a real app, you would open the block device, e.g., os.open(self.device_path, os.O_WRONLY)
            # Here, we create a temporary file to simulate the device.
            file_size = 50 * 1024 * 1024  # 50 MB simulation file
            with open(self.device_path, "wb") as f:
                f.truncate(file_size)
            # --- END SIMULATION SETUP ---
            
            total_size = os.path.getsize(self.device_path)
            
            # NIST SP 800-88r1 "Clear" pass (Overwrite with zeros)
            self._perform_pass(0, total_size, b'\x00')
            if not self.is_running: return

            # Second pass (Overwrite with ones)
            self._perform_pass(1, total_size, b'\xFF')
            if not self.is_running: return

            # Third pass (Overwrite with random data)
            self._perform_pass(2, total_size, os.urandom(1)) # In reality, generate random data per block
            if not self.is_running: return
            
            # Final verification pass can be added here
            
            self.end_time = datetime.utcnow()
            report = self._generate_report(True, "Wipe completed successfully.")
            self.finished.emit(True, "Success", report)
        
        except Exception as e:
            self.end_time = datetime.utcnow()
            error_message = f"An error occurred: {e}"
            report = self._generate_report(False, error_message)
            self.finished.emit(False, error_message, report)
        
        finally:
            # --- SIMULATION CLEANUP ---
            if os.path.exists(self.device_path):
                os.remove(self.device_path)
            # --- END SIMULATION CLEANUP ---

    def _perform_pass(self, pass_num, total_size, pattern):
        """Simulates a single pass of writing data to the device."""
        written = 0
        with open(self.device_path, "wb") as f:
            while written < total_size and self.is_running:
                data_block = pattern * self.block_size
                f.write(data_block)
                written += self.block_size
                
                # Calculate overall progress across all passes
                pass_progress = (written / total_size) * 100
                overall_progress = ((pass_num * 100) + pass_progress) / self.passes
                self.progress.emit(int(overall_progress))
                time.sleep(0.01) # Simulate I/O delay

    def _generate_report(self, success, message):
        """Generates a dictionary with wipe results."""
        return {
            "device_path": self.device_path,
            "status": "Success" if success else "Failed",
            "message": message,
            "start_time_utc": self.start_time.isoformat() + "Z",
            "end_time_utc": self.end_time.isoformat() + "Z" if self.end_time else "N/A",
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "method_used": "3-pass overwrite (NIST 800-88 Clear)",
            "passes_completed": self.passes if success else "N/A"
        }

    def stop(self):
        """Stops the wiping process."""
        self.is_running = False
