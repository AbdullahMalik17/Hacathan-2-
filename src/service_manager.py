import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path
from datetime import datetime

# Configure Paths
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "Vault" / "Logs"
STARTUP_LOG = LOG_DIR / "startup_log.md"

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ServiceManager")

SERVICES = {
    "gmail_watcher": {
        "command": [sys.executable, "src/watchers/gmail_watcher.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Gmail inbox monitor"
    },
    "filesystem_watcher": {
        "command": [sys.executable, "src/watchers/filesystem_watcher.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Filesystem drop folder monitor"
    },
    "whatsapp_watcher": {
        "command": [sys.executable, "src/watchers/whatsapp_watcher.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 10,
        "description": "WhatsApp Web monitor (requires browser)"
    },
    "orchestrator": {
        "command": [sys.executable, "src/orchestrator.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Task orchestrator with Ralph Wiggum loop"
    }
}

processes = {}
running = True

def log_event(event_type, service_name, status, details=""):
    """Write event to the markdown startup log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"| {timestamp} | {event_type} | {service_name} | {status} | {details} |\n"
    
    try:
        # Ensure log directory exists
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # specific file logic
        if not STARTUP_LOG.exists():
            with open(STARTUP_LOG, "w") as f:
                f.write("# Laptop Startup & Service Log\n\n")
                f.write("| Timestamp | Event | Service | Status | Details |\n")
                f.write("|-----------|-------|---------|--------|---------|\n")
        
        with open(STARTUP_LOG, "a") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Failed to write to startup log: {e}")

def start_service(name):
    """Start a specific service."""
    if name in processes and processes[name].poll() is None:
        return # Already running

    config = SERVICES[name]
    logger.info(f"Starting service: {name}")
    
    try:
        # Start the process
        # We redirect stderr to stdout to capture all output
        # For a production service, we might want to redirect these to separate log files
        p = subprocess.Popen(
            config["command"],
            cwd=config["cwd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True # Python 3.7+
        )
        processes[name] = p
        log_event("STARTUP", name, "SUCCESS", f"PID: {p.pid}")
        logger.info(f"Started {name} with PID {p.pid}")
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        log_event("STARTUP", name, "FAILED", str(e))

def stop_services():
    """Gracefully stop all services."""
    global running
    running = False
    logger.info("Stopping all services...")
    
    for name, p in processes.items():
        if p.poll() is None:
            logger.info(f"Terminating {name} (PID {p.pid})...")
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Service {name} did not stop gracefully, killing...")
                p.kill()
            log_event("SHUTDOWN", name, "SUCCESS", "Graceful stop")

def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    stop_services()
    sys.exit(0)

def monitor_loop():
    """Main loop to monitor and restart services."""
    while running:
        for name in SERVICES:
            if name not in processes:
                start_service(name)
                continue

            p = processes[name]
            ret_code = p.poll()
            
            if ret_code is not None:
                # Process has exited
                logger.warning(f"Service {name} exited with code {ret_code}")
                log_event("CRASH", name, "EXITED", f"Code: {ret_code}")
                
                # Check for output to debug
                # Note: This reads strictly what's in the buffer. 
                # For robust logging, we'd use threads to read streams continuously.
                # stdout_content = p.stdout.read() if p.stdout else ""
                # stderr_content = p.stderr.read() if p.stderr else ""
                # if stderr_content:
                #    logger.error(f"{name} stderr: {stderr_content}")

                # Restart logic
                time.sleep(SERVICES[name]["restart_delay"])
                start_service(name)
        
        time.sleep(1)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Service Manager starting up...")
    log_event("SYSTEM", "ServiceManager", "STARTED", "Manager initialization")
    
    try:
        monitor_loop()
    except KeyboardInterrupt:
        stop_services()
    except Exception as e:
        logger.critical(f"Service Manager crashed: {e}")
        log_event("SYSTEM", "ServiceManager", "CRASHED", str(e))
        stop_services()
