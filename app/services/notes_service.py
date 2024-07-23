from fastapi import APIRouter, HTTPException  # Importing APIRouter and HTTPException from FastAPI for routing and error handling
from langchain.prompts import PromptTemplate  # Importing PromptTemplate from LangChain for generating prompts
from langchain_google_genai import ChatGoogleGenerativeAI  # Importing ChatGoogleGenerativeAI for generating AI-based responses
from langchain.schema.runnable import RunnableSequence  # Importing RunnableSequence to create a sequence of operations
from langchain.schema import StrOutputParser  # Importing StrOutputParser to parse the string output
from ..schemas import NoteRequest, NoteResponse  # Importing NoteRequest and NoteResponse schemas from the parent directory

router = APIRouter()  # Creating a new FastAPI router instance

def get_notes_generation_chain():
    # Defining the prompt template for generating notes
    prompt_template = """
    Generate detailed notes on the given topic. Use headings, subheadings, and bullet points to organize the information.
    Make sure to cover key concepts, important details, and any relevant examples or applications.

    Topic: {topic}

    Please structure your notes as follows:
    1. Start with a brief introduction to the topic.
    2. Use main headings (##) for major sections.
    3. Use subheadings (###) for subsections.
    4. Use bullet points (-) for listing details, examples, or key points.
    5. Conclude with a summary of the main points.

    Notes:
    """

    # Initializing the Google Generative AI model with specific parameters
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.3)
    # Creating a PromptTemplate with the defined template and input variable
    prompt = PromptTemplate(template=prompt_template, input_variables=["topic"])
    
    # Creating a RunnableSequence with the prompt, model, and output parser
    chain = RunnableSequence(
        prompt | model | StrOutputParser()
    )
    return chain  # Returning the created chain

def generate_notes(topic: str) -> str:
    chain = get_notes_generation_chain()  # Getting the notes generation chain
    return chain.invoke({"topic": topic})  # Invoking the chain with the provided topic and returning the generated notes

@router.post("/generate_notes/", response_model=NoteResponse)  # Defining a POST endpoint for generating notes
async def create_notes(note_request: NoteRequest):
    try:
        notes_content = generate_notes(note_request.topic)  # Generating notes for the requested topic
        return NoteResponse(topic=note_request.topic, content=notes_content)  # Returning the notes response
    except Exception as e:
        # Raising an HTTP exception in case of an error
        raise HTTPException(status_code=500, detail=f"Failed to generate notes: {str(e)}")
