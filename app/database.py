from sqlalchemy import create_engine  # Importing create_engine function from SQLAlchemy to create a database engine
from sqlalchemy.ext.declarative import declarative_base  # Importing declarative_base function to create a base class for our models
from sqlalchemy.orm import sessionmaker  # Importing sessionmaker to create a configured Session class
import os  # Importing os module to access environment variables

# Getting the database URL from environment variables, with a fallback to a local SQLite database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Creating a database engine with the specified URL
# For SQLite, setting check_same_thread to False to allow usage in multiple threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creating a configured Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creating a base class for our models to inherit from
Base = declarative_base()

def init_db():
    # Importing all classes that extend Base here to ensure they are registered with SQLAlchemy
    from .models import PDFFile, PDFEmbedding
    # Creating all tables in the database that are defined by classes extending Base
    Base.metadata.create_all(bind=engine)
