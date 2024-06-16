import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import pyaudio
import wave

# Load pre-trained model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5

# Initialize pyaudio
audio = pyaudio.PyAudio()

# Function to record audio and convert to text
def recognize_speech():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    print("Listening...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")
    stream.stop_stream()
    stream.close()

    # Save the recorded data as a WAV file
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Load the audio file
    speech_array, sampling_rate = torchaudio.load("output.wav")
    # Preprocess the audio file
    inputs = processor(speech_array, sampling_rate=16000, return_tensors="pt", padding=True)

    # Perform inference
    with torch.no_grad():
        logits = model(inputs.input_values).logits

    # Get the predicted ids
    predicted_ids = torch.argmax(logits, dim=-1)

    # Decode the ids to text
    transcription = processor.batch_decode(predicted_ids)
    print(f"You said: {transcription[0]}")

if __name__ == "__main__":
    while True:
        recognize_speech()
