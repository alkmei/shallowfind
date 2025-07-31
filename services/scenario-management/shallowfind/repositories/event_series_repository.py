import uuid
from sqlalchemy.orm import Session
from ..models import EventSeries

class EventSeriesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_series_id: uuid.UUID) -> EventSeries | None:
        return self.db.query(EventSeries).filter(EventSeries.id == event_series_id).first()

    def create(self, event_series_data):
        new_event_series = EventSeries(**event_series_data)
        self.db.add(new_event_series)
        self.db.commit()
        return new_event_series

    def update(self, event_series_id, event_series_data):
        event_series = self.get_by_id(event_series_id)
        if event_series:
            for key, value in event_series_data.items():
                setattr(event_series, key, value)
            self.db.commit()
            return event_series
        return None

    def delete(self, event_series_id):
        event_series = self.get_by_id(event_series_id)
        if event_series:
            self.db.delete(event_series)
            self.db.commit()
            return True
        return False