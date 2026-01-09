"""Cosmos DB Progress Tracker for NextRole AI"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from azure.cosmos import CosmosClient, PartitionKey

logger = logging.getLogger(__name__)


class CosmosProgressTracker:
    """Tracks user career progress using Azure Cosmos DB"""

    def __init__(self):
        """Initialize Cosmos DB client and container"""
        self.connection_string = os.getenv("COSMOS_CONNECTION_STRING")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME", "nextrole-db")
        self.container_name = os.getenv("COSMOS_CONTAINER_NAME", "progress")
        
        if not self.connection_string:
            logger.warning("COSMOS_CONNECTION_STRING not set; progress tracking disabled")
            self.client = None
            self.container = None
            return
        
        try:
            self.client = CosmosClient.from_connection_string(self.connection_string)
            database = self.client.get_database_client(self.database_name)
            self.container = database.get_container_client(self.container_name)
            logger.info("Cosmos DB progress tracker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            self.client = None
            self.container = None

    def save_user_session(self, user_id: str, session_data: Dict) -> bool:
        """Save or update user session (skills, career goal, etc.)"""
        if not self.container:
            logger.warning("Cosmos DB not available; skipping save_user_session")
            return False
        
        try:
            item = {
                "id": f"session_{user_id}_{datetime.utcnow().isoformat()}",
                "user_id": user_id,
                "type": "session",
                "timestamp": datetime.utcnow().isoformat(),
                "skills": session_data.get("skills", []),
                "career_goal": session_data.get("career_goal"),
                "experience_level": session_data.get("experience_level"),
                "current_role": session_data.get("current_role"),
            }
            self.container.create_item(body=item)
            logger.info(f"Session saved for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def save_role_selection(self, user_id: str, role: Dict) -> bool:
        """Track when user selects a career role"""
        if not self.container:
            logger.warning("Cosmos DB not available; skipping save_role_selection")
            return False
        
        try:
            item = {
                "id": f"role_selection_{user_id}_{datetime.utcnow().isoformat()}",
                "user_id": user_id,
                "type": "role_selection",
                "timestamp": datetime.utcnow().isoformat(),
                "role_name": role.get("role"),
                "summary": role.get("summary"),
                "required_skills": role.get("required_skills", []),
                "missing_skills": role.get("missing_skills", []),
            }
            self.container.create_item(body=item)
            logger.info(f"Role selection recorded for user {user_id}: {role.get('role')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save role selection: {e}")
            return False

    def save_phase_progress(self, user_id: str, role_name: str, phase_number: int, progress: Dict) -> bool:
        """Track completion of a study phase"""
        if not self.container:
            logger.warning("Cosmos DB not available; skipping save_phase_progress")
            return False
        
        try:
            item = {
                "id": f"phase_progress_{user_id}_{role_name}_{phase_number}_{datetime.utcnow().isoformat()}",
                "user_id": user_id,
                "type": "phase_progress",
                "timestamp": datetime.utcnow().isoformat(),
                "role_name": role_name,
                "phase_number": phase_number,
                "status": progress.get("status", "in_progress"),  # in_progress, completed
                "completion_percentage": progress.get("completion_percentage", 0),
                "hours_spent": progress.get("hours_spent", 0),
                "skills_learned": progress.get("skills_learned", []),
                "notes": progress.get("notes", ""),
            }
            self.container.create_item(body=item)
            logger.info(f"Phase progress recorded for user {user_id}, role {role_name}, phase {phase_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to save phase progress: {e}")
            return False

    def save_skill_milestone(self, user_id: str, skill: str, milestone_data: Dict) -> bool:
        """Track when user completes a skill milestone"""
        if not self.container:
            logger.warning("Cosmos DB not available; skipping save_skill_milestone")
            return False
        
        try:
            item = {
                "id": f"skill_milestone_{user_id}_{skill}_{datetime.utcnow().isoformat()}",
                "user_id": user_id,
                "type": "skill_milestone",
                "timestamp": datetime.utcnow().isoformat(),
                "skill": skill,
                "proficiency_level": milestone_data.get("proficiency_level", "beginner"),  # beginner, intermediate, advanced
                "resources_used": milestone_data.get("resources_used", []),
                "certification": milestone_data.get("certification", ""),
            }
            self.container.create_item(body=item)
            logger.info(f"Skill milestone recorded for user {user_id}: {skill}")
            return True
        except Exception as e:
            logger.error(f"Failed to save skill milestone: {e}")
            return False

    def get_user_progress_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve user's progress history"""
        if not self.container:
            logger.warning("Cosmos DB not available; returning empty history")
            return []
        
        try:
            query = f"SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
            items = list(self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@user_id", "value": user_id},
                    {"name": "@limit", "value": limit}
                ]
            ))
            logger.info(f"Retrieved {len(items)} progress records for user {user_id}")
            return items
        except Exception as e:
            logger.error(f"Failed to retrieve progress history: {e}")
            return []

    def get_user_stats(self, user_id: str) -> Dict:
        """Get aggregated statistics for user"""
        if not self.container:
            logger.warning("Cosmos DB not available; returning empty stats")
            return {
                "total_roles_explored": 0,
                "total_phases_completed": 0,
                "total_hours_studied": 0,
                "skills_learned": [],
                "roles_history": [],
            }
        
        try:
            history = self.get_user_progress_history(user_id, limit=500)
            
            stats = {
                "total_roles_explored": 0,
                "total_phases_completed": 0,
                "total_hours_studied": 0,
                "skills_learned": [],
                "roles_history": [],
                "milestones": [],
            }
            
            seen_roles = set()
            for item in history:
                item_type = item.get("type")
                
                if item_type == "role_selection":
                    role_name = item.get("role_name")
                    if role_name not in seen_roles:
                        seen_roles.add(role_name)
                        stats["total_roles_explored"] += 1
                        stats["roles_history"].append({
                            "role": role_name,
                            "timestamp": item.get("timestamp"),
                        })
                
                elif item_type == "phase_progress":
                    if item.get("status") == "completed":
                        stats["total_phases_completed"] += 1
                    stats["total_hours_studied"] += item.get("hours_spent", 0)
                
                elif item_type == "skill_milestone":
                    skill = item.get("skill")
                    if skill not in stats["skills_learned"]:
                        stats["skills_learned"].append(skill)
                    stats["milestones"].append({
                        "skill": skill,
                        "level": item.get("proficiency_level"),
                        "timestamp": item.get("timestamp"),
                    })
            
            logger.info(f"Computed stats for user {user_id}: {stats['total_roles_explored']} roles, {stats['total_phases_completed']} phases completed")
            return stats
        except Exception as e:
            logger.error(f"Failed to compute user stats: {e}")
            return {}

    def is_available(self) -> bool:
        """Check if Cosmos DB is available"""
        return self.container is not None


def get_progress_tracker() -> CosmosProgressTracker:
    """Factory function to get progress tracker instance"""
    return CosmosProgressTracker()
