from sqlalchemy import Column, ForeignKey, Integer, String, Boolean  # Importing necessary column types and ForeignKey from SQLAlchemy
from sqlalchemy.orm import relationship  # Importing relationship to define relationships between models
from .database import Base  # Importing the Base class from the database module

class PDFFile(Base):  # Defining a PDFFile model extending the Base class
    __tablename__ = "pdf_files"  # Specifying the table name in the database
    id = Column(Integer, primary_key=True, index=True)  # Defining the primary key column with an index
    name = Column(String, unique=True, index=True)  # Defining a unique name column with an index
    indexed = Column(Boolean, default=False)  # Defining a boolean column with a default value of False
    embeddings = relationship("PDFEmbedding", back_populates="pdf_file")  # Defining a relationship to PDFEmbedding model

class PDFEmbedding(Base):  # Defining a PDFEmbedding model extending the Base class
    __tablename__ = "pdf_embeddings"  # Specifying the table name in the database
    id = Column(Integer, primary_key=True, index=True)  # Defining the primary key column with an index
    embedding = Column(String)  # Defining a column to store embeddings as a JSON string
    pdf_file_id = Column(Integer, ForeignKey("pdf_files.id"))  # Defining a foreign key column referencing the pdf_files table
    pdf_file = relationship("PDFFile", back_populates="embeddings")  # Defining a relationship to the PDFFile model
