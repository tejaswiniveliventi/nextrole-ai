# Placeholder for tracking user progress in future persistence layer
class ProgressRepository:
    def __init__(self):
        self.data = {}

    def save_progress(self, user_id, role_info, completed_weeks):
        self.data[user_id] = {"role": role_info, "completed_weeks": completed_weeks}

    def get_progress(self, user_id):
        return self.data.get(user_id, None)
