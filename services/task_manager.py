from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from models.database import Task, TaskStatus, get_db
from typing import List, Dict, Any

class TaskManager:
    def __init__(self):
        self.db = next(get_db())

    def add_task(self, title: str, date, priority: str) -> None:
        new_task = Task(
            id=str(uuid.uuid4()),
            title=title,
            date=datetime.combine(date, datetime.min.time()),
            priority=priority,
            status=TaskStatus.NOT_STARTED
        )
        self.db.add(new_task)
        self.db.commit()

    def get_tasks(self) -> List[Dict[str, Any]]:
        tasks = self.db.query(Task).all()
        return [{
            'id': task.id,
            'title': task.title,
            'date': task.date.date().isoformat(),
            'priority': task.priority,
            'status': task.status.value,
            'created_at': task.created_at.isoformat()
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

        return {
            'completed': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            'partial': len([t for t in tasks if t.status == TaskStatus.PARTIAL]),
            'not_started': len([t for t in tasks if t.status == TaskStatus.NOT_STARTED]),
            'tasks': [{
                'id': t.id,
                'title': t.title,
                'date': t.date.date().isoformat(),
                'priority': t.priority,
                'status': t.status.value,
                'created_at': t.created_at.isoformat()
            } for t in tasks]
        }