import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class AIPrioritization:
    def __init__(self):
        self.priority_weights = {
            'High': 1.0,
            'Medium': 0.7,
            'Low': 0.4
        }
        
    def calculate_task_score(self, task: Dict[str, Any], current_time: datetime) -> float:
        """Calculate a priority score for a task based on multiple factors"""
        # Base score from priority
        score = self.priority_weights.get(task['priority'], 0.5) * 100
        
        # Time factor
        task_date = datetime.fromisoformat(task['date'])
        days_until_due = (task_date.date() - current_time.date()).days
        
        # Urgency factor (higher score for tasks due sooner)
        if days_until_due <= 0:
            urgency_score = 100  # Due today or overdue
        else:
            urgency_score = max(0, 100 - (days_until_due * 10))
        
        # Duration factor (shorter tasks get slight priority)
        duration_score = 100 - min(100, task['estimated_duration'] / 15)
        
        # Combine scores with weights
        final_score = (
            score * 0.4 +          # Priority weight
            urgency_score * 0.4 +  # Urgency weight
            duration_score * 0.2    # Duration weight
        )
        
        return final_score

    def suggest_task_time(self, task: Dict[str, Any], busy_times: List[Dict[str, Any]]) -> str:
        """Suggest optimal time for a flexible task"""
        if task['is_fixed_time']:
            return task['fixed_time']
            
        # Convert busy times to blocked periods
        blocked_periods = []
        for busy in busy_times:
            start = datetime.strptime(busy['start_time'], '%H:%M').time()
            end = (datetime.strptime(busy['start_time'], '%H:%M') + 
                  timedelta(minutes=int(busy['duration'].split()[0]))).time()
            blocked_periods.append((start, end))
            
        # Find available time slots
        available_slots = self._find_available_slots(
            blocked_periods,
            task['flexible_start_time'],
            task['flexible_end_time'],
            int(task['estimated_duration'])
        )
        
        if not available_slots:
            return None
            
        # Return the best slot (currently just the first available)
        return available_slots[0].strftime('%H:%M')
        
    def _find_available_slots(self, blocked_periods, start_time, end_time, duration):
        """Find available time slots between blocked periods"""
        # Convert times to datetime for easier manipulation
        base_date = datetime.today()
        start_dt = datetime.combine(base_date, datetime.strptime(start_time, '%H:%M').time())
        end_dt = datetime.combine(base_date, datetime.strptime(end_time, '%H:%M').time())
        
        # Sort blocked periods
        blocked_periods.sort(key=lambda x: x[0])
        
        available_slots = []
        current_time = start_dt
        
        for block_start, block_end in blocked_periods:
            block_start_dt = datetime.combine(base_date, block_start)
            block_end_dt = datetime.combine(base_date, block_end)
            
            # Check if there's enough time before the blocked period
            if (block_start_dt - current_time).total_seconds() / 60 >= duration:
                available_slots.append(current_time.time())
                
            current_time = block_end_dt
            
        # Check final period
        if (end_dt - current_time).total_seconds() / 60 >= duration:
            available_slots.append(current_time.time())
            
        return available_slots
