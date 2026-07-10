"""
Reflection engine for MindPy AI.

Provides self-improvement through task evaluation and learning.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mindpy.llm.provider import LLMProvider, LLMMessage, MessageRole
from mindpy.llm.manager import LLMManager
from mindpy.logging import get_logger


class ReflectionType(Enum):
    """Types of reflection."""
    TASK_EVALUATION = "task_evaluation"
    DECISION_ANALYSIS = "decision_analysis"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_REVIEW = "performance_review"
    STRATEGY_ADJUSTMENT = "strategy_adjustment"


@dataclass
class ReflectionResult:
    """
    Result of a reflection operation.
    
    Contains analysis, lessons learned, and recommendations.
    """
    reflection_type: ReflectionType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    analysis: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"ReflectionResult({self.reflection_type.value}, lessons={len(self.lessons_learned)})"


class ReflectionEngine:
    """
    Engine for AI self-reflection and improvement.
    
    Evaluates past actions, learns from mistakes, and improves future decisions.
    """
    
    def __init__(
        self,
        llm_manager: LLMManager,
        reflection_prompt: Optional[str] = None
    ):
        """
        Initialize the reflection engine.
        
        Args:
            llm_manager: LLM manager for generating reflections
            reflection_prompt: Optional custom reflection prompt
        """
        self._llm_manager = llm_manager
        self._reflection_prompt = reflection_prompt or self._default_reflection_prompt()
        self._reflection_history: List[ReflectionResult] = []
        self._logger = get_logger(__name__)
    
    def _default_reflection_prompt(self) -> str:
        """Get the default reflection prompt."""
        return """You are an AI reflection engine. Your task is to analyze past actions and decisions, identify what worked well and what didn't, and provide recommendations for improvement.

Consider:
1. What was the goal?
2. What actions were taken?
3. What was the outcome?
4. What succeeded and why?
5. What failed and why?
6. What could be done differently next time?

Provide specific, actionable recommendations."""
    
    async def reflect_on_task(
        self,
        task_description: str,
        actions_taken: List[str],
        outcome: str,
        success: bool
    ) -> ReflectionResult:
        """
        Reflect on a completed task.
        
        Args:
            task_description: Description of the task
            actions_taken: List of actions taken
            outcome: Task outcome
            success: Whether the task was successful
            
        Returns:
            Reflection result
        """
        prompt = f"""Task: {task_description}

Actions taken:
{chr(10).join(f"- {action}" for action in actions_taken)}

Outcome: {outcome}
Success: {success}

Reflect on this task and provide analysis, lessons learned, and recommendations."""
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=self._reflection_prompt),
            LLMMessage(role=MessageRole.USER, content=prompt)
        ]
        
        response = await self._llm_manager.generate(messages)
        
        # Parse the response
        result = self._parse_reflection_response(
            ReflectionType.TASK_EVALUATION,
            response.content
        )
        
        result.metadata = {
            "task_description": task_description,
            "success": success
        }
        
        self._reflection_history.append(result)
        return result
    
    async def reflect_on_decision(
        self,
        decision: str,
        context: Dict[str, Any],
        outcome: str
    ) -> ReflectionResult:
        """
        Reflect on a past decision.
        
        Args:
            decision: The decision that was made
            context: Context at the time of decision
            outcome: Outcome of the decision
            
        Returns:
            Reflection result
        """
        prompt = f"""Decision: {decision}

Context:
{self._format_context(context)}

Outcome: {outcome}

Reflect on this decision and provide analysis, lessons learned, and recommendations."""
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=self._reflection_prompt),
            LLMMessage(role=MessageRole.USER, content=prompt)
        ]
        
        response = await self._llm_manager.generate(messages)
        
        result = self._parse_reflection_response(
            ReflectionType.DECISION_ANALYSIS,
            response.content
        )
        
        result.metadata = {
            "decision": decision,
            "context": context
        }
        
        self._reflection_history.append(result)
        return result
    
    async def reflect_on_error(
        self,
        error: str,
        context: Dict[str, Any],
        attempted_solutions: List[str]
    ) -> ReflectionResult:
        """
        Reflect on an error that occurred.
        
        Args:
            error: Error that occurred
            context: Context when error occurred
            attempted_solutions: Solutions that were tried
            
        Returns:
            Reflection result
        """
        prompt = f"""Error: {error}

Context:
{self._format_context(context)}

Attempted solutions:
{chr(10).join(f"- {solution}" for solution in attempted_solutions)}

