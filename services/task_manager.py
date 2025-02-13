from datetime import datetime, timedelta, time
import uuid
from sqlalchemy.orm import Session
from models.database import Task, TaskStatus, TaskType, RecurrencePattern, get_db
from typing import List, Dict, Any

class TaskManager:
    def __init__(self):
        self.db = next(get_db())

    def add_task(self, title: str, date, priority: str, task_type: str,
                 is_fixed_time: bool = False, fixed_time: time = None,
                 flexible_start_time: time = None, flexible_end_time: time = None,
                 recurrence_pattern: str = "None", estimated_duration: int = None) -> None:
        new_task = Task(
            id=str(uuid.uuid4()),
            title=title,
            date=datetime.combine(date, datetime.min.time()),
            priority=priority,
            status=TaskStatus.NOT_STARTED,
            task_type=TaskType(task_type),
            is_fixed_time=is_fixed_time,
            fixed_time=fixed_time,
            flexible_start_time=flexible_start_time,
            flexible_end_time=flexible_end_time,
            recurrence_pattern=RecurrencePattern(recurrence_pattern),
            estimated_duration=estimated_duration
        )
        self.db.add(new_task)
        self.db.commit()

    def get_tasks(self, task_type: str = None) -> List[Dict[str, Any]]:
        query = self.db.query(Task)
        if task_type:
            query = query.filter(Task.task_type == TaskType(task_type))

        tasks = query.all()
        return [{
            'id': task.id,
            'title': task.title,
            'date': task.date.date().isoformat(),
            'priority': task.priority,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'task_type': task.task_type.value,
            'is_fixed_time': task.is_fixed_time,
            'fixed_time': task.fixed_time.strftime('%H:%M') if task.fixed_time else None,
            'flexible_start_time': task.flexible_start_time.strftime('%H:%M') if task.flexible_start_time else None,
            'flexible_end_time': task.flexible_end_time.strftime('%H:%M') if task.flexible_end_time else None,
            'recurrence_pattern': task.recurrence_pattern.value,
            'estimated_duration': task.estimated_duration
        } for task in tasks]

    def update_task_status(self, task_id: str, status: str) -> None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus(status)
            self.db.commit()

    def get_completion_stats(self, time_range: str) -> Dict[str, Any]:
        today = datetime.now()
        if time_range == "Last Week":
            start_date = today - timedelta(days=7)
        elif time_range == "Last Month":
            start_date = today - timedelta(days=30)
        else:  # Last 3 Months
            start_date = today - timedelta(days=90)

        tasks = self.db.query(Task).filter(Task.date >= start_date).all()

        # Calculate completion rates by priority
        priority_stats = {'High': {'total': 0, 'completed': 0},
                         'Medium': {'total': 0, 'completed': 0},
                         'Low': {'total': 0, 'completed': 0}}

        for task in tasks:
            priority_stats[task.priority]['total'] += 1
            if task.status == TaskStatus.COMPLETED:
                priority_stats[task.priority]['completed'] += 1

        # Calculate best performing days
        day_stats = {}
        for task in tasks:
            day = task.date.strftime('%A')
            if day not in day_stats:
                day_stats[day] = {'total': 0, 'completed': 0}
            day_stats[day]['total'] += 1
            if task.status == TaskStatus.COMPLETED:
                day_stats[day]['completed'] += 1

        return {
            'completed': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            'partial': len([t for t in tasks if t.status == TaskStatus.PARTIAL]),
            'not_started': len([t for t in tasks if t.status == TaskStatus.NOT_STARTED]),
            'priority_stats': priority_stats,
            'day_stats': day_stats,
            'tasks': [{
                'id': t.id,
                'title': t.title,
                'date': t.date.date().isoformat(),
                'priority': t.priority,
                'status': t.status.value,
                'created_at': t.created_at.isoformat(),
                'is_fixed_time': t.is_fixed_time,
                'fixed_time': t.fixed_time.strftime('%H:%M') if t.fixed_time else None,
                'flexible_start_time': t.flexible_start_time.strftime('%H:%M') if t.flexible_start_time else None,
                'flexible_end_time': t.flexible_end_time.strftime('%H:%M') if t.flexible_end_time else None
            } for t in tasks]
        }
    
    def delete_task(self, task_id: str):
        """Delete a task by its ID"""
        db = next(get_db())  # Get the database session
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return True
        return False