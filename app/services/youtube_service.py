from fastapi import APIRouter, HTTPException  # Importing FastAPI components for routing and exception handling
import google.generativeai as genai  # Importing Google Generative AI library
import os  # Importing os module to access environment variables
from dotenv import load_dotenv  # Importing dotenv to load environment variables from a .env file
from youtube_transcript_api import YouTubeTranscriptApi  # Importing YouTubeTranscriptApi to fetch video transcripts
from ..schemas import VideoConvertRequest, VideoConvertResponse, Video  # Importing request and response schemas

load_dotenv()  # Loading environment variables from a .env file

router = APIRouter()  # Creating a new FastAPI router instance

# Configuring Google Generative AI with the API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract transcript from a YouTube video
def extract_transcript(youtube_video_url):
    try:
        # Extracting the video ID from the YouTube URL
        video_id = youtube_video_url.split("=")[-1]

        # Fetching the transcript using the YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combining the transcript text into a single string
        transcript_text = ""
        for i in transcript:
            transcript_text += " " + i["text"]

        return transcript_text  # Returning the combined transcript text
    except Exception as e:
        print(f"Error extracting transcript: {e}")  # Printing error message
        return None  # Returning None if an error occurs

# Function to generate notes from the transcript text
def generate_notes(transcript_text: str, subject: str) -> str:
    # Defining the prompt for generating notes
    prompt = f"""
        Title: Detailed Notes on {subject} from YouTube Video Transcript

        As an expert in {subject}, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

        Your notes should:

        - Analyze and explain the main ideas, theories, or concepts presented in the video.
        - Provide examples, illustrations, or case studies to support the understanding of the topic.
        - Offer insights or practical applications of the subject matter discussed.
        - Use clear language and concise explanations to facilitate learning.

        Please provide the notes based on the following transcript:

        {transcript_text}
    """

    # Initializing the generative model
    model = genai.GenerativeModel('gemini-pro')
    # Generating the content using the model
    response = model.generate_content(prompt)
    return response.text  # Returning the generated notes

@router.post("/convert_video/", response_model=VideoConvertResponse)
async def convert_video(request: VideoConvertRequest):
    try:
        # Extracting the video ID from the YouTube URL
        video_id = str(request.youtube_link).split("=")[-1]
        # Constructing the thumbnail URL
        thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"

        # Extracting the transcript text from the YouTube video
        transcript_text = extract_transcript(str(request.youtube_link))
        if not transcript_text:
            raise HTTPException(status_code=400, detail="Failed to extract transcript from the video")

        # Generating notes from the transcript text
        notes = generate_notes(transcript_text, request.subject)
        
        # Creating a Video object (typically you would save this to a database)
        video = Video(url=request.youtube_link, thumbnail_url=thumbnail_url, notes=notes)
        
        # Returning the generated notes in the response
        return VideoConvertResponse(notes=notes)
    except Exception as e:
        # Raising an HTTP exception if an error occurs
        raise HTTPException(status_code=500, detail=f"Failed to convert video: {str(e)}")
