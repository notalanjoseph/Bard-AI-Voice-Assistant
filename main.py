from Bard import Chatbot
from playsound import playsound
import speech_recognition as sr
from os import system
import whisper
import warnings
import sys

# Paste your Bard Token (check README.md for where to find yours)
token = 'aghROKGcysKUOhA1XPlHodigfAtcRfC7jOo7OA3rxDcBzV6KzqrSCHYsPzmbt_5h2HoBDA.'
ts_token = 'sidts-CjEBSAxbGdkTVzjYEMu8JenjNJ2D5bYMhD0ZMT-9ERujj7bRCvu68NAruNLE1FL0nJucEAA'

chatbot = Chatbot(token, ts_token)
r = sr.Recognizer()

# for wake detections
tiny_model = whisper.load_model('tiny')
# for prompts
base_model = whisper.load_model('base')
# stops warning from cluttering the terminal
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Initiate pyttsx3 if OS is not Mac OS
if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    # Decrease speech rate by 50 wpm (Change as desired)
    engine.setProperty('rate', rate-50)


def prompt_bard(prompt):
    response = chatbot.ask(prompt)
    # only the value with key='content' from the dictionary
    return response['content']


def speak(text):
    # If Mac OS use system messages for TTS
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$: ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    # Use pyttsx3 for other OS
    else:
        engine.say(text)
        engine.runAndWait()


def main():
    # Initialize microphone object
    with sr.Microphone() as source:
        # block background noise
        r.adjust_for_ambient_noise(source)
        # Runs program indefinitely
        while True:
            # Continuously listens for wake word locally
            while True:
                try:
                    print('\nSay "Hi" to wake me up.\n')
                    audio = r.listen(source)  #listen for how long??
                    # whisper needs audio variable in wav format
                    with open("wake_word.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    transcription = tiny_model.transcribe('wake_word.wav')
                    transcription_text = transcription['text']
                    if 'hi' in transcription_text.lower().strip():
                        break
                    else:
                        print("No wake word found. TRY AGAIN")

                except Exception as e:
                    print("error transcribing audio: ", e)
                    continue

            try:
                playsound('wake_detected.mp3')
                print("wake word detected, I AM LISTENING\n")
                audio = r.listen(source)
                with open("prompt.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                prompt = base_model.transcribe('prompt.wav')
                prompt_text = prompt['text']
                print("Bard heard:", prompt_text, '\n')
                if len(prompt_text.strip()) == 0: # never executes??
                    print("please speak again, I heard nothing.")
                    speak("please speak again")
                    continue

            except Exception as e:
                print("error transcribing audio: ", e)
                continue

            response = prompt_bard(prompt_text)
            # windows cannot ASCII delete in command prompt to change font color
            if sys.platform.startswith('win'):
                print('BARD: ', response)
            else:
                # Prints Bard response in red for linux & mac terminal
                print("\033[31m" + 'BARD : ', response, '\n' + "\033[0m")
            speak(response)


if __name__ == '__main__':
    main()
