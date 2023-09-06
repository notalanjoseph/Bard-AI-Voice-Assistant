from Bard import Chatbot
from playsound import playsound
import speech_recognition as sr
from os import system
import whisper
import warnings
import sys

# Paste your Bard Token (check README.md for where to find yours)
token = 'aghROKGcysKUOhA1XPlHodigfAtcRfC7jOo7OA3rxDcBzV6KzqrSCHYsPzmbt_5h2HoBDA.'
ts_token = 'sidts-CjEBSAxbGcUiPR8hAK2JC82-H61OklEbd2bGM6kH0Q4nxhJtaAxxE9Sy-8BsqRqZ23HREAA'
# Initialize Google Bard API
chatbot = Chatbot(token, ts_token)
r = sr.Recognizer()

tiny_model = whisper.load_model('tiny')
base_model = whisper.load_model('base')
#warnings.filter......

if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-50)

def prompt_bard(prompt):
    response = chatbot.ask(prompt)
    return response['content']

def speak(text):
    # If Mac OS use system messages for TTS
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$: ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    # Use pyttsx3 for other operating sytstems
    else:
        engine.say(text)
        engine.runAndWait()

def main():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while True:
            while True:
                try:
                    print('\nSay "Hi"\n')
                    audio = r.listen(source)
                    with open("wake_detect.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    result = tiny_model.transcribe('wake_detect.wav')
                    text_input = result['text']
                    if 'hi' in text_input.lower().strip():
                        break
                    else:
                        print("No wake word found. try again")

                except Exception as e:
                    print("error transcribing audio: ", e)
                    continue

            try:
                playsound('wake_detected.mp3')
                print("wake word detected\n")
                audio = r.listen(source)
                with open("prompt.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                result = base_model.transcribe('prompt.wav')
                prompt_text = result['text']
                print("sending to bard:", prompt_text, '\n')
                if len(prompt_text.strip()) == 0:
                    print("please speak again")
                    speak("please speak again")
                    continue
            except Exception as e:
                print("error transcribing audio: ", e)
                continue
            response = prompt_bard(prompt_text)
            # Prints Bard response normal if windows (cannot ASCII delete in command prompt to change font color)
            if sys.platform.startswith('win'):
                print('Bards response: ', response)
            else:
                # Prints Bard response in red for linux & mac terminal
                print("\033[31m" + 'Bards response: ',
                      response, '\n' + "\033[0m")
            speak(response)


if __name__ == '__main__':
    main()