Reflect on this error and provide analysis, lessons learned, and recommendations for avoiding similar errors in the future."""
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=self._reflection_prompt),
            LLMMessage(role=MessageRole.USER, content=prompt)
        ]
        
        response = await self._llm_manager.generate(messages)
        
        result = self._parse_reflection_response(
            ReflectionType.ERROR_ANALYSIS,
            response.content
        )
        
        result.metadata = {
            "error": error,
            "attempted_solutions": attempted_solutions
        }
        
        self._reflection_history.append(result)
        return result
    
    async def performance_review(
        self,
        tasks_completed: List[Dict[str, Any]],
        time_period: str
    ) -> ReflectionResult:
        """
        Review overall performance over a time period.
        
        Args:
            tasks_completed: List of completed tasks with metadata
            time_period: Time period description
            
        Returns:
            Reflection result
        """
        success_count = sum(1 for task in tasks_completed if task.get("success", False))
        total_count = len(tasks_completed)
        
        prompt = f"""Performance review for {time_period}

Tasks completed: {total_count}
Successful: {success_count}
Failed: {total_count - success_count}
Success rate: {success_count / total_count * 100 if total_count > 0 else 0:.1f}%

Tasks:
{chr(10).join(f"- {task.get('description', 'Unknown')}: {'Success' if task.get('success') else 'Failed'}" for task in tasks_completed[:10])}

Reflect on this performance and provide analysis, lessons learned, and recommendations."""
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=self._reflection_prompt),
            LLMMessage(role=MessageRole.USER, content=prompt)
        ]
        
        response = await self._llm_manager.generate(messages)
        
        result = self._parse_reflection_response(
            ReflectionType.PERFORMANCE_REVIEW,
            response.content
        )
        
        result.metadata = {
            "time_period": time_period,
            "total_tasks": total_count,
            "successful_tasks": success_count
        }
        
        self._reflection_history.append(result)
        return result
    
    def _parse_reflection_response(
        self,
        reflection_type: ReflectionType,
        response: str
    ) -> ReflectionResult:
        """
        Parse the LLM response into a reflection result.
        
        Args:
            reflection_type: Type of reflection
            response: LLM response text
            
        Returns:
            Parsed reflection result
        """
        # Simple parsing - in production, use more sophisticated parsing
        lines = response.split('\n')
        
        analysis = ""
        lessons = []
        recommendations = []
        
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            
            if "analysis" in line_lower or "what happened" in line_lower:
                current_section = "analysis"
            elif "lesson" in line_lower or "learned" in line_lower:
                current_section = "lessons"
            elif "recommend" in line_lower or "suggestion" in line_lower or "improve" in line_lower:
                current_section = "recommendations"
            elif line.strip():
                if current_section == "analysis":
                    analysis += line + "\n"
                elif current_section == "lessons":
                    lessons.append(line.strip("- "))
                elif current_section == "recommendations":
                    recommendations.append(line.strip("- "))
        
        return ReflectionResult(
            reflection_type=reflection_type,
            analysis=analysis.strip(),
            lessons_learned=lessons,
            recommendations=recommendations
        )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary for the LLM.
        
        Args:
            context: Context dictionary
            
        Returns:
            Formatted context string
        """
        lines = []
        for key, value in context.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def get_lessons_learned(self, reflection_type: Optional[ReflectionType] = None) -> List[str]:
        """
        Get all lessons learned from reflections.
        
        Args:
            reflection_type: Optional type filter
            
        Returns:
            List of lessons
        """
        lessons = []
        
        for reflection in self._reflection_history:
            if reflection_type is None or reflection.reflection_type == reflection_type:
                lessons.extend(reflection.lessons_learned)
        
        return lessons
    
    def get_recommendations(self, reflection_type: Optional[ReflectionType] = None) -> List[str]:
        """
        Get all recommendations from reflections.
        
        Args:
            reflection_type: Optional type filter
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for reflection in self._reflection_history:
            if reflection_type is None or reflection.reflection_type == reflection_type:
                recommendations.extend(reflection.recommendations)
        
        return recommendations
    
    def get_reflection_history(self) -> List[ReflectionResult]:
        """Get the full reflection history."""
        return self._reflection_history.copy()
    
    def clear_history(self) -> None:
        """Clear reflection history."""
        self._reflection_history.clear()
    
    def __repr__(self) -> str:
        return f"ReflectionEngine(reflections={len(self._reflection_history)})"
