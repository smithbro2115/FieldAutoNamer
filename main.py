import speech_recognition as sr
import pydub

AUDIO_FILE = "C:\\Users\\smith\\Downloads\\ZOOM0007_3.WAV"
AUDIO_FILE_1 = "C:\\Users\\smith\\Downloads\\Sports Human Voice Male Young Man Basketball" \
             " Announcer It's Fifty Six To Forty Five At The Half 02.wav"
# pydub.AudioSegment.ffmpeg = "D:\\Programming\\FieldAutoNamer\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe"
audio_editor = pydub.AudioSegment.from_wav(AUDIO_FILE)
first_fifteen = audio_editor[:8000]
last_fifteen = audio_editor[15000:]
first_fifteen = first_fifteen.set_frame_rate(44100)
print(first_fifteen.frame_rate)
audio_data = first_fifteen.export("cache\\Zoom.wav", format='wav', parameters=["-ar", "441000"])
# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile("cache\\Zoom.wav") as source:
    audio = r.record(source)  # read the entire audio file

try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print(r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
