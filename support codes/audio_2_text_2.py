from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
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
    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS-14,
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

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_chunk, chunk_filenames))
    
    whole_text = "".join(results)
    return whole_text

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

if __name__ == '__main__':
    app.run(debug=True)
