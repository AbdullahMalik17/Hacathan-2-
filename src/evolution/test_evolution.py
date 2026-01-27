# Test for Self-Evolving AI Employee System

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
SRC_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SRC_DIR))

from evolution.self_evolution_engine import SelfEvolvingAgent, CodeAnalyzer, ImprovementEngine, TestingFramework
from evolution.knowledge_system import KnowledgeDatabase, LearningModule, KnowledgeEntry
from evolution.config import get_default_config

class TestSelfEvolutionEngine(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_code.py"
        
        # Sample code to test evolution on
        self.sample_code = '''
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
        
        self.test_file.write_text(self.sample_code)
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_code_analyzer(self):
        """Test the code analyzer functionality"""
        analyzer = CodeAnalyzer()
        metrics = analyzer.analyze_performance(self.sample_code)
        
        self.assertIn('lines_of_code', metrics)
        self.assertIn('cyclomatic_complexity', metrics)
        self.assertGreater(metrics['lines_of_code'], 0)
        self.assertGreaterEqual(metrics['cyclomatic_complexity'], 1)
    
    def test_improvement_engine(self):
        """Test the improvement engine"""
        analyzer = CodeAnalyzer()
        improvement_engine = ImprovementEngine()
        
        metrics = analyzer.analyze_performance(self.sample_code)
        improvements = improvement_engine.generate_improvements(self.sample_code, metrics)
        
        # Should generate at least one improvement
        self.assertGreater(len(improvements), 0)
        
        # Each improvement should be a string
        for imp in improvements:
            self.assertIsInstance(imp, str)
    
    def test_testing_framework(self):
        """Test the testing framework"""
        testing_framework = TestingFramework()
        
        # Test that validation works (even if it fails)
        result = testing_framework.validate_improvement(self.sample_code, self.sample_code)
        
        # Should return a dictionary with results
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_self_evolution_agent(self):
        """Test the complete self-evolution agent"""
        agent = SelfEvolvingAgent()
        
        # This is a complex test, so we'll just ensure it doesn't crash
        # In a real scenario, we'd have more specific tests
        try:
            # The agent should be able to analyze the test file
            analysis = agent.code_analyzer.analyze_performance(self.sample_code)
            self.assertIsInstance(analysis, dict)
        except Exception as e:
            self.fail(f"SelfEvolvingAgent raised {e} unexpectedly!")

class TestKnowledgeSystem(unittest.TestCase):
    def setUp(self):
        """Set up knowledge system test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_knowledge.db"
        
    def tearDown(self):
        """Clean up knowledge system test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_knowledge_database(self):
        """Test the knowledge database functionality"""
        db = KnowledgeDatabase(db_path=self.db_path)
        
        # Create a test entry
        from datetime import datetime
        entry = KnowledgeEntry(
            id="test_entry_1",
            content="This is a test knowledge entry",
            source="unittest",
            timestamp=datetime.now(),
            tags=["test", "knowledge"],
            confidence=0.9,
            relevance_score=0.8
        )
        
        # Add the entry
        db.add_entry(entry)
        
        # Retrieve the entry
        retrieved = db.get_entry("test_entry_1")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test_entry_1")
        self.assertEqual(retrieved.content, "This is a test knowledge entry")
    
    def test_learning_module(self):
        """Test the learning module"""
        db = KnowledgeDatabase(db_path=self.db_path)
        learning_module = LearningModule(db)
        
        # Test experience learning
        experience = {
            "task": "test_task",
            "method": "test_method",
            "result": "test_result",
            "outcome": "success",
            "metrics": {"accuracy": 0.95, "speed": 1.2}
        }
        
        knowledge = learning_module.learn_from_experience(experience)
        
        # Should have created at least one knowledge entry
        self.assertGreater(len(knowledge), 0)
        
        # Test skill acquisition
        success = learning_module.acquire_new_skill("test_skill")
        self.assertTrue(success)
        
        # Test skill assessment
        mastery = learning_module.assess_skill_mastery("test_skill")
        self.assertGreaterEqual(mastery, 0.0)
        self.assertLessEqual(mastery, 1.0)

class TestConfiguration(unittest.TestCase):
    def test_default_configuration(self):
        """Test the default configuration"""
        config = get_default_config()
        
        # Check that required attributes exist
        self.assertTrue(hasattr(config, 'enabled'))
        self.assertTrue(hasattr(config, 'max_iterations'))
        self.assertTrue(hasattr(config, 'safety_threshold'))
        self.assertTrue(hasattr(config, 'target_files'))
        
        # Check that default values are reasonable
        self.assertTrue(config.enabled)
        self.assertGreater(config.max_iterations, 0)
        self.assertGreaterEqual(config.safety_threshold, 0.0)
        self.assertLessEqual(config.safety_threshold, 1.0)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()