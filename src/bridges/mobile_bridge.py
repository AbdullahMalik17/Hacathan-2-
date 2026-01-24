"""
Mobile Bridge (Android)
Connects to an Android device via ADB to read notifications and control the device.
"""

import subprocess
import time
import re
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class MobileNotification:
    package: str
    title: str
    text: str
    time: float
    id: int

class MobileBridge:
    def __init__(self, device_id: str = None):
        self.device_id = device_id
        self.adb_path = self._find_adb()
        self.connected = False
        self.refresh_connection()

    def _find_adb(self) -> str:
        local_adb = os.path.join(os.getcwd(), "tools", "platform-tools", "adb.exe")
        if os.path.exists(local_adb):
            return local_adb
        
        # Check parent if in src
        parent_adb = os.path.join(os.getcwd(), "..", "tools", "platform-tools", "adb.exe")
        if os.path.exists(parent_adb):
            return parent_adb
            
        return "adb"

    def _run_adb(self, command: List[str]) -> Optional[str]:
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(command)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="ignore")
            return result.stdout.strip()
        except Exception:
            return None

    def refresh_connection(self) -> bool:
        output = self._run_adb(["devices"])
        if not output: 
            self.connected = False
            return False
            
        lines = output.split("\n")[1:]
        # Only count as connected if status is "device" (not "unauthorized" or "offline")
        devices = [line.split("\t")[0] for line in lines if line.strip() and "\tdevice" in line]
        
        if devices:
            if not self.device_id: self.device_id = devices[0]
            self.connected = True
            return True
        
        self.connected = False
        return False

    def get_battery_status(self) -> Dict[str, str]:
        if not self.refresh_connection(): return {"status": "Disconnected", "level": "0"}
        output = self._run_adb(["shell", "dumpsys", "battery"])
        if not output: return {}
        status = {}
        for line in output.split("\n"):
            line = line.strip()
            if "level" in line: status["level"] = line.split(": ")[1]
            elif "status" in line: status["status"] = line.split(": ")[1]
        return status

    def take_screenshot(self, local_path: str = "mobile_screenshot.png") -> bool:
        if not self.refresh_connection(): return False
        remote_path = "/sdcard/screenshot.png"
        self._run_adb(["shell", "screencap", "-p", remote_path])
        self._run_adb(["pull", remote_path, local_path])
        self._run_adb(["shell", "rm", remote_path])
        return True

mobile_bridge = MobileBridge()
