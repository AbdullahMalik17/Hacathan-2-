# Knowledge Management System for Self-Evolving AI
# Handles learning, memory, and knowledge synthesis

import os
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib
import threading
import time

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to main project root
VAULT_PATH = PROJECT_ROOT / "Vault"
KNOWLEDGE_PATH = VAULT_PATH / "Knowledge"
KNOWLEDGE_PATH.mkdir(parents=True, exist_ok=True)

@dataclass
class KnowledgeEntry:
    """Represents a piece of knowledge"""
    id: str
    content: str
    source: str
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    relevance_score: float = 1.0
    related_entries: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class KnowledgeDatabase:
    """SQLite-based knowledge storage and retrieval"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (KNOWLEDGE_PATH / "knowledge.db")
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the knowledge database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT,
                    timestamp TEXT,
                    tags TEXT,
                    confidence REAL,
                    relevance_score REAL,
                    related_entries TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON knowledge(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON knowledge(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON knowledge(timestamp)')
            
            conn.commit()
            conn.close()
    
    def add_entry(self, entry: KnowledgeEntry):
        """Add a knowledge entry to the database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge 
                (id, content, source, timestamp, tags, confidence, relevance_score, related_entries, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.id,
                entry.content,
                entry.source,
                entry.timestamp.isoformat(),
                json.dumps(entry.tags),
                entry.confidence,
                entry.relevance_score,
                json.dumps(entry.related_entries),
                json.dumps(entry.metadata)
            ))
            
            conn.commit()
            conn.close()
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM knowledge WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return KnowledgeEntry(
                    id=row[0],
                    content=row[1],
                    source=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    tags=json.loads(row[4]),
                    confidence=row[5],
                    relevance_score=row[6],
                    related_entries=json.loads(row[7]),
                    metadata=json.loads(row[8])
                )
            return None
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[KnowledgeEntry]:
        """Search for knowledge entries containing the query"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search in content and tags
            cursor.execute('''
                SELECT * FROM knowledge 
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY relevance_score DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            entries = []
            for row in rows:
                entry = KnowledgeEntry(
                    id=row[0],
                    content=row[1],
                    source=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    tags=json.loads(row[4]),
                    confidence=row[5],
                    relevance_score=row[6],
                    related_entries=json.loads(row[7]),
                    metadata=json.loads(row[8])
                )
                entries.append(entry)
            
            return entries
    
    def get_entries_by_tag(self, tag: str, limit: int = 10) -> List[KnowledgeEntry]:
        """Get knowledge entries by tag"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM knowledge 
                WHERE tags LIKE ?
                ORDER BY relevance_score DESC
                LIMIT ?
            ''', (f'%{tag}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            entries = []
            for row in rows:
                entry = KnowledgeEntry(
                    id=row[0],
                    content=row[1],
                    source=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    tags=json.loads(row[4]),
                    confidence=row[5],
                    relevance_score=row[6],
                    related_entries=json.loads(row[7]),
                    metadata=json.loads(row[8])
                )
                entries.append(entry)
            
            return entries

class KnowledgeSynthesizer:
    """Synthesizes new knowledge from existing knowledge"""
    
    def __init__(self, knowledge_db: KnowledgeDatabase):
        self.knowledge_db = knowledge_db
        self.synthesis_cache = {}
    
    def find_connections(self, entries: List[KnowledgeEntry]) -> List[Tuple[str, str, str]]:
        """Find connections between different knowledge entries"""
        connections = []
        
        for i, entry1 in enumerate(entries):
            for j, entry2 in enumerate(entries[i+1:], i+1):
                # Look for semantic connections
                similarity = self._calculate_similarity(entry1.content, entry2.content)
                
                if similarity > 0.7:  # Threshold for connection
                    connections.append((entry1.id, entry2.id, f"similarity_{similarity:.2f}"))
        
        return connections
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        # Simplified similarity calculation
        # In a real system, this would use embeddings or more sophisticated NLP
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def synthesize_new_insights(self, related_entries: List[KnowledgeEntry]) -> List[KnowledgeEntry]:
        """Generate new insights by combining related knowledge"""
        insights = []
        
        # Find patterns across related entries
        for i, entry1 in enumerate(related_entries):
            for j, entry2 in enumerate(related_entries[i+1:], i+1):
                # Generate synthetic insight from combination
                insight_content = self._generate_insight(entry1, entry2)
                
                if insight_content:
                    insight_id = hashlib.md5(
                        f"{entry1.id}_{entry2.id}_insight".encode()
                    ).hexdigest()
                    
                    insight = KnowledgeEntry(
                        id=insight_id,
                        content=insight_content,
                        source=f"synthesis_{entry1.id}_{entry2.id}",
                        timestamp=datetime.now(),
                        tags=["insight", "synthesis", "combination"],
                        confidence=0.8,  # Lower confidence for synthetic insights
                        relevance_score=0.7,
                        related_entries=[entry1.id, entry2.id],
                        metadata={
                            "derived_from": [entry1.id, entry2.id],
                            "synthesis_method": "combination"
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _generate_insight(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> Optional[str]:
        """Generate an insight by combining two knowledge entries"""
        # This is a simplified example
        # In a real system, this would use more sophisticated reasoning
        
        # Look for cause-effect relationships
        if "causes" in entry1.content.lower() and "solution" in entry2.content.lower():
            return f"When {entry1.content} occurs, applying {entry2.content} can be an effective solution."
        
        # Look for patterns
        if "pattern" in entry1.content.lower() and "implementation" in entry2.content.lower():
            return f"The pattern described in '{entry1.content}' can be implemented using the approach in '{entry2.content}'."
        
        # General combination
        return f"Combining insights: {entry1.content[:100]}... and {entry2.content[:100]}..."
    
    def update_relevance_scores(self):
        """Update relevance scores based on usage patterns"""
        # This would analyze how often entries are accessed and update scores
        # For now, it's a placeholder
        pass

class LearningModule:
    """Handles the learning aspect of the self-evolving system"""
    
    def __init__(self, knowledge_db: KnowledgeDatabase):
        self.knowledge_db = knowledge_db
        self.synthesizer = KnowledgeSynthesizer(knowledge_db)
        self.learning_history = []
    
    def learn_from_experience(self, experience_data: Dict[str, Any]) -> List[KnowledgeEntry]:
        """Learn from an experience or task completion"""
        new_knowledge = []
        
        # Extract key information from experience
        experience_summary = self._summarize_experience(experience_data)
        
        if experience_summary:
            # Create knowledge entry from experience
            # Convert experience_data to a hashable representation
            exp_id = hashlib.md5(
                f"experience_{datetime.now().isoformat()}_{hash(str(sorted(experience_data.items())))}".encode()
            ).hexdigest()
            
            experience_entry = KnowledgeEntry(
                id=exp_id,
                content=experience_summary,
                source="experience",
                timestamp=datetime.now(),
                tags=["experience", "learning", "task_completion"],
                confidence=0.9,
                relevance_score=0.8,
                metadata=experience_data
            )
            
            new_knowledge.append(experience_entry)
            
            # Add to knowledge base
            self.knowledge_db.add_entry(experience_entry)
        
        return new_knowledge
    
    def _summarize_experience(self, experience_data: Dict[str, Any]) -> Optional[str]:
        """Create a summary of an experience"""
        try:
            # Extract key elements from experience
            task = experience_data.get('task', 'Unknown task')
            result = experience_data.get('result', 'Unknown result')
            method = experience_data.get('method', 'Unknown method')
            outcome = experience_data.get('outcome', 'Unknown outcome')
            
            summary = f"Task: {task}. Method: {method}. Result: {result}. Outcome: {outcome}."
            
            # Add performance metrics if available
            if 'metrics' in experience_data:
                metrics = experience_data['metrics']
                summary += f" Performance: {json.dumps(metrics)}"
            
            return summary
        except Exception:
            return None
    
    def acquire_new_skill(self, skill_description: str) -> bool:
        """Acquire a new skill by learning and synthesizing knowledge"""
        try:
            # Search for existing knowledge about the skill
            existing_knowledge = self.knowledge_db.search_knowledge(skill_description, limit=5)
            
            # Synthesize new knowledge from existing knowledge
            if existing_knowledge:
                new_insights = self.synthesizer.synthesize_new_insights(existing_knowledge)
                
                for insight in new_insights:
                    self.knowledge_db.add_entry(insight)
            
            # Create skill acquisition record
            skill_id = hashlib.md5(f"skill_{skill_description}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            skill_entry = KnowledgeEntry(
                id=skill_id,
                content=f"Acquired skill: {skill_description}",
                source="skill_acquisition",
                timestamp=datetime.now(),
                tags=["skill", "acquisition", skill_description],
                confidence=0.7,
                relevance_score=0.9,
                metadata={"skill_name": skill_description, "acquisition_method": "knowledge_synthesis"}
            )
            
            self.knowledge_db.add_entry(skill_entry)
            self.learning_history.append({
                "timestamp": datetime.now(),
                "type": "skill_acquisition",
                "skill": skill_description,
                "success": True
            })
            
            return True
            
        except Exception as e:
            self.learning_history.append({
                "timestamp": datetime.now(),
                "type": "skill_acquisition",
                "skill": skill_description,
                "success": False,
                "error": str(e)
            })
            return False
    
    def assess_skill_mastery(self, skill_name: str) -> float:
        """Assess the mastery level of a skill"""
        # Search for knowledge entries related to the skill
        skill_entries = self.knowledge_db.get_entries_by_tag(skill_name, limit=20)
        
        if not skill_entries:
            return 0.0  # No knowledge about this skill
        
        # Calculate mastery based on various factors
        total_confidence = sum(entry.confidence for entry in skill_entries)
        avg_confidence = total_confidence / len(skill_entries) if skill_entries else 0.0
        
        # Factor in recency of knowledge
        recent_entries = [e for e in skill_entries if 
                         datetime.now() - e.timestamp < timedelta(days=30)]
        recency_factor = len(recent_entries) / len(skill_entries) if skill_entries else 0.0
        
        # Combine factors for mastery score
        mastery_score = (avg_confidence * 0.7) + (recency_factor * 0.3)
        
        return min(mastery_score, 1.0)  # Cap at 1.0

# Example usage
if __name__ == "__main__":
    # Initialize the knowledge system
    knowledge_db = KnowledgeDatabase()
    learning_module = LearningModule(knowledge_db)
    
    # Example: Learn from an experience
    experience = {
        "task": "optimize_api_response_time",
        "method": "implement_caching_layer",
        "result": "reduced_response_time_by_40_percent",
        "outcome": "successful",
        "metrics": {
            "before_ms": 2500,
            "after_ms": 1500,
            "improvement_percentage": 40
        }
    }
    
    new_knowledge = learning_module.learn_from_experience(experience)
    print(f"Learned from experience, created {len(new_knowledge)} knowledge entries")
    
    # Example: Acquire a new skill
    skill_acquired = learning_module.acquire_new_skill("machine_learning_optimization")
    print(f"Skill acquisition {'successful' if skill_acquired else 'failed'}")
    
    # Example: Assess skill mastery
    mastery = learning_module.assess_skill_mastery("machine_learning_optimization")
    print(f"Skill mastery level: {mastery:.2f}")
    
    # Example: Search for knowledge
    search_results = knowledge_db.search_knowledge("optimization", limit=3)
    print(f"Found {len(search_results)} entries related to 'optimization'")