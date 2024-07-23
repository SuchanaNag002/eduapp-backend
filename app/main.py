from dotenv import load_dotenv
from fastapi import FastAPI
from .services import pdf_service, questionnaire_service, youtube_service, notes_service
from app.database import init_db

# Load environment variables from a .env file
load_dotenv()

# Initialize the database by creating the necessary tables
init_db()

# Initialize the FastAPI application
app = FastAPI(
    title="PDF Q&A API",  # Title of the application
    description="API for asking questions about PDF documents"  # Description of the application
)

# Include the router for PDF querying functionality
app.include_router(
    pdf_service.router,  # The router instance from pdf_service
    prefix="/pdf",  # URL prefix for all routes in this router
    tags=["pdf querying"]  # Tags for categorizing the routes in documentation
)

# Include the router for MCQ (Multiple Choice Question) generation functionality
app.include_router(
    questionnaire_service.router,  # The router instance from questionnaire_service
    prefix="/mcq",  # URL prefix for all routes in this router
    tags=["mcq generation"]  # Tags for categorizing the routes in documentation
)

# Include the router for generating notes from YouTube videos
app.include_router(
    youtube_service.router,  # The router instance from youtube_service
    prefix="/yt",  # URL prefix for all routes in this router
    tags=["youtube notes"]  # Tags for categorizing the routes in documentation
)

# Include the router for generating notes from input topics
app.include_router(
    notes_service.router,  # The router instance from notes_service
    prefix="/note",  # URL prefix for all routes in this router
    tags=["note generation"]  # Tags for categorizing the routes in documentation
)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application with Uvicorn as the ASGI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
