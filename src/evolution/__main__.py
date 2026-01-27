#!/usr/bin/env python3
"""
Self-Evolving AI Employee - Main Entry Point
This script initializes and runs the self-evolving AI system
"""

import os
import sys
from pathlib import Path
import logging
import argparse

# Add src to path
SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(SRC_DIR))

def main():
    parser = argparse.ArgumentParser(description="Self-Evolving AI Employee System")
    parser.add_argument("command", nargs="?", default="start", 
                       choices=["start", "status", "force-cycle", "history", "setup"],
                       help="Command to execute")
    parser.add_argument("--daemon", action="store_true", 
                       help="Run as a daemon process")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("SelfEvolvingMain")
    
    if args.command == "setup":
        logger.info("Setting up Self-Evolving AI Employee...")
        setup_system()
    elif args.command == "start":
        logger.info("Starting Self-Evolving AI Employee...")
        start_system(daemon=args.daemon)
    elif args.command == "status":
        logger.info("Getting system status...")
        get_status()
    elif args.command == "force-cycle":
        logger.info("Forcing evolution cycle...")
        force_cycle()
    elif args.command == "history":
        logger.info("Getting evolution history...")
        get_history()
    else:
        parser.print_help()

def setup_system():
    """Setup the self-evolving system"""
    from evolution.config import get_default_config, save_evolution_config
    
    logger = logging.getLogger("SelfEvolvingSetup")
    logger.info("Setting up Self-Evolving AI Employee system...")
    
    # Create necessary directories
    PROJECT_ROOT = Path(__file__).parent.parent
    VAULT_PATH = PROJECT_ROOT / "Vault"
    EVOLUTION_PATH = VAULT_PATH / "Evolution"
    
    EVOLUTION_PATH.mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    config = get_default_config()
    save_evolution_config(config)
    
    logger.info("System setup complete!")

def start_system(daemon=False):
    """Start the self-evolving system"""
    from evolution.orchestrator import SelfEvolvingOrchestrator
    
    logger = logging.getLogger("SelfEvolvingStart")
    
    orchestrator = SelfEvolvingOrchestrator()
    
    if daemon:
        import threading
        daemon_thread = threading.Thread(target=orchestrator.start, daemon=True)
        daemon_thread.start()
        logger.info("Self-Evolving AI Employee started as daemon")
        
        # Keep main thread alive
        try:
            daemon_thread.join()
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            orchestrator.stop_event.set()
    else:
        orchestrator.start()

def get_status():
    """Get current system status"""
    from evolution.orchestrator import SelfEvolvingOrchestrator
    import json
    
    orchestrator = SelfEvolvingOrchestrator()
    status = orchestrator.get_status()
    print(json.dumps(status, indent=2, default=str))

def force_cycle():
    """Force an immediate evolution cycle"""
    from evolution.orchestrator import SelfEvolvingOrchestrator
    
    orchestrator = SelfEvolvingOrchestrator()
    success = orchestrator.force_evolution_cycle()
    print(f"Force cycle {'successful' if success else 'failed'}")

def get_history():
    """Get evolution history"""
    from evolution.orchestrator import SelfEvolvingOrchestrator
    import json
    
    orchestrator = SelfEvolvingOrchestrator()
    history = orchestrator.get_evolution_history()
    print(json.dumps(history, indent=2, default=str))

if __name__ == "__main__":
    main()