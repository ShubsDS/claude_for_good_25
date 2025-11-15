from sqlmodel import SQLModel, create_engine

DB_FILE = "db.sqlite"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# echo=True will print SQL statements; you can set to False to reduce output
engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)
