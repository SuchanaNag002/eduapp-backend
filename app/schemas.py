from pydantic import BaseModel, HttpUrl  # Importing BaseModel and HttpUrl from pydantic library for data validation
from typing import List, Optional  # Importing List and Optional from typing module for type hinting

class MCQQuestion(BaseModel):  # Defining a Pydantic model for multiple choice questions
    QuestionNumber: int  # An integer representing the question number
    Question: str  # A string containing the question text
    A: str  # A string containing the text for option A
    B: str  # A string containing the text for option B
    C: str  # A string containing the text for option C
    D: str  # A string containing the text for option D
    CorrectAnswer: str  # A string indicating the correct answer
    Explanation: str  # A string providing an explanation for the correct answer

class MCQRequest(BaseModel):  # Defining a Pydantic model for MCQ request data
    topic: str  # A string specifying the topic of the questions
    num_questions: Optional[int] = 10  # An optional integer specifying the number of questions, default is 10

class MCQResponse(BaseModel):  # Defining a Pydantic model for MCQ response data
    questions: List[MCQQuestion]  # A list of MCQQuestion objects

class Video(BaseModel):  # Defining a Pydantic model for video data
    url: HttpUrl  # A URL field for the video URL
    thumbnail_url: HttpUrl  # A URL field for the thumbnail URL
    notes: str  # A string containing notes related to the video

class VideoConvertRequest(BaseModel):  # Defining a Pydantic model for video conversion request data
    youtube_link: HttpUrl  # A URL field for the YouTube link
    subject: str  # A string specifying the subject of the video

class VideoConvertResponse(BaseModel):  # Defining a Pydantic model for video conversion response data
    notes: str  # A string containing notes generated from the video

class NoteRequest(BaseModel):  # Defining a Pydantic model for note request data
    topic: str  # A string specifying the topic of the notes

class NoteResponse(BaseModel):  # Defining a Pydantic model for note response data
    topic: str  # A string specifying the topic of the notes
    content: str  # A string containing the content of the notes
