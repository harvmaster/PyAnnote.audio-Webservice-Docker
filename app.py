import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pyannote.core import Segment, Annotation
from pyannote.audio import Pipeline

HF_API_KEY = os.environ.get("HF_API_KEY")
ORIGINS = os.environ.get("ALLOW_ORIGINS")

pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=HF_API_KEY)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class SpeakerInfo(BaseModel):
    speaker: str
    start: float
    end: float

@app.post("/diarize/")
async def get_speaker_data(audio_file: UploadFile = File(...)):
    audio_data = audio_file.file

    diarization = pipeline({"uri": audio_file.filename, "audio": audio_data})
    annotation = diarization.get_timeline().to_annotation()
    speaker_data = []

    for segment in annotation.itersegments():
        speaker_data.append(SpeakerInfo(speaker=segment[2], start=segment[0], end=segment[1]))

    return speaker_data

