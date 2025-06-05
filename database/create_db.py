import os
import sys

print("Current working directory:", os.getcwd())
print("sys.path:", sys.path)

from database.database import engine, Base
from database import models # Импортируем все модели, чтобы они были известны Base.metadata

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.") 