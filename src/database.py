import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Event, Course

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/newsletter.db")
os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    # Seeding requirement (at least 5 records)
    if session.query(Event).count() == 0:
        events = [Event(name=f"Event {i}", description=f"Details for event {i}", event_date=datetime.now() + timedelta(days=i)) for i in range(1, 6)]
        session.add_all(events)
        
    if session.query(Course).count() == 0:
        courses = [Course(name=f"Course {i}", reminder=f"HW {i} due", due_date=datetime.now() + timedelta(days=i)) for i in range(1, 6)]
        session.add_all(courses)
        
    session.commit()
    session.close()