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
    "watching-gmail": {
        "command": [sys.executable, ".claude/skills/watching-gmail/scripts/run.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Gmail inbox monitor (Skill)"
    },
    "watching-filesystem": {
        "command": [sys.executable, ".claude/skills/watching-filesystem/scripts/run.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Filesystem drop folder monitor (Skill)"
    },
    "watching-whatsapp": {
        "command": [sys.executable, ".claude/skills/watching-whatsapp/scripts/run.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 10,
        "description": "WhatsApp Web monitor (Skill, requires browser)"
    },
    "digital-fte-orchestrator": {
        "command": [sys.executable, ".claude/skills/digital-fte-orchestrator/scripts/run.py"],
        "cwd": str(BASE_DIR),
        "restart_delay": 5,
        "description": "Task orchestrator with Ralph Wiggum loop (Skill)"
    }
}

processes = {}
running = True

def verify_skill(name):
    """Verify skill is properly configured before starting."""
    config = SERVICES[name]
    skill_path = Path(config["command"][1])

    # Check if skill script exists
    if not skill_path.exists():
        logger.error(f"Skill script not found: {skill_path}")
        return False

    # Check if verify.py exists and run it
    verify_script = skill_path.parent / "verify.py"
    if verify_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(verify_script)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                logger.warning(f"Skill {name} verification failed: {result.stdout}")
                return False
            logger.info(f"Skill {name} verified successfully")
        except Exception as e:
            logger.warning(f"Could not verify skill {name}: {e}")
            # Don't fail on verification error, just warn

    return True

def get_service_status():
    """Get status of all services."""
    status = {}
    for name in SERVICES:
        if name in processes:
            p = processes[name]
            if p.poll() is None:
                status[name] = "running"
            else:
                status[name] = f"exited (code {p.poll()})"
        else:
            status[name] = "not started"
    return status

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

    # Verify skill before starting
    if not verify_skill(name):
        logger.error(f"Skill verification failed for {name}, skipping startup")
        log_event("STARTUP", name, "FAILED", "Skill verification failed")
        return

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
    import argparse

    parser = argparse.ArgumentParser(description="Digital FTE Service Manager")
    parser.add_argument("--status", action="store_true", help="Show status of all services")
    parser.add_argument("--start-all", action="store_true", help="Start all services and monitor")
    parser.add_argument("--start", type=str, help="Start a specific service")
    parser.add_argument("--stop", type=str, help="Stop a specific service")

    args = parser.parse_args()

    # Handle status command
    if args.status:
        logger.info("=== Service Status ===")
        for name, service_status in get_service_status().items():
            config = SERVICES[name]
            logger.info(f"{name}: {service_status} - {config['description']}")
        sys.exit(0)

    # Handle single service start
    if args.start:
        if args.start not in SERVICES:
            logger.error(f"Unknown service: {args.start}")
            logger.info(f"Available services: {', '.join(SERVICES.keys())}")
            sys.exit(1)
        start_service(args.start)
        logger.info(f"Started {args.start}")
        sys.exit(0)

    # Handle single service stop
    if args.stop:
        if args.stop not in processes:
            logger.error(f"Service not running: {args.stop}")
            sys.exit(1)
        p = processes[args.stop]
        if p.poll() is None:
            p.terminate()
            p.wait(timeout=5)
            logger.info(f"Stopped {args.stop}")
        sys.exit(0)

    # Default: Start all services and monitor
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("Digital FTE Service Manager (Skill-Based Architecture)")
    logger.info("=" * 60)
    logger.info(f"Managing {len(SERVICES)} services:")
    for name, config in SERVICES.items():
        logger.info(f"  - {name}: {config['description']}")
    logger.info("=" * 60)

    log_event("SYSTEM", "ServiceManager", "STARTED", "Manager initialization")

    try:
        monitor_loop()
    except KeyboardInterrupt:
        stop_services()
    except Exception as e:
        logger.critical(f"Service Manager crashed: {e}")
        log_event("SYSTEM", "ServiceManager", "CRASHED", str(e))
        stop_services()
