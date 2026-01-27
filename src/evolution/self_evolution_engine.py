# Self-Evolving AI Employee System
# Core architecture for autonomous self-improvement

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import inspect
import ast
import hashlib
import pickle
import copy

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
logger = logging.getLogger("SelfEvolvingAI")

class EvolutionStage(Enum):
    ANALYSIS = "analysis"
    IDENTIFICATION = "identification"
    GENERATION = "generation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    EVALUATION = "evaluation"

@dataclass
class EvolutionRecord:
    """Record of an evolution attempt"""
    id: str
    timestamp: datetime
    stage: EvolutionStage
    original_code: str
    modified_code: str
    test_results: Dict[str, Any]
    success: bool
    reason: str
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]

class CodeAnalyzer:
    """Analyzes code to identify improvement opportunities"""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze_performance(self, code: str, context: str = "") -> Dict[str, Any]:
        """Analyze code for performance metrics"""
        try:
            # Parse the code to AST
            tree = ast.parse(code)
            
            # Analyze various metrics
            metrics = {
                "lines_of_code": len(code.splitlines()),
                "cyclomatic_complexity": self._calculate_complexity(tree),
                "function_count": self._count_functions(tree),
                "variable_count": self._count_variables(tree),
                "nested_depth": self._calculate_depth(tree),
                "duplicate_code_ratio": self._calculate_duplication(code),
                "efficiency_score": self._calculate_efficiency(code)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"error": str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += 1  # Each boolean operation adds to complexity
        
        return complexity
    
    def _count_functions(self, tree: ast.AST) -> int:
        """Count functions in code"""
        return len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
    
    def _count_variables(self, tree: ast.AST) -> int:
        """Count variables in code"""
        return len([node for node in ast.walk(tree) if isinstance(node, ast.Name)])
    
    def _calculate_depth(self, tree: ast.AST) -> int:
        """Calculate nesting depth"""
        max_depth = 0
        
        def traverse(node, current_depth):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                traverse(child, current_depth + 1)
        
        traverse(tree, 0)
        return max_depth
    
    def _calculate_duplication(self, code: str) -> float:
        """Calculate approximate duplicate code ratio"""
        lines = code.splitlines()
        line_counts = {}
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                line_counts[line] = line_counts.get(line, 0) + 1
        
        duplicates = sum(count - 1 for count in line_counts.values() if count > 1)
        total_lines = len([l for l in lines if l.strip() and not l.startswith('#')])
        
        return duplicates / total_lines if total_lines > 0 else 0.0
    
    def _calculate_efficiency(self, code: str) -> float:
        """Calculate efficiency score based on various factors"""
        # This is a simplified efficiency calculation
        # In a real system, this would be much more sophisticated
        lines = len(code.splitlines())
        functions = len([l for l in code.splitlines() if l.strip().startswith('def ')])
        
        # Efficiency = (functions / lines) * 100, normalized
        if lines > 0:
            efficiency = (functions / lines) * 100
            # Higher efficiency is better, but capped
            return min(efficiency, 100.0)
        return 0.0

class ImprovementEngine:
    """Generates code improvements based on analysis"""
    
    def __init__(self):
        self.improvement_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Callable]:
        """Load improvement patterns"""
        return {
            "optimize_loops": self._optimize_loops,
            "reduce_complexity": self._reduce_complexity,
            "improve_readability": self._improve_readability,
            "add_error_handling": self._add_error_handling,
            "memory_optimization": self._memory_optimization,
        }
    
    def generate_improvements(self, original_code: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate potential improvements based on analysis"""
        improvements = []
        
        # Apply different improvement patterns based on analysis
        if analysis.get("cyclomatic_complexity", 0) > 10:
            improvements.append(self._reduce_complexity(original_code))
        
        if analysis.get("duplicate_code_ratio", 0) > 0.1:  # 10% duplication
            improvements.append(self._optimize_loops(original_code))
        
        if analysis.get("lines_of_code", 0) > 100:
            improvements.append(self._improve_readability(original_code))
        
        # Add error handling if not present
        if "try:" not in original_code and "except" not in original_code:
            improvements.append(self._add_error_handling(original_code))
        
        # Memory optimization for large codebases
        if analysis.get("lines_of_code", 0) > 50:
            improvements.append(self._memory_optimization(original_code))
        
        return improvements
    
    def _optimize_loops(self, code: str) -> str:
        """Optimize loops and repetitive code"""
        # This is a simplified example
        # In a real system, this would use more sophisticated AST transformations
        optimized = code.replace("for i in range(len(", "for i, item in enumerate(")
        return optimized
    
    def _reduce_complexity(self, code: str) -> str:
        """Reduce code complexity"""
        # Simplified complexity reduction
        lines = code.splitlines()
        optimized_lines = []
        
        for line in lines:
            # Remove unnecessary nested conditions
            if "if" in line and "else" in line and ":" in line:
                # This is a simplified example
                optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return "\n".join(optimized_lines)
    
    def _improve_readability(self, code: str) -> str:
        """Improve code readability"""
        # Add comments, improve variable names, etc.
        improved = code  # Placeholder for actual readability improvements
        
        # In a real system, this would add meaningful comments and improve structure
        return improved
    
    def _add_error_handling(self, code: str) -> str:
        """Add error handling to code"""
        # This is a simplified example
        # In a real system, this would intelligently add try-except blocks
        lines = code.splitlines()
        improved_lines = []
        
        for line in lines:
            improved_lines.append(line)
            if "return" in line and not any(x in line for x in ["try:", "except", "finally"]):
                # Add error handling after return statements
                improved_lines.append("    except Exception as e:")
                improved_lines.append("        logger.error(f'Error in function: {e}')")
                improved_lines.append("        raise")
        
        return "\n".join(improved_lines)
    
    def _memory_optimization(self, code: str) -> str:
        """Optimize memory usage"""
        # Replace list comprehensions with generators where appropriate
        optimized = code.replace("[x for x in", "(x for x in")
        return optimized

class TestingFramework:
    """Framework for testing code improvements"""
    
    def __init__(self):
        self.test_results = {}
    
    def validate_improvement(self, original_code: str, improved_code: str) -> Dict[str, Any]:
        """Validate that an improvement maintains functionality"""
        try:
            # Create a temporary module for testing
            import tempfile
            import importlib.util
            
            # Test original functionality
            original_result = self._test_functionality(original_code)
            
            # Test improved functionality
            improved_result = self._test_functionality(improved_code)
            
            # Compare results
            functionality_preserved = self._compare_results(original_result, improved_result)
            
            # Test performance
            original_perf = self._benchmark_code(original_code)
            improved_perf = self._benchmark_code(improved_code)
            
            # Test memory usage
            original_memory = self._measure_memory(original_code)
            improved_memory = self._measure_memory(improved_code)
            
            return {
                "functionality_preserved": functionality_preserved,
                "performance_improved": improved_perf < original_perf,
                "memory_improved": improved_memory < original_memory,
                "original_performance": original_perf,
                "improved_performance": improved_perf,
                "original_memory": original_memory,
                "improved_memory": improved_memory,
                "success": functionality_preserved and (improved_perf < original_perf or improved_memory < original_memory)
            }
            
        except Exception as e:
            logger.error(f"Error validating improvement: {e}")
            return {
                "functionality_preserved": False,
                "success": False,
                "error": str(e)
            }
    
    def _test_functionality(self, code: str) -> Any:
        """Test the functionality of the code"""
        # This is a simplified test - in reality, you'd need proper unit tests
        try:
            # Execute the code in a safe environment
            local_vars = {}
            exec(code, {}, local_vars)
            return local_vars
        except Exception as e:
            return {"error": str(e)}
    
    def _compare_results(self, result1: Any, result2: Any) -> bool:
        """Compare results to ensure functionality is preserved"""
        # Simplified comparison
        return str(result1) == str(result2)
    
    def _benchmark_code(self, code: str) -> float:
        """Benchmark code execution time"""
        import timeit
        
        # This is a simplified benchmark
        # In reality, you'd need to extract and test specific functions
        timer_code = f"""
import time
start_time = time.time()
{code}
end_time = time.time()
end_time - start_time
"""
        try:
            elapsed = timeit.timeit(timer_code, number=1)
            return elapsed
        except:
            return float('inf')  # Indicate failure
    
    def _measure_memory(self, code: str) -> int:
        """Measure approximate memory usage"""
        # Simplified memory measurement
        return len(code.encode('utf-8'))

class EvolutionLogger:
    """Logs evolution attempts and results"""
    
    def __init__(self):
        self.log_file = EVOLUTION_PATH / "evolution_log.jsonl"
    
    def log_attempt(self, record: EvolutionRecord):
        """Log an evolution attempt"""
        log_entry = {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "stage": record.stage.value,
            "success": record.success,
            "reason": record.reason,
            "metrics_before": record.metrics_before,
            "metrics_after": record.metrics_after
        }
        
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Retrieve evolution history"""
        if not self.log_file.exists():
            return []
        
        history = []
        with open(self.log_file, "r", encoding='utf-8') as f:
            for line in f:
                history.append(json.loads(line.strip()))
        
        return history

class SelfEvolvingAgent:
    """Main self-evolving AI agent"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.improvement_engine = ImprovementEngine()
        self.testing_framework = TestingFramework()
        self.evolution_logger = EvolutionLogger()
        self.evolution_records = []
        
        # Track evolution metrics
        self.metrics_history = []
        
    def evolve_code(self, code_path: str) -> bool:
        """Perform evolution on code at given path"""
        try:
            # Read the code
            code_path = Path(code_path)
            original_code = code_path.read_text(encoding='utf-8')
            
            # Stage 1: Analysis
            logger.info(f"Analyzing code at {code_path}")
            analysis = self.code_analyzer.analyze_performance(original_code)
            
            # Stage 2: Identification of improvement opportunities
            logger.info("Identifying improvement opportunities")
            improvements = self.improvement_engine.generate_improvements(original_code, analysis)
            
            if not improvements:
                logger.info("No improvements identified")
                return False
            
            # Stage 3: Testing each improvement
            best_improvement = None
            best_validation = None
            
            for i, improved_code in enumerate(improvements):
                logger.info(f"Testing improvement {i+1}/{len(improvements)}")
                
                validation = self.testing_framework.validate_improvement(
                    original_code, improved_code
                )
                
                if validation["success"]:
                    if best_validation is None or self._is_better_than(validation, best_validation):
                        best_improvement = improved_code
                        best_validation = validation
            
            if best_improvement is None:
                logger.info("No valid improvements found")
                return False
            
            # Stage 4: Deployment
            logger.info("Deploying improvement")
            code_path.write_text(best_improvement, encoding='utf-8')
            
            # Stage 5: Evaluation and logging
            record = EvolutionRecord(
                id=f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(best_improvement.encode()).hexdigest()[:8]}",
                timestamp=datetime.now(),
                stage=EvolutionStage.EVALUATION,
                original_code=original_code,
                modified_code=best_improvement,
                test_results=best_validation,
                success=True,
                reason="Improvement successfully applied",
                metrics_before=analysis,
                metrics_after=self.code_analyzer.analyze_performance(best_improvement)
            )
            
            self.evolution_records.append(record)
            self.evolution_logger.log_attempt(record)
            
            logger.info(f"Evolution successful! Applied improvement to {code_path}")
            return True
            
        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            return False
    
    def _is_better_than(self, validation1: Dict[str, Any], validation2: Dict[str, Any]) -> bool:
        """Determine if validation1 is better than validation2"""
        # Prioritize functionality preservation first
        if not validation1.get("functionality_preserved", False):
            return False
        if not validation2.get("functionality_preserved", False):
            return True
        
        # Then prioritize performance improvements
        perf1 = validation1.get("improved_performance", float('inf'))
        perf2 = validation2.get("improved_performance", float('inf'))
        
        if perf1 < perf2:
            return True
        
        # Then memory improvements
        mem1 = validation1.get("improved_memory", float('inf'))
        mem2 = validation2.get("improved_memory", float('inf'))
        
        return mem1 < mem2
    
    def run_evolution_cycle(self, code_paths: List[str]) -> Dict[str, Any]:
        """Run a complete evolution cycle on multiple code paths"""
        results = {
            "total_files": len(code_paths),
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "start_time": datetime.now().isoformat(),
            "files_processed": []
        }
        
        for path in code_paths:
            logger.info(f"Processing {path}")
            success = self.evolve_code(path)
            
            results["files_processed"].append({
                "path": path,
                "success": success
            })
            
            if success:
                results["successful_evolutions"] += 1
            else:
                results["failed_evolutions"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        results["success_rate"] = results["successful_evolutions"] / len(code_paths) if code_paths else 0
        
        return results

# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the self-evolving system
    agent = SelfEvolvingAgent()
    
    # Example code to evolve (this would typically be loaded from files)
    example_code = '''
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total

def process_data(data):
    results = []
    for item in data:
        if item > 0:
            results.append(item * 2)
        else:
            results.append(0)
    return results
'''
    
    # Write example to a temporary file for testing
    test_file = EVOLUTION_PATH / "test_evolution.py"
    test_file.write_text(example_code)
    
    # Run evolution on the test file
    success = agent.evolve_code(str(test_file))
    
    if success:
        print("Evolution successful!")
        evolved_code = test_file.read_text()
        print("Evolved code:")
        print(evolved_code)
    else:
        print("Evolution failed")
    
    # Clean up
    test_file.unlink()