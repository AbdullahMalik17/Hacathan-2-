# Self-Evolving AI Employee Orchestrator
# Main controller for autonomous evolution

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
import threading
import signal
import json

# Import components
sys.path.append(str(Path(__file__).parent))
from self_evolution_engine import SelfEvolvingAgent, EvolutionStage
from config import EVOLUTION_CONFIG, load_evolution_config
from knowledge_system import KnowledgeDatabase, LearningModule

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to main project root
VAULT_PATH = PROJECT_ROOT / "Vault"
EVOLUTION_PATH = VAULT_PATH / "Evolution"
EVOLUTION_PATH.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SelfEvolvingOrchestrator")

@dataclass
class EvolutionCycle:
    """Represents a complete evolution cycle"""
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    target_files: List[str] = None
    results: Dict[str, Any] = None
    metrics_before: Dict[str, Any] = None
    metrics_after: Dict[str, Any] = None

class SelfEvolvingOrchestrator:
    """Main orchestrator for the self-evolving AI system"""
    
    def __init__(self):
        self.agent = SelfEvolvingAgent()
        self.knowledge_db = KnowledgeDatabase()
        self.learning_module = LearningModule(self.knowledge_db)
        self.config = load_evolution_config()
        
        # State management
        self.current_cycle: Optional[EvolutionCycle] = None
        self.cycle_history: List[EvolutionCycle] = []
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Metrics tracking
        self.global_metrics = {
            "total_cycles": 0,
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "total_improvements": 0,
            "average_success_rate": 0.0
        }
    
    def start(self):
        """Start the self-evolving system"""
        logger.info("Starting Self-Evolving AI Employee...")
        self.is_running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.is_running and not self.stop_event.is_set():
                self.run_evolution_cycle()
                
                # Wait for cooldown period
                logger.info(f"Waiting {self.config.cooldown_period} seconds until next cycle...")
                for _ in range(self.config.cooldown_period):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Interrupt received, shutting down...")
        finally:
            self.shutdown()
    
    def run_evolution_cycle(self):
        """Execute a complete evolution cycle"""
        if not self.config.enabled:
            logger.info("Evolution is disabled in configuration")
            return
        
        logger.info("Starting evolution cycle...")
        
        # Create cycle record
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_cycle = EvolutionCycle(
            id=cycle_id,
            start_time=datetime.now()
        )
        
        try:
            # Step 1: Gather targets for evolution
            target_files = self._identify_targets()
            self.current_cycle.target_files = target_files
            
            if not target_files:
                logger.info("No targets identified for evolution")
                self._finalize_cycle(success=False, reason="No targets")
                return
            
            logger.info(f"Identified {len(target_files)} targets for evolution")
            
            # Step 2: Collect metrics before evolution
            metrics_before = self._collect_metrics(target_files)
            self.current_cycle.metrics_before = metrics_before
            
            # Step 3: Perform evolution
            results = self.agent.run_evolution_cycle(target_files)
            
            # Step 4: Collect metrics after evolution
            metrics_after = self._collect_metrics(target_files)
            self.current_cycle.metrics_after = metrics_after
            
            # Step 5: Learn from the cycle
            self._learn_from_cycle(results, metrics_before, metrics_after)
            
            # Step 6: Update global metrics
            self._update_global_metrics(results)
            
            # Step 7: Finalize cycle
            self._finalize_cycle(success=results["success_rate"] > 0.5, results=results)
            
            logger.info(f"Evolution cycle completed. Success rate: {results['success_rate']:.2%}")
            
        except Exception as e:
            logger.error(f"Error in evolution cycle: {e}")
            self._finalize_cycle(success=False, reason=str(e))
    
    def _identify_targets(self) -> List[str]:
        """Identify files/directories to evolve"""
        targets = []
        
        # Add configured target files
        for pattern in self.config.target_files:
            path = PROJECT_ROOT / pattern
            if path.exists():
                if path.is_file():
                    targets.append(str(path))
                else:
                    # Add all files in directory matching pattern
                    for file_path in path.rglob("*.py"):
                        if not self._should_exclude(file_path):
                            targets.append(str(file_path))
        
        # Filter out excluded patterns
        filtered_targets = [t for t in targets if not self._should_exclude(Path(t))]
        
        # Limit to max changes per cycle
        return filtered_targets[:self.config.max_code_changes_per_cycle]
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from evolution"""
        path_str = str(path)
        
        for pattern in self.config.exclude_patterns:
            if pattern.startswith("*"):
                # Simple wildcard match
                if pattern[1:] in path_str:
                    return True
            elif "*" in pattern:
                # More complex pattern matching
                import fnmatch
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            elif pattern in path_str:
                return True
        
        return False
    
    def _collect_metrics(self, target_files: List[str]) -> Dict[str, Any]:
        """Collect metrics before/after evolution"""
        metrics = {
            "file_count": len(target_files),
            "total_lines": 0,
            "total_size_bytes": 0,
            "start_time": datetime.now().isoformat()
        }
        
        for file_path in target_files:
            try:
                path = Path(file_path)
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    metrics["total_lines"] += len(content.splitlines())
                    metrics["total_size_bytes"] += len(content.encode('utf-8'))
            except Exception as e:
                logger.warning(f"Could not collect metrics for {file_path}: {e}")
        
        return metrics
    
    def _learn_from_cycle(self, results: Dict[str, Any], before_metrics: Dict[str, Any], after_metrics: Dict[str, Any]):
        """Learn from the evolution cycle results"""
        try:
            experience_data = {
                "task": "evolution_cycle",
                "method": "self_evolution",
                "result": "completed",
                "outcome": "success" if results["success_rate"] > 0.5 else "partial_success",
                "metrics": {
                    "success_rate": results["success_rate"],
                    "files_processed": results["total_files"],
                    "successful_evolutions": results["successful_evolutions"],
                    "failed_evolutions": results["failed_evolutions"],
                    "before_lines": before_metrics.get("total_lines", 0),
                    "after_lines": after_metrics.get("total_lines", 0),
                    "before_size": before_metrics.get("total_size_bytes", 0),
                    "after_size": after_metrics.get("total_size_bytes", 0)
                }
            }
            
            # Learn from the experience
            self.learning_module.learn_from_experience(experience_data)
            
            # If improvements were made, acquire new skills
            if results["successful_evolutions"] > 0:
                improvement_rate = results["successful_evolutions"] / results["total_files"]
                if improvement_rate > 0.3:  # If 30%+ files improved
                    self.learning_module.acquire_new_skill("code_optimization")
                    self.learning_module.acquire_new_skill("performance_tuning")
        
        except Exception as e:
            logger.error(f"Error learning from cycle: {e}")
    
    def _update_global_metrics(self, results: Dict[str, Any]):
        """Update global evolution metrics"""
        self.global_metrics["total_cycles"] += 1
        self.global_metrics["successful_evolutions"] += results["successful_evolutions"]
        self.global_metrics["failed_evolutions"] += results["failed_evolutions"]
        self.global_metrics["total_improvements"] += results["successful_evolutions"]
        
        # Update average success rate
        if self.global_metrics["total_cycles"] > 0:
            total_evolutions = self.global_metrics["successful_evolutions"] + self.global_metrics["failed_evolutions"]
            if total_evolutions > 0:
                self.global_metrics["average_success_rate"] = (
                    self.global_metrics["successful_evolutions"] / total_evolutions
                )
    
    def _finalize_cycle(self, success: bool, results: Dict[str, Any] = None, reason: str = ""):
        """Finalize the current evolution cycle"""
        if self.current_cycle:
            self.current_cycle.end_time = datetime.now()
            self.current_cycle.status = "success" if success else "failed"
            self.current_cycle.results = results or {"reason": reason}
            
            # Add to history
            self.cycle_history.append(self.current_cycle)
            
            # Keep only recent history (last 100 cycles)
            if len(self.cycle_history) > 100:
                self.cycle_history = self.cycle_history[-100:]
            
            self.current_cycle = None
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.stop_event.set()
    
    def shutdown(self):
        """Gracefully shut down the system"""
        logger.info("Shutting down Self-Evolving AI Employee...")
        self.is_running = False
        
        # Save current state
        self._save_state()
        
        logger.info("Self-Evolving AI Employee shutdown complete")
    
    def _save_state(self):
        """Save current state to persistent storage"""
        state_file = EVOLUTION_PATH / "current_state.json"
        
        state = {
            "global_metrics": self.global_metrics,
            "last_cycle_time": self.current_cycle.start_time.isoformat() if self.current_cycle else None,
            "cycle_history_count": len(self.cycle_history),
            "is_running": self.is_running
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the evolution system"""
        return {
            "is_running": self.is_running,
            "current_cycle": self.current_cycle.id if self.current_cycle else None,
            "global_metrics": self.global_metrics,
            "config": {
                "enabled": self.config.enabled,
                "cooldown_period": self.config.cooldown_period,
                "max_iterations": self.config.max_iterations
            },
            "cycle_history_count": len(self.cycle_history)
        }
    
    def force_evolution_cycle(self):
        """Force an immediate evolution cycle"""
        if not self.is_running:
            logger.warning("System not running, cannot force cycle")
            return False
        
        logger.info("Forcing immediate evolution cycle...")
        self.run_evolution_cycle()
        return True
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get history of evolution cycles"""
        history = []
        for cycle in self.cycle_history[-20:]:  # Last 20 cycles
            history.append({
                "id": cycle.id,
                "start_time": cycle.start_time.isoformat(),
                "end_time": cycle.end_time.isoformat() if cycle.end_time else None,
                "status": cycle.status,
                "targets_count": len(cycle.target_files) if cycle.target_files else 0,
                "results": cycle.results
            })
        return history

# Command-line interface
def main():
    """Main entry point for the self-evolving orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Evolving AI Employee Orchestrator")
    parser.add_argument("--start", action="store_true", help="Start the evolution system")
    parser.add_argument("--status", action="store_true", help="Get current status")
    parser.add_argument("--force-cycle", action="store_true", help="Force an immediate evolution cycle")
    parser.add_argument("--history", action="store_true", help="Show evolution history")
    
    args = parser.parse_args()
    
    orchestrator = SelfEvolvingOrchestrator()
    
    if args.start:
        logger.info("Starting Self-Evolving AI Employee...")
        orchestrator.start()
    elif args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.force_cycle:
        success = orchestrator.force_evolution_cycle()
        print(f"Force cycle {'successful' if success else 'failed'}")
    elif args.history:
        history = orchestrator.get_evolution_history()
        print(json.dumps(history, indent=2, default=str))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()