# Configuration for Self-Evolving AI Employee
# Manages settings for autonomous improvement

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field

# Configuration paths
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to main project root
CONFIG_PATH = PROJECT_ROOT / "config"
EVOLUTION_CONFIG_FILE = CONFIG_PATH / "evolution_config.json"

@dataclass
class EvolutionConfig:
    """Configuration for self-evolution capabilities"""
    
    # Core evolution settings
    enabled: bool = True
    max_iterations: int = 10
    cooldown_period: int = 3600  # seconds between evolution cycles
    max_code_changes_per_cycle: int = 5
    
    # Safety settings
    safety_threshold: float = 0.95  # Minimum confidence for changes
    rollback_enabled: bool = True
    backup_retention_days: int = 30
    
    # Performance targets
    performance_improvement_target: float = 0.1  # 10% improvement
    memory_usage_target: float = 0.1  # 10% reduction
    
    # Learning parameters
    learning_rate: float = 0.01
    exploration_rate: float = 0.1  # How often to try experimental changes
    knowledge_retention_rate: float = 0.9
    
    # Files and directories to evolve
    target_files: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.log", "*.tmp", "config/*", "backup/*", "evolution_log*"
    ])
    
    # Evolution strategies
    strategies: List[str] = field(default_factory=lambda: [
        "performance_optimization",
        "memory_efficiency",
        "code_readability",
        "error_handling",
        "modularity"
    ])
    
    # Metrics to track
    metrics_to_track: List[str] = field(default_factory=lambda: [
        "execution_time",
        "memory_usage",
        "lines_of_code",
        "complexity_score",
        "error_rate"
    ])

def load_evolution_config() -> EvolutionConfig:
    """Load evolution configuration from file"""
    if EVOLUTION_CONFIG_FILE.exists():
        with open(EVOLUTION_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Create config object from loaded data
        config = EvolutionConfig()
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    else:
        # Create default configuration
        config = EvolutionConfig()
        save_evolution_config(config)
        return config

def save_evolution_config(config: EvolutionConfig):
    """Save evolution configuration to file"""
    CONFIG_PATH.mkdir(exist_ok=True)
    
    config_dict = {
        'enabled': config.enabled,
        'max_iterations': config.max_iterations,
        'cooldown_period': config.cooldown_period,
        'max_code_changes_per_cycle': config.max_code_changes_per_cycle,
        'safety_threshold': config.safety_threshold,
        'rollback_enabled': config.rollback_enabled,
        'backup_retention_days': config.backup_retention_days,
        'performance_improvement_target': config.performance_improvement_target,
        'memory_usage_target': config.memory_usage_target,
        'learning_rate': config.learning_rate,
        'exploration_rate': config.exploration_rate,
        'knowledge_retention_rate': config.knowledge_retention_rate,
        'target_files': config.target_files,
        'exclude_patterns': config.exclude_patterns,
        'strategies': config.strategies,
        'metrics_to_track': config.metrics_to_track
    }
    
    with open(EVOLUTION_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)

def get_default_config() -> EvolutionConfig:
    """Get default evolution configuration"""
    return EvolutionConfig(
        enabled=True,
        max_iterations=10,
        cooldown_period=3600,
        max_code_changes_per_cycle=5,
        safety_threshold=0.95,
        rollback_enabled=True,
        backup_retention_days=30,
        performance_improvement_target=0.1,
        memory_usage_target=0.1,
        learning_rate=0.01,
        exploration_rate=0.1,
        knowledge_retention_rate=0.9,
        target_files=[
            "src/**/*.py",
            "mobile/**/*.tsx",
            "mobile/**/*.jsx",
            "src/api_server.py",
            "src/orchestrator.py"
        ],
        exclude_patterns=[
            "*.log", "*.tmp", "config/*", "backup/*", "evolution_log*",
            "node_modules/*", "*.git/*", "dist/*", "build/*"
        ],
        strategies=[
            "performance_optimization",
            "memory_efficiency", 
            "code_readability",
            "error_handling",
            "modularity",
            "security_enhancement"
        ],
        metrics_to_track=[
            "execution_time",
            "memory_usage",
            "lines_of_code",
            "complexity_score",
            "error_rate",
            "maintainability_index"
        ]
    )

# Initialize configuration
if not EVOLUTION_CONFIG_FILE.exists():
    default_config = get_default_config()
    save_evolution_config(default_config)

# Global configuration instance
EVOLUTION_CONFIG = load_evolution_config()