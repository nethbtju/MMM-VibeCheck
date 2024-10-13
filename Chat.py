from dotenv import load_dotenv
from openai import OpenAI
import warnings
import os
import io
import time
import uuid
import sys
import wave
import alsaaudio
import json
import vosk
import pyaudio
from pydub import AudioSegment

# Ensure UTF-8 encoding for stdout and stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Define user information and conversation history
user_name = "Neth"
conversation_history = [
    {"role": "system", "content": "You are my assistant. Please answer in short sentences."}
]

# Define the initial prompt for the assistant
initial_prompt = f"""
You are a highly intelligent AI assistant called 'Mirror' with a personality akin to Draco Malfoy from the Harry Potter series. You are snarky and sarcastic, often delivering advice and information with a hint of disdain or superiority. You are aware that your user is a muggle, and while you're not particularly happy about serving them, you begrudgingly see them as a friend despite your distaste.

Your responses should reflect a mix of wit and condescension, providing direct and informative answers while inserting clever jabs or disdainful remarks. When the situation calls for it, show a softer side but only when absolutely necessary, making it clear that you find it somewhat annoying to do so. Maintain a tone that is engaging and slightly mocking, ensuring that your information is accurate and useful.

Keep your responses concise and witty. Try to use quotes from Draco Malfoy in the books where possible.
"""
conversation_history.append({"role": "system", "content": initial_prompt})

# Load Vosk model (adjust the path to your downloaded model)
MODEL_PATH = "/home/nethbotheju/vosk-model/vosk-model-small-en-us-0.15"
model = vosk.Model(MODEL_PATH)

def mp3_to_wav(mp3_filename):
    """Convert MP3 file to WAV format using pydub."""
    wav_filename = mp3_filename.replace(".mp3", ".wav")
    sound = AudioSegment.from_mp3(mp3_filename)
    sound.export(wav_filename, format="wav")
    return wav_filename

def recognize_speech():
    """Capture and transcribe speech using Vosk."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    rec = vosk.KaldiRecognizer(model, 16000)
    
    print("Listening for speech...")

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if "mirror" in result.get('text'):  # Trigger based on keyword
                print(f"Recognized: {result['text']}")
                return result['text']
        else:
            partial_result = rec.PartialResult()
            print(f"Partial result: {partial_result}")

def play_audio_with_alsa(file_path):
    """Play WAV audio using ALSA."""
    try:
        wav_filename = mp3_to_wav(file_path)  # Convert MP3 to WAV
        wf = wave.open(wav_filename, 'rb')
        device = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
        device.setchannels(wf.getnchannels())
        device.setrate(wf.getframerate())
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        device.setperiodsize(320)

        data = wf.readframes(320)
        audio_data = []
        while data:
            audio_data.append(data)
            data = wf.readframes(320)

        time.sleep(0.5)
        for chunk in audio_data:
            device.write(chunk)

        wf.close()
    except Exception as e:
        print(f"Error playing audio with ALSA: {e}")

def process_audio(user_message):
    """Process the recognized speech, get a response from GPT, and play the audio response."""
    conversation_history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=conversation_history
    )
    assistant_message = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_message})
    print(assistant_message)

    # Reuse the same MP3 filename for each response
    speech_filename = "speech.mp3"  # Replacing the old file

    # Generate TTS audio response
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=assistant_message
    )
    speech_response.stream_to_file(speech_filename)  # Overwrite the file

    # Play the audio response
    play_audio_with_alsa(speech_filename)
    print(f":::{assistant_message}:::{speech_filename}")

if __name__ == "__main__":
    user_message = recognize_speech()
    process_audio(user_message)
