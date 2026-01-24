import unittest
import sys
import os
import time
import threading
import subprocess
import signal
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import service_manager

class TestServiceManager(unittest.TestCase):
    def setUp(self):
        # Create a dummy service config
        self.dummy_script = str(Path(__file__).parent / "dummy_service.py")
        
        # Override SERVICES in service_manager
        service_manager.SERVICES = {
            "dummy_service": {
                "command": [sys.executable, self.dummy_script],
                "cwd": str(Path(__file__).parent),
                "restart_delay": 1,
                "description": "Dummy Service for Testing"
            }
        }
        
        # Reset global state
        service_manager.processes = {}
        service_manager.running = True

    def tearDown(self):
        service_manager.stop_services()
        # Clean up pid file
        if os.path.exists("dummy_service.pid"):
            os.remove("dummy_service.pid")

    def test_startup_and_recovery(self):
        # 1. Start the service manager in a separate thread
        manager_thread = threading.Thread(target=service_manager.monitor_loop)
        manager_thread.daemon = True
        manager_thread.start()

        # Wait for service to start
        print("Waiting for dummy service to start...")
        time.sleep(2)
        
        # Check if running
        self.assertIn("dummy_service", service_manager.processes)
        proc = service_manager.processes["dummy_service"]
        self.assertIsNone(proc.poll())
        initial_pid = proc.pid
        print(f"Service started with PID {initial_pid}")

        # 2. Kill the process to simulate crash
        print("Killing service...")
        proc.kill()
        proc.wait()
        
        # Wait for recovery (restart_delay is 1s, loop sleeps 1s)
        print("Waiting for recovery...")
        time.sleep(3)
        
        # 3. Verify it restarted
        new_proc = service_manager.processes["dummy_service"]
        self.assertIsNone(new_proc.poll())
        self.assertNotEqual(new_proc.pid, initial_pid)
        print(f"Service recovered with new PID {new_proc.pid}")

        # 4. Stop everything
        service_manager.running = False
        time.sleep(1) # Let loop exit

if __name__ == "__main__":
    unittest.main()
