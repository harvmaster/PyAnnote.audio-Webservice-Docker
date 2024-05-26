import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import torchaudio
from pydantic import BaseModel
from pyannote.core import Annotation
from pyannote.audio import Pipeline

HF_API_KEY = os.environ.get("HF_API_KEY")
ORIGINS = os.environ.get("ALLOW_ORIGINS")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HF_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
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
    audio_data = audio_file.file.read()

    print(f"Received audio file: {audio_file.filename} with size: {len(audio_data)}")

    # Save audio data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
        tmp_audio_file.write(audio_data)

    # Load the temporary file using torchaudio
    waveform, sample_rate = torchaudio.load(tmp_audio_file.name)
    
    # Run diarization on the loaded waveform
    diarization = pipeline({'audio': waveform, 'sample_rate': sample_rate})
    annotation = diarization.get_timeline().to_annotation()
    
    speaker_data = []

    for segment in annotation.itersegments():
        speaker_data.append(SpeakerInfo(speaker=segment[2], start=segment[0], end=segment[1]))

    # Delete the temporary file
    os.unlink(tmp_audio_file.name)

    return speaker_data
