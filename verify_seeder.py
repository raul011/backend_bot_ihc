import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.conductor import Conductor
from app.db.seeder import seed_conductores

def verify():
    print("Running seeder...")
    seed_conductores()
    
    db = SessionLocal()
    try:
        conductores = db.query(Conductor).all()
        print(f"Found {len(conductores)} conductors:")
        for c in conductores:
            print(f"- {c.name} ({c.email})")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
