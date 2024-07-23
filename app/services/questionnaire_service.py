from fastapi import APIRouter, HTTPException  # Importing FastAPI components for routing and exception handling
from langchain_google_genai import ChatGoogleGenerativeAI  # Importing Google Generative AI library
from langchain.prompts import PromptTemplate  # Importing PromptTemplate to format prompts
import json  # Importing json module to handle JSON data
import os  # Importing os module to access environment variables
import logging  # Importing logging module to enable logging
import re  # Importing re module for regex operations
from dotenv import load_dotenv  # Importing dotenv to load environment variables from a .env file
from ..schemas import MCQQuestion, MCQRequest, MCQResponse  # Importing request and response schemas

load_dotenv()  # Loading environment variables from a .env file

router = APIRouter()  # Creating a new FastAPI router instance
logging.basicConfig(level=logging.INFO)  # Setting the logging level to INFO
logger = logging.getLogger(__name__)  # Creating a logger instance

# Function to get the language model
def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get the prompt template for generating MCQs
def get_mcq_prompt():
    return PromptTemplate(
        template="""
        Generate a multiple-choice questionnaire on the topic: {topic}
        Number of questions: {num_questions}

        Format the response as a valid JSON array of objects. Each object should have these properties:
        - QuestionNumber: integer (starting from 1)
        - Question: string (max 50 characters)
        - A, B, C, D: string (each max 50 characters)
        - CorrectAnswer: string (A, B, C, or D)
        - Explanation: string (max 200 characters)

        Ensure the entire response is a valid JSON array that can be parsed by JSON.parse().
        Do not include any text before or after the JSON array.
        Do not wrap the JSON in code block formatting (i.e., do not use ```json or ```).
        """,
        input_variables=["topic", "num_questions"]
    )

# Function to generate MCQs using the language model
def generate_mcqs(topic: str, num_questions: int) -> list[MCQQuestion]:
    llm = get_llm()
    prompt = get_mcq_prompt()
    
    try:
        # Generating text from the language model using the formatted prompt
        generated_text = llm.invoke(prompt.format(topic=topic, num_questions=num_questions)).content.strip()
        logger.info(f"Generated text: {generated_text}")
        
        # Remove ```json and ``` if present
        cleaned_text = re.sub(r'^```json\n|\n```$', '', generated_text, flags=re.MULTILINE)
        
        # Parse the cleaned text as JSON
        mcq_data = json.loads(cleaned_text)
        return [MCQQuestion(**question) for question in mcq_data]
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Cleaned text: {cleaned_text}")
        raise ValueError(f"Failed to parse generated MCQs: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

# API endpoint to generate MCQs
@router.post("/generate_mcqs/", response_model=MCQResponse)
async def generate_questionnaire(request: MCQRequest):
    try:
        # Generating questions using the topic and number of questions from the request
        questions = generate_mcqs(request.topic, request.num_questions)
        return MCQResponse(questions=questions)
    except ValueError as ve:
        logger.error(f"ValueError in generate_questionnaire: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in generate_questionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate MCQs: {str(e)}")
