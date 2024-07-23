import io  # Importing io module for file handling
from typing import List  # Importing List from typing module for type hinting
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile  # Importing FastAPI components for routing, dependencies, file uploads, and exception handling
from sqlalchemy.orm import Session  # Importing Session for database operations
from PyPDF2 import PdfReader  # Importing PdfReader from PyPDF2 for reading PDF files
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing RecursiveCharacterTextSplitter for splitting text
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Importing GoogleGenerativeAIEmbeddings for generating embeddings
from langchain.prompts import PromptTemplate  # Importing PromptTemplate for creating prompt templates
from langchain.chains import LLMChain  # Importing LLMChain for creating language model chains
from langchain_google_genai import ChatGoogleGenerativeAI  # Importing ChatGoogleGenerativeAI for chat model
import os  # Importing os module to access environment variables
from pinecone import Pinecone  # Importing Pinecone for vector database
from dotenv import load_dotenv  # Importing dotenv to load environment variables from a .env file
from ..database import SessionLocal  # Importing SessionLocal for database session
from ..models import PDFFile, PDFEmbedding  # Importing PDFFile and PDFEmbedding models

router = APIRouter()  # Creating a new FastAPI router instance

load_dotenv()  # Loading environment variables from a .env file

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))  # Initializing Pinecone with API key from environment variable

def get_db():
    db = SessionLocal()  # Creating a new database session
    try:
        yield db  # Yielding the session for dependency injection
    finally:
        db.close()  # Closing the session when done

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    # Checking if the uploaded file is empty
    if pdf_file.file.read(1) == b'':
        raise ValueError("The uploaded file is empty")
    
    pdf_file.file.seek(0)  # Reset file pointer to the beginning
    pdf_bytes = io.BytesIO(pdf_file.file.read())  # Reading the file into a BytesIO stream
    pdf_reader = PdfReader(pdf_bytes)  # Creating a PdfReader object
    
    text = ""
    # Extracting text from each page of the PDF
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Raising an error if no text could be extracted
    if not text.strip():
        raise ValueError("No text could be extracted from the PDF")
    
    return text  # Returning the extracted text

def get_text_chunks(text: str) -> List[str]:
    # Creating a text splitter with specified chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000
    )
    return text_splitter.split_text(text)  # Splitting the text into chunks

def generate_embeddings(text_chunks: List[str]) -> List[List[float]]:
    # Initializing the embeddings model
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Generating embeddings for each text chunk
    return [embeddings_model.embed_query(chunk) for chunk in text_chunks]

def store_embeddings(db: Session, pdf_file_id: int, embeddings: List[List[float]]):
    # Storing each embedding in the database
    for embedding in embeddings:
        pdf_embedding = PDFEmbedding(pdf_file_id=pdf_file_id, embedding=str(embedding))
        db.add(pdf_embedding)
    db.commit()  # Committing the transaction to save embeddings

def get_vector_store(text_chunks: List[str], embeddings: List[List[float]]):
    index_name = "pdf-chatbot"  # Specifying the index name for Pinecone
    
    # Checking if the index already exists
    if index_name not in pc.list_indexes().names():
        # Creating a new index if it does not exist
        pc.create_index(
            name=index_name, 
            dimension=768,  # Adjust this based on your embedding dimension
            metric='cosine'
        )
    
    index = pc.Index(index_name)  # Getting the index
    
    # Upserting (inserting or updating) vectors into the index
    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        index.upsert(vectors=[{
            'id': f'vec{i}',
            'values': embedding,
            'metadata': {'text': chunk}
        }])
    
    return index  # Returning the index

def get_conversational_chain():
    # Defining the prompt template for generating conversational responses
    prompt_template = """
    Answer the question in detail as much as possible from the provided context, make sure to provide all the 
    details, if the answer is not in the provided context just say, "answer is not available in the context", do not
    provide the wrong answer\n\n
    Context:\n{context}?\n
    Question:\n{question}\n

    Answer:
    """
    
    # Initializing the chat model with specific parameters
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    # Creating a PromptTemplate with the defined template and input variables
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    # Returning an LLMChain with the chat model and prompt
    return LLMChain(llm=model, prompt=prompt)

def generate_answer(question: str, index: Pinecone) -> str:
    # Initializing the embeddings model
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Generating the embedding for the query
    query_embedding = embeddings_model.embed_query(question)
    
    # Querying the Pinecone index to get the top 5 matches
    response = index.query(vector=query_embedding, top_k=5, include_metadata=True)
    
    # Combining the context from the top matches
    context = " ".join([match['metadata']['text'] for match in response['matches']])
    
    # Getting the conversational chain
    chain = get_conversational_chain()
    # Running the chain with the context and question to generate an answer
    return chain.run(context=context, question=question)

@router.post("/ask_question/")
async def ask_question(pdf_file: UploadFile = File(...), question: str = "", db: Session = Depends(get_db)):
    try:
        pdf_name = pdf_file.filename  # Getting the filename of the uploaded PDF
        pdf_record = db.query(PDFFile).filter(PDFFile.name == pdf_name).first()  # Querying the database for the PDF record
        
        if pdf_record is None:
            # New PDF, process it
            text = extract_text_from_pdf(pdf_file)  # Extracting text from the PDF
            text_chunks = get_text_chunks(text)  # Splitting the text into chunks
            embeddings = generate_embeddings(text_chunks)  # Generating embeddings for the text chunks
            
            pdf_record = PDFFile(name=pdf_name, indexed=True)  # Creating a new PDFFile record
            db.add(pdf_record)  # Adding the record to the database
            db.flush()  # Flushing to assign an ID to the record
            
            store_embeddings(db, pdf_record.id, embeddings)  # Storing the embeddings in the database
            index = get_vector_store(text_chunks, embeddings)  # Creating/updating the vector store in Pinecone
        elif not pdf_record.indexed:
            # PDF exists but not indexed, process it
            text = extract_text_from_pdf(pdf_file)  # Extracting text from the PDF
            text_chunks = get_text_chunks(text)  # Splitting the text into chunks
            embeddings = generate_embeddings(text_chunks)  # Generating embeddings for the text chunks
            
            pdf_record.indexed = True  # Marking the PDF as indexed
            store_embeddings(db, pdf_record.id, embeddings)  # Storing the embeddings in the database
            index = get_vector_store(text_chunks, embeddings)  # Creating/updating the vector store in Pinecone
        else:
            # PDF exists and is indexed, fetch existing embeddings
            embeddings = [eval(e.embedding) for e in pdf_record.embeddings]  # Fetching existing embeddings from the database
            index = get_vector_store([], embeddings)  # Creating/updating the vector store in Pinecone
        
        response = generate_answer(question, index)  # Generating an answer to the question
        return {"response": response}  # Returning the response
    
    except ValueError as ve:
        # Raising an HTTP exception for value errors
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Raising an HTTP exception for other errors
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")