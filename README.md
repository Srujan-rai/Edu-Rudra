# Edu-Rudra

Edu-Rudra is a Flask-based web application that allows users to upload video files, extract audio from the videos, transcribe the audio, translate and summarize the transcriptions, and perform text-to-speech operations

## Features

- Upload video files and extract audio
- Transcribe audio to text
- Translate transcriptions to different languages
- Summarize transcriptions using Google Gemini AI
- Search for specific words within transcriptions and get timestamps
- Live text-to-speech functionality

## Prerequisites

- Python 3.x
- Flask
- moviepy
- speech_recognition
- pydub
- googletrans
- google.generativeai
- concurrent.futures
- secrets

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Srujan-rai/edu-rudra.git
    cd edu-rudra
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up your Google Generative AI API key:
    - Replace `YOUR_GOOGLE_GENERATIVE_AI_API_KEY` in the `API_KEY` variable in the `app.py` file with your actual API key.

4. Run the application:
    ```sh
    python app.py
    ```

## Usage

1. Navigate to `http://localhost:5000` in your web browser.
2. Upload a video file in the allowed format (.mp4).
3. Extract audio and transcribe it.
4. Translate the transcription to your desired language.
5. Summarize the transcription.
6. Search for specific words within the transcription.
7. Use the live text-to-speech functionality.

## File Structure
Sure! Below is the file structure in markdown format.

```
Edu-Rudra/
├── templates/
│   ├── index.html
│   ├── upload.html
│   ├── transcription.html
│   ├── speech_2_text.html
├── uploads/
│   ├── (uploaded files)
├── app.py
├── requirements.txt
└── README.md
```


## Routes

- `/`: Home page.
- `/upload`: Upload a video file.
- `/translate`: Translate transcription.
- `/summarize`: Summarize transcription.
- `/search`: Search within transcription.
- `/live_text_to_speech`: Live text-to-speech page.

## API Endpoints

- `POST /upload`: Uploads a video file and extracts audio for transcription.
- `POST /translate`: Translates the transcribed text to the selected language.
- `POST /summarize`: Summarizes the transcribed text.
- `POST /search`: Searches for a specific word in the transcribed text and returns timestamps.

## License

This project is licensed under the MIT License.


