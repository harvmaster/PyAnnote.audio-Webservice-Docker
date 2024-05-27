import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import torchaudio
from pydantic import BaseModel
from pyannote.core import Annotation
from pyannote.audio import Pipeline
# import torch

# Load environment variables
HF_API_KEY = os.environ.get("HF_API_KEY")
ORIGINS = os.environ.get("ALLOW_ORIGINS", "*")

print(f"Using Hugging Face API key: {HF_API_KEY}")

# Check if API key is provided
if not HF_API_KEY:
    raise RuntimeError("Hugging Face API key not found in environment variables")

# Initialize pipeline
# torch.NumCudaDevices()
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# print(torch.cuda.get_device_name(device))
# print(f"Using device: {device}")
# print("CUDA Available:", torch.cuda.is_available())
try:
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HF_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to load pipeline: {e}")

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
    try:
        audio_data = audio_file.file.read()

        print(f"Received audio file: {audio_file.filename} with size: {len(audio_data)}")

        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
            tmp_audio_file.write(audio_data)
            tmp_audio_file_path = tmp_audio_file.name

        # Run diarization on the temporary audio file
        diarization = pipeline({'uri': 'temp_audio', 'audio': tmp_audio_file_path})
        annotation = diarization.get_timeline().to_annotation()

        speaker_data = []

        for segment, track, label in annotation.itertracks(yield_label=True):
            speaker_data.append(SpeakerInfo(speaker=label, start=segment.start, end=segment.end))

        # Delete the temporary file
        os.unlink(tmp_audio_file_path)

        return speaker_data

    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))