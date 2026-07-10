"""
Knowledge base implementation for MindPy.

Knowledge base stores structured knowledge and rules.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from mindpy.memory.base import Memory, MemoryEntry


@dataclass
class KnowledgeEntry:
    """A knowledge entry."""
    subject: str
    predicate: str
    object: str
    confidence: float
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def to_triple(self) -> tuple[str, str, str]:
        """Convert to (subject, predicate, object) triple."""
        return (self.subject, self.predicate, self.object)


@dataclass
class Rule:
    """A rule for reasoning."""
    name: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: float = 0.5
    enabled: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class KnowledgeBase(Memory):
    """
    Knowledge base for storing structured knowledge and rules.
    
    Uses a triple-store like structure for facts and a rule system
    for reasoning.
    """
    
    def __init__(self, capacity: int = 1000, persistence_enabled: bool = True):
        """
        Initialize knowledge base.
        
        Args:
            capacity: Maximum number of entries (default: 1000)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._spo_index: Dict[tuple[str, str, str], str] = {}  # (subject, predicate, object) -> entry_id
        self._sp_index: Dict[tuple[str, str], List[str]] = {}  # (subject, predicate) -> list of entry_ids
        self._rules: Dict[str, str] = {}  # rule_name -> entry_id
    
    def add(self, content: Any, entry_type: str = "knowledge", **metadata) -> MemoryEntry:
        """
        Add knowledge to the base.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        if self.is_full():
            self._evict_least_accessed()
        
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 0.7)
        )
        
        self._entries[entry.entry_id] = entry
        
        # Index by type
        if entry_type == "knowledge_entry" and isinstance(content, KnowledgeEntry):
            triple = content.to_triple()
            self._spo_index[triple] = entry.entry_id
            
            sp_key = (content.subject, content.predicate)
            if sp_key not in self._sp_index:
                self._sp_index[sp_key] = []
            self._sp_index[sp_key].append(entry.entry_id)
        
        elif entry_type == "rule" and isinstance(content, Rule):
            self._rules[content.name] = entry.entry_id
        
        return entry
    
    def add_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        source: str = "user"
    ) -> MemoryEntry:
        """
        Add a fact to the knowledge base.
        
        Args:
            subject: The subject of the fact
            predicate: The predicate/relation
            obj: The object of the fact
            confidence: Confidence score (0.0 to 1.0)
            source: Source of the knowledge
            
        Returns:
            The memory entry
        """
        knowledge = KnowledgeEntry(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            source=source,
            timestamp=datetime.utcnow()
        )
        return self.add(knowledge, "knowledge_entry", importance=0.7)
    
    def get_fact(self, subject: str, predicate: str, obj: str) -> Optional[KnowledgeEntry]:
        """
        Get a specific fact.
        
        Args:
            subject: The subject
            predicate: The predicate
            obj: The object
            
        Returns:
            KnowledgeEntry or None if not found
        """
        entry_id = self._spo_index.get((subject, predicate, obj))
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def query_subject(self, subject: str) -> List[KnowledgeEntry]:
        """
        Query all facts about a subject.
        
        Args:
            subject: The subject to query
            
        Returns:
            List of knowledge entries
        """
        results = []
        for (s, p), entry_ids in self._sp_index.items():
            if s == subject:
                for entry_id in entry_ids:
                    entry = self.get(entry_id)
                    if entry:
                        results.append(entry.content)
                        entry.access()
        return results
    
    def query_predicate(self, predicate: str) -> List[KnowledgeEntry]:
        """
        Query all facts with a predicate.
        
        Args:
            predicate: The predicate to query
            
        Returns:
            List of knowledge entries
        """
        results = []
        for (s, p), entry_ids in self._sp_index.items():
            if p == predicate:
                for entry_id in entry_ids:
                    entry = self.get(entry_id)
                    if entry:
                        results.append(entry.content)
                        entry.access()
        return results
    
    def query_object(self, obj: str) -> List[KnowledgeEntry]:
        """
        Query all facts about an object.
        
        Args:
            obj: The object to query
            
        Returns:
            List of knowledge entries
        """
        results = []
        for entry in self._entries.values():
            if entry.entry_type == "knowledge_entry":
                if entry.content.object == obj:
                    results.append(entry.content)
                    entry.access()
        return results
    
    def add_rule(
        self,
        name: str,
        conditions: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        priority: float = 0.5,
        **metadata
    ) -> MemoryEntry:
        """
        Add a rule to the knowledge base.
        
        Args:
            name: Rule name
            conditions: List of condition dictionaries
            actions: List of action dictionaries
            priority: Rule priority
            **metadata: Additional metadata
            
        Returns:
            The memory entry
        """
        rule = Rule(
            name=name,
            conditions=conditions,
            actions=actions,
            priority=priority,
            metadata=metadata
        )
        return self.add(rule, "rule", importance=0.8)
    
    def get_rule(self, name: str) -> Optional[Rule]:
        """
        Get a rule by name.
        
        Args:
            name: Rule name
            
        Returns:
            Rule or None if not found
        """
        entry_id = self._rules.get(name)
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def get_all_rules(self, enabled_only: bool = True) -> List[Rule]:
        """
        Get all rules.
        
        Args:
            enabled_only: Whether to only return enabled rules
            
        Returns:
            List of rules
        """
        rules = self.get_by_type("rule")
        if enabled_only:
            rules = [r for r in rules if r.content.enabled]
        return [r.content for r in rules]
    
    def update_rule_status(self, name: str, enabled: bool) -> bool:
        """
        Enable or disable a rule.
        
        Args:
            name: Rule name
            enabled: Whether to enable the rule
            
        Returns:
            True if updated, False if not found
        """
        rule = self.get_rule(name)
        if rule:
            rule.enabled = enabled
            return True
        return False
    
    def search_knowledge(self, query: str, limit: int = 20) -> List[KnowledgeEntry]:
        """
        Search knowledge by text.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge entries
        """
        results = []
        query_lower = query.lower()
        
        for entry in self._entries.values():
            if entry.entry_type == "knowledge_entry":
                content = entry.content
                text = f"{content.subject} {content.predicate} {content.object}".lower()
                if query_lower in text:
                    results.append(content)
                    entry.access()
                    if len(results) >= limit:
                        break
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Dictionary with statistics
        """
        facts = self.get_by_type("knowledge_entry")
        rules = self.get_by_type("rule")
        
        return {
            "total_facts": len(facts),
            "total_rules": len(rules),
            "enabled_rules": len([r for r in rules if r.content.enabled]),
            "unique_subjects": len(set(f.subject for f in facts)),
            "unique_predicates": len(set(f.predicate for f in facts)),
        }
