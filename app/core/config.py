import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://delvauxo:yolo@postgres:5432/yolo")

settings = Settings()
