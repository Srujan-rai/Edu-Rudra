import moviepy.editor as mp

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

video_path = "What is Velocity -  Full Concept of Velocity - Physics  Infinity Learn.mp4"
audio_path = "extracted_audio.wav"

extract_audio(video_path, audio_path)