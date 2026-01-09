"""Azure Table Storage Progress Tracker for NextRole AI"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError

logger = logging.getLogger(__name__)


class TableStorageProgressTracker:
    """Tracks user career progress using Azure Table Storage"""

    def __init__(self):
        """Initialize Table Storage client"""
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.table_name = os.getenv("AZURE_STORAGE_TABLE_NAME", "progress")
        
        if not self.connection_string:
            logger.warning("AZURE_STORAGE_CONNECTION_STRING not set; progress tracking disabled")
            self.client = None
            return
        
        try:
            self.client = TableClient.from_connection_string(
                conn_str=self.connection_string,
                table_name=self.table_name
            )
            logger.info("Azure Table Storage progress tracker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Table Storage: {e}")
            self.client = None

    def save_user_session(self, user_id: str, session_data: Dict) -> bool:
        """Save or update user session (skills, career goal, etc.)"""
        if not self.client:
            logger.warning("Table Storage not available; skipping save_user_session")
            return False
        
        try:
            timestamp = datetime.utcnow().isoformat()
            entity = {
                "PartitionKey": user_id,
                "RowKey": f"session_{timestamp}",
                "type": "session",
                "timestamp": timestamp,
                "skills": json.dumps(session_data.get("skills", [])),
                "career_goal": session_data.get("career_goal", ""),
                "experience_level": session_data.get("experience_level", ""),
                "current_role": session_data.get("current_role", ""),
            }
            self.client.upsert_entity(entity=entity)
            logger.info(f"Session saved for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def save_role_selection(self, user_id: str, role: Dict) -> bool:
        """Track when user selects a career role"""
        if not self.client:
            logger.warning("Table Storage not available; skipping save_role_selection")
            return False
        
        try:
            timestamp = datetime.utcnow().isoformat()
            entity = {
                "PartitionKey": user_id,
                "RowKey": f"role_{timestamp}",
                "type": "role_selection",
                "timestamp": timestamp,
                "role_name": role.get("role", ""),
                "summary": role.get("summary", ""),
                "required_skills": json.dumps(role.get("required_skills", [])),
                "missing_skills": json.dumps(role.get("missing_skills", [])),
            }
            self.client.upsert_entity(entity=entity)
            logger.info(f"Role selection recorded for user {user_id}: {role.get('role')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save role selection: {e}")
            return False

    def save_phase_progress(self, user_id: str, role_name: str, phase_number: int, progress: Dict) -> bool:
        """Track completion of a study phase"""
        if not self.client:
            logger.warning("Table Storage not available; skipping save_phase_progress")
            return False
        
        try:
            timestamp = datetime.utcnow().isoformat()
            entity = {
                "PartitionKey": user_id,
                "RowKey": f"phase_{role_name}_{phase_number}_{timestamp}",
                "type": "phase_progress",
                "timestamp": timestamp,
                "role_name": role_name,
                "phase_number": phase_number,
                "status": progress.get("status", "in_progress"),
                "completion_percentage": progress.get("completion_percentage", 0),
                "hours_spent": progress.get("hours_spent", 0),
                "skills_learned": json.dumps(progress.get("skills_learned", [])),
                "notes": progress.get("notes", ""),
            }
            self.client.upsert_entity(entity=entity)
            logger.info(f"Phase progress recorded for user {user_id}, role {role_name}, phase {phase_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to save phase progress: {e}")
            return False

    def save_skill_milestone(self, user_id: str, skill: str, milestone_data: Dict) -> bool:
        """Track when user completes a skill milestone"""
        if not self.client:
            logger.warning("Table Storage not available; skipping save_skill_milestone")
            return False
        
        try:
            timestamp = datetime.utcnow().isoformat()
            entity = {
                "PartitionKey": user_id,
                "RowKey": f"skill_{skill}_{timestamp}",
                "type": "skill_milestone",
                "timestamp": timestamp,
                "skill": skill,
                "proficiency_level": milestone_data.get("proficiency_level", "beginner"),
                "resources_used": json.dumps(milestone_data.get("resources_used", [])),
                "certification": milestone_data.get("certification", ""),
            }
            self.client.upsert_entity(entity=entity)
            logger.info(f"Skill milestone recorded for user {user_id}: {skill}")
            return True
        except Exception as e:
            logger.error(f"Failed to save skill milestone: {e}")
            return False

    def get_user_progress_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve user's progress history"""
        if not self.client:
            logger.warning("Table Storage not available; returning empty history")
            return []
        
        try:
            filter_str = f"PartitionKey eq '{user_id}'"
            items = list(self.client.query_entities(filter_str))
            # Sort by timestamp descending
            items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            items = items[:limit]
            
            # Parse JSON fields back
            for item in items:
                if "skills" in item and isinstance(item["skills"], str):
                    try:
                        item["skills"] = json.loads(item["skills"])
                    except:
                        item["skills"] = []
                if "required_skills" in item and isinstance(item["required_skills"], str):
                    try:
                        item["required_skills"] = json.loads(item["required_skills"])
                    except:
                        item["required_skills"] = []
                if "missing_skills" in item and isinstance(item["missing_skills"], str):
                    try:
                        item["missing_skills"] = json.loads(item["missing_skills"])
                    except:
                        item["missing_skills"] = []
                if "skills_learned" in item and isinstance(item["skills_learned"], str):
                    try:
                        item["skills_learned"] = json.loads(item["skills_learned"])
                    except:
                        item["skills_learned"] = []
                if "resources_used" in item and isinstance(item["resources_used"], str):
                    try:
                        item["resources_used"] = json.loads(item["resources_used"])
                    except:
                        item["resources_used"] = []
            
            logger.info(f"Retrieved {len(items)} progress records for user {user_id}")
            return items
        except Exception as e:
            logger.error(f"Failed to retrieve progress history: {e}")
            return []

    def get_user_stats(self, user_id: str) -> Dict:
        """Get aggregated statistics for user"""
        if not self.client:
            logger.warning("Table Storage not available; returning empty stats")
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
        """Check if Table Storage is available"""
        return self.client is not None


def get_progress_tracker() -> TableStorageProgressTracker:
    """Factory function to get progress tracker instance"""
    return TableStorageProgressTracker()
