from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os

class GamificationService:
    def __init__(self):
        self.points_system = {
            'TaskStatus': {
                'COMPLETED': 100,
                'PARTIAL': 50,
            },
            'Priority': {
                'High': 50,
                'Medium': 30,
                'Low': 20
            },
            'Streak': {
                'daily': 50,
                'weekly': 200
            }
        }
        
        self.achievements = {
            'task_master': {
                'name': 'Task Master',
                'description': 'Complete 10 tasks in a day',
                'requirement': 10,
                'points': 500
            },
            'early_bird': {
                'name': 'Early Bird',
                'description': 'Complete 5 tasks before 10 AM',
                'requirement': 5,
                'points': 300
            },
            'priority_handler': {
                'name': 'Priority Handler',
                'description': 'Complete 5 high-priority tasks in a row',
                'requirement': 5,
                'points': 400
            }
        }
        
    def calculate_points(self, task: Dict[str, Any], status: str) -> int:
        """Calculate points for a task completion"""
        points = 0
        
        # Base points for task status
        points += self.points_system['TaskStatus'].get(status, 0)
        
        # Priority bonus
        points += self.points_system['Priority'].get(task['priority'], 0)
        
        # Early completion bonus (if completed before due date)
        if status == 'COMPLETED':
            task_date = datetime.fromisoformat(task['date'])
            if datetime.now().date() < task_date.date():
                points += 50  # Early completion bonus
                
        return points
        
    def update_streak(self, user_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's streak information"""
        today = datetime.now().date()
        last_active = datetime.fromisoformat(user_stats.get('last_active', 
                                           today.isoformat())).date()
        
        # Update daily streak
        if (today - last_active).days <= 1:
            user_stats['daily_streak'] = user_stats.get('daily_streak', 0) + 1
            user_stats['points'] = user_stats.get('points', 0) + self.points_system['Streak']['daily']
        else:
            user_stats['daily_streak'] = 1
            
        # Update weekly streak
        current_week = today.isocalendar()[1]
        last_week = last_active.isocalendar()[1]
        if current_week - last_week <= 1:
            user_stats['weekly_streak'] = user_stats.get('weekly_streak', 0) + 1
            user_stats['points'] = user_stats.get('points', 0) + self.points_system['Streak']['weekly']
        else:
            user_stats['weekly_streak'] = 1
            
        user_stats['last_active'] = today.isoformat()
        return user_stats
        
    def check_achievements(self, user_stats: Dict[str, Any], 
                         completed_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check and return newly unlocked achievements"""
        new_achievements = []
        today_tasks = [t for t in completed_tasks 
                      if datetime.fromisoformat(t['date']).date() == datetime.now().date()]
        
        # Check Task Master achievement
        if len(today_tasks) >= self.achievements['task_master']['requirement']:
            if 'task_master' not in user_stats.get('achievements', []):
                new_achievements.append(self.achievements['task_master'])
                
        # Check Early Bird achievement
        early_tasks = [t for t in today_tasks 
                      if datetime.strptime(t['fixed_time'], '%H:%M').hour < 10 
                      if t.get('fixed_time')]
        if len(early_tasks) >= self.achievements['early_bird']['requirement']:
            if 'early_bird' not in user_stats.get('achievements', []):
                new_achievements.append(self.achievements['early_bird'])
                
        # Check Priority Handler achievement
        high_priority_streak = sum(1 for t in completed_tasks[-5:] 
                                 if t['priority'] == 'High' 
                                 and t['status'] == 'COMPLETED')
        if high_priority_streak >= self.achievements['priority_handler']['requirement']:
            if 'priority_handler' not in user_stats.get('achievements', []):
                new_achievements.append(self.achievements['priority_handler'])
                
        return new_achievements
