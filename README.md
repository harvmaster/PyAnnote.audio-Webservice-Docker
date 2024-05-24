# PyAnnote.audio Docker Webservice
A easy to setup web api for PyAnnote.audio for docker made in python.

Get your Hugging Face API key [here](https://huggingface.co/settings/tokens)

## Docker-compose
```yml
version: "3.3"

services:
    whisper_pyannote:
        image: harvmaster/pyannote-api:latest
        container_name: "pyannote-api"
        environment: 
            - ALLOW_ORIGINS=*
            - HF_API_KEY= // Use your Hugging Face API key, per above
        ports:
            - 9000:9000
```

## Routes
```
POST /diarize

BODY {
    audio_file: File
}
```
