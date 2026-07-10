"""
Skill registry for MindPy.

Manages skill registration, lookup, and execution.
"""

from typing import Dict, List, Optional
from mindpy.skills.skill import Skill, SkillState, SkillResult
from mindpy.logging import get_logger


class SkillRegistry:
    """
    Registry for skills.
    
    Manages skill registration, lookup, and execution.
    """
    
    def __init__(self):
        """Initialize the skill registry."""
        self._skills: Dict[str, Skill] = {}
        self._active_skills: Dict[str, Skill] = {}
        self._logger = get_logger(__name__)
    
    def register(self, skill: Skill) -> None:
        """
        Register a skill.
        
        Args:
            skill: Skill to register
        """
        self._skills[skill.name] = skill
        self._logger.info(f"Registered skill: {skill.name}")
    
    def unregister(self, skill_name: str) -> bool:
        """
        Unregister a skill.
        
        Args:
            skill_name: Skill name
            
        Returns:
            True if unregistered
        """
        if skill_name in self._skills:
            # Stop if active
            if skill_name in self._active_skills:
                import asyncio
                asyncio.create_task(self.stop_skill(skill_name))
            
            del self._skills[skill_name]
            self._logger.info(f"Unregistered skill: {skill_name}")
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            skill_name: Skill name
            
        Returns:
            Skill or None
        """
        return self._skills.get(skill_name)
    
    def get_all_skills(self) -> List[Skill]:
        """Get all registered skills."""
        return list(self._skills.values())
    
    async def execute_skill(
        self,
        skill_name: str,
        context: Dict[str, any]
    ) -> SkillResult:
        """
        Execute a skill.
        
        Args:
            skill_name: Skill name
            context: Execution context
            
        Returns:
            Skill result
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillResult(
                success=False,
                message=f"Skill not found: {skill_name}"
            )
        
        if skill_name in self._active_skills:
            return SkillResult(
                success=False,
                message=f"Skill already active: {skill_name}"
            )
        
        self._active_skills[skill_name] = skill
        skill._set_state(SkillState.RUNNING)
        
        try:
            result = await skill.execute(context)
            skill._set_state(SkillState.COMPLETED if result.success else SkillState.FAILED)
            return result
        except Exception as e:
            skill._set_state(SkillState.FAILED)
            self._logger.error(f"Error executing skill {skill_name}: {e}")
            return SkillResult(
                success=False,
                message=f"Error: {str(e)}"
            )
        finally:
            if skill_name in self._active_skills:
                del self._active_skills[skill_name]
    
    async def pause_skill(self, skill_name: str) -> bool:
        """
        Pause an active skill.
        
        Args:
            skill_name: Skill name
            
        Returns:
            True if paused
        """
        skill = self._active_skills.get(skill_name)
        if not skill:
            return False
        
        await skill.pause()
        skill._set_state(SkillState.PAUSED)
        return True
    
    async def resume_skill(self, skill_name: str) -> bool:
        """
        Resume a paused skill.
        
        Args:
            skill_name: Skill name
            
        Returns:
            True if resumed
        """
        skill = self._skills.get(skill_name)
        if not skill or skill.get_state() != SkillState.PAUSED:
            return False
        
        await skill.resume()
        skill._set_state(SkillState.RUNNING)
        self._active_skills[skill_name] = skill
        return True
    
    async def stop_skill(self, skill_name: str) -> bool:
        """
        Stop an active skill.
        
        Args:
            skill_name: Skill name
            
        Returns:
            True if stopped
        """
        skill = self._active_skills.get(skill_name)
        if not skill:
            return False
        
        await skill.cancel()
        skill._set_state(SkillState.CANCELLED)
        
        if skill_name in self._active_skills:
            del self._active_skills[skill_name]
        
        return True
    
    def get_active_skills(self) -> List[Skill]:
        """Get all currently active skills."""
        return list(self._active_skills.values())
    
    def get_skill_count(self) -> int:
        """Get the total number of registered skills."""
        return len(self._skills)
    
    def has_skill(self, skill_name: str) -> bool:
        """Check if a skill is registered."""
        return skill_name in self._skills
    
    def clear(self) -> None:
        """Clear all skills."""
        self._skills.clear()
        self._active_skills.clear()
    
    def __repr__(self) -> str:
        return f"SkillRegistry(skills={self.get_skill_count()}, active={len(self._active_skills)})"
