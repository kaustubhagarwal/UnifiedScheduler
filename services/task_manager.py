import json
import datetime
import uuid
from pathlib import Path

class TaskManager:
    def __init__(self):
        self.tasks_file = Path("data/tasks.json")
        self._initialize_storage()
    
    def _initialize_storage(self):
        if not self.tasks_file.parent.exists():
            self.tasks_file.parent.mkdir(parents=True)
        if not self.tasks_file.exists():
            self._save_tasks([])
    
    def _load_tasks(self):
        try:
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_tasks(self, tasks):
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f)
    
    def add_task(self, title, date, priority):
        tasks = self._load_tasks()
        new_task = {
            'id': str(uuid.uuid4()),
            'title': title,
            'date': date.isoformat(),
            'priority': priority,
            'status': 'Not Started',
            'created_at': datetime.datetime.now().isoformat()
        }
        tasks.append(new_task)
        self._save_tasks(tasks)
    
    def get_tasks(self):
        return self._load_tasks()
    
    def update_task_status(self, task_id, status):
        tasks = self._load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = status
                break
        self._save_tasks(tasks)
    
    def get_completion_stats(self, time_range):
        tasks = self._load_tasks()
        today = datetime.date.today()
        
        if time_range == "Last Week":
            start_date = today - datetime.timedelta(days=7)
        elif time_range == "Last Month":
            start_date = today - datetime.timedelta(days=30)
        else:  # Last 3 Months
            start_date = today - datetime.timedelta(days=90)
        
        filtered_tasks = [
            task for task in tasks
            if datetime.date.fromisoformat(task['date']) >= start_date
        ]
        
        return {
            'completed': len([t for t in filtered_tasks if t['status'] == 'Completed']),
            'partial': len([t for t in filtered_tasks if t['status'] == 'Partial']),
            'not_started': len([t for t in filtered_tasks if t['status'] == 'Not Started']),
            'tasks': filtered_tasks
        }
