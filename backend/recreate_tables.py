#!/usr/bin/env python3
"""Recreate database tables with new schema."""
from app.db.database import engine, Base
from app.models.cfts_db import CFTSRequirementDB

def recreate_tables():
    """Drop and recreate all tables."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables recreated successfully!")

    # Print table schema
    print("\nTable schema:")
    for column in CFTSRequirementDB.__table__.columns:
        print(f"  - {column.name}: {column.type}")

if __name__ == "__main__":
    recreate_tables()
