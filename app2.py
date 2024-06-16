from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
import googletrans

API_KEY = 'AIzaSyC8kopd_HFCYwAjsBx6ta88OnAuOno2KYo'

genai.configure(api_key=API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
chat_session = model.start_chat(history=[])


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

translator = googletrans.Translator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(chunk_filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(chunk_filename) as source:
        audio_listened = recognizer.record(source)
        text = recognizer.recognize_google(audio_listened)
    return text

def process_chunk(chunk_filename):
    try:
        text = transcribe_audio(chunk_filename)
    except sr.UnknownValueError as e:
        print(f"Error in {chunk_filename}: {str(e)}")
        text = ""
    return f"{text.capitalize()}. "

def get_large_audio_transcription_on_silence(path):
    sound = AudioSegment.from_file(path)

    # Adjust silence detection parameters
    chunks = split_on_silence(
        sound,
        min_silence_len=500,   
        silence_thresh=sound.dBFS - 14, 
        keep_silence=500,
    )

    folder_name = "audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    
    chunk_filenames = []
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        chunk_filenames.append(chunk_filename)

    # Process chunks concurrently
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_chunk, chunk_filenames))
    
    whole_text = "".join(results)
    return whole_text

def summarize_text_with_gemini(text, language):
    response = chat_session.send_message(f"give me the summary of {text} in {language}")
    candidates = response.candidates
    
    text_parts = []
    cleaned_text_parts = []

    for candidate in candidates:
        content = candidate.content
        
        for part in content.parts:
            text = part.text
            cleaned_text = text.replace('\n', ' ').replace('[', '').replace(']', '').replace('**', '').strip('"')
            cleaned_text_parts.append(cleaned_text)
            print(text_parts)
    
    return cleaned_text_parts

def translate_text(text, target_language):
    return translator.translate(text, dest=target_language).text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
            file.save(video_path)
            extract_audio(video_path, audio_path)
            transcription = get_large_audio_transcription_on_silence(audio_path)
            
            return render_template('transcription.html', transcription=transcription)
    return render_template('upload.html')

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['transcription']
    language = request.form['language']
    translated_text = translate_text(text, language)
    return render_template('transcription.html', transcription=text, translation=translated_text, selected_language=language)

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form['transcription']
    language = request.form['summary_language']
    summary = summarize_text_with_gemini(text, language)
    return render_template('transcription.html', transcription=text, summary=summary)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
