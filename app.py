from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor
import requests
import os
import google.generativeai as genai
import google.generativeai as genai
import json

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

API_KEY = os.getenv('AIzaSyBKavTG4yNRcatXJ-neX8-qVk4dWxtKWVQ')

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

def summarize_text_with_gemini(text):
    response = chat_session.send_message(f"give me the summary of {text} 'my prompt is Hello everybody today i'm saving an email that i got from a young physics student while working on an array of really really so the question is what is the difference between speed and velocity there is an interesting and excellent question because i do at some point that there is a same thing now as per usual i am going to tell you what the difference is in words and then i will explain with an easy example so basically the difference between them is that the velocity has a direction while speed does not in physics we call speed is scalar quantity is a vector expression 30 km per hour distance over time so this is by definition speed velocity expression with something like. 30 km per hour in the north direction or do not very simple example if you take your bicycle when you want to go to the park if you are writing your baisikal at 5 km per hour and 2 years reach the park then your speed is 5 km per hour is the distance that you have covered in the time it took you to cover it for velocity like i said it has to do with the direction so for example if you start from point a and you go with the speed. In a circle and then you come back to point a again the exact same point then we say your speed here is 5 km per hour but your velocity here is zero and the reason it is zero is because there is no directional again you started in the same point and then you came back at the same point again even if you want to work for mirrors this way 2 m this way. 4 m this way and then 2 metres of here then your velocity or average velocity is zero km per hour the difference between the two is like the difference between distance and displacement basically if you not sure about that when i will make a very quick video like this about it thank you so much guys just quickly while i'm working on different videos there are longer i'll see on the next one.' the")
    print(response)
    candidates = response.candidates
    
    # Extracting the "text" part from the response
    text_parts = []
    
    for candidate in candidates:
        content = candidate.content
        
        for part in content.parts:
            text = part.text
            text_parts.append(text)
            
    print(text_parts)
    
    return text_parts

    
   



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
            summary = summarize_text_with_gemini(transcription)
            return render_template('transcription.html', transcription=transcription, summary=summary)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
