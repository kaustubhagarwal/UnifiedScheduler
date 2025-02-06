import datetime

class AppleCalendarService:
    def __init__(self):
        # Mock implementation
        pass
    
    def get_events(self, date):
        # Mock implementation - in reality, this would integrate with Apple Calendar
        return [
            {
                'title': 'Lunch with Client',
                'start_time': '12:00',
                'duration': '1 hour',
                'source': 'Apple Calendar'
            },
            {
                'title': 'Team Meeting',  # Duplicate event for testing
                'start_time': '09:00',
                'duration': '1 hour',
                'source': 'Apple Calendar'
            }
        ]
