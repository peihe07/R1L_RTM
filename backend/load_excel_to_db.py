#!/usr/bin/env python3
"""Load Excel data into database."""
import json
import sys
import os

from app.db.database import engine, SessionLocal, Base
from app.db.crud import bulk_create_cfts_requirements
from app.models.requirement import CFTSRequirement
from app.models.cfts_db import CFTSRequirementDB


def load_data_to_database():
    """Load extracted Excel data into database."""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Load JSON data (check multiple possible paths)
        possible_paths = [
            "/app/extracted_data_md_scope.json",  # Docker path (MD Scope filtered)
            "extracted_data_md_scope.json",       # Local path (MD Scope filtered)
            "../extracted_data_md_scope.json",    # Parent directory (MD Scope filtered)
            "/app/extracted_data.json",           # Fallback Docker path
            "extracted_data.json",                # Fallback local path
            "../extracted_data.json"              # Fallback parent directory
        ]
        
        data = None
        for json_path in possible_paths:
            try:
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"Loaded data from: {json_path}")
                    break
            except Exception as e:
                print(f"Failed to load from {json_path}: {e}")
                continue
        
        if not data:
            raise FileNotFoundError("Could not find extracted_data.json in any expected location")
        
        print(f"Loaded {len(data)} records from JSON")
        
        # Convert to Pydantic models
        requirements = [CFTSRequirement(**item) for item in data]
        
        # Create database session
        db = SessionLocal()
        try:
            # Bulk insert
            count = bulk_create_cfts_requirements(db, requirements)
            print(f"Successfully inserted {count} CFTS requirements into database")
            
            # Verify insertion
            total_records = db.query(CFTSRequirementDB).count()
            print(f"Total records in database: {total_records}")
            
        finally:
            db.close()
            
        print("Data loading completed successfully!")
        
    except Exception as e:
        print(f"Error loading data to database: {e}")
        raise


if __name__ == "__main__":
    load_data_to_database()