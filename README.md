
---
# GPTUTOR API

## Description

The **GPTUTOR API** is a FastAPI-based application designed to provide functionality for querying PDF documents, generating multiple-choice questions (MCQs), extracting and converting YouTube video transcripts into notes, and generating notes based on input topics. This application leverages various AI models and libraries to deliver comprehensive and interactive features.

## Features

- **PDF Querying**: Extract text from PDFs, generate embeddings, and use them for querying.
- **MCQ Generation**: Generate multiple-choice questions on a given topic using an AI model.
- **YouTube Notes**: Convert YouTube video transcripts into detailed notes.
- **Topic-Based Notes**: Generate notes based on user-provided topics.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- SQLAlchemy
- PyPDF2
- Langchain
- Google Generative AI
- Pinecone
- YouTube Transcript API
- Dotenv

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/eduapp-backend.git
   cd pdf-qa-api
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project and add the following variables:

   ```env
   GOOGLE_API_KEY=your_google_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```

## Usage

1. **Run the Application**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000/docs`.

2. **API Endpoints**

   ### PDF Querying

   - **Upload PDF and Ask a Question**
     - **Endpoint**: `/pdf/ask_question/`
     - **Method**: POST
     - **Description**: Upload a PDF and ask a question about its content.
     - **Request**: `multipart/form-data` with `pdf_file` and `question` fields.
     - **Response**: JSON object containing the answer to the question.

   ### MCQ Generation

   - **Generate MCQs**
     - **Endpoint**: `/mcq/generate_mcqs/`
     - **Method**: POST
     - **Description**: Generate a set of multiple-choice questions based on a topic.
     - **Request**: JSON object with `topic` and `num_questions`.
     - **Response**: JSON object containing the list of MCQs.

   ### YouTube Notes

   - **Convert YouTube Video to Notes**
     - **Endpoint**: `/yt/convert_video/`
     - **Method**: POST
     - **Description**: Convert a YouTube video transcript into detailed notes.
     - **Request**: JSON object with `youtube_link` and `subject`.
     - **Response**: JSON object containing the generated notes.

   ### Topic-Based Notes

   - **Generate Notes**
     - **Endpoint**: `/note/generate_notes/`
     - **Method**: POST
     - **Description**: Generate notes based on a given topic.
     - **Request**: JSON object with `topic`.
     - **Response**: JSON object containing the generated notes.

## Configuration

- **Database**: The application uses SQLite by default. Update the `DATABASE_URL` in the `.env` file if using a different database.
- **API Keys**: Ensure you have valid API keys for Google Generative AI and Pinecone.

## Project Structure

```
root/
│
├── app/
│   ├── database.py        # Database setup and initialization
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLAlchemy models
│   └── services/
│       ├── pdf_service.py # PDF querying service
│       ├── questionnaire_service.py # MCQ generation service
│       ├── youtube_service.py # YouTube notes service
│       └── notes_service.py # Topic-based notes service
│
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Explanation:

- **Description**: Provides a summary of the project's purpose and features.
- **Requirements**: Lists the necessary packages and Python version.
- **Installation**: Instructions on how to set up the project locally.
- **Usage**: How to run the application and details about API endpoints.
- **Configuration**: Additional setup details for database and API keys.
- **Project Structure**: Overview of the project's directory layout.
- **Contributing**: Information on how to contribute to the project.
- **License**: Specifies the project's licensing terms.

---