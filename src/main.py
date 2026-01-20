"""
Project: Jarvis Voice Assistant
Author: Jatin
Type: Major Project
Description:
Secure voice-controlled assistant with system automation,
file management, and access control.
"""
import speech_recognition as sr
import webbrowser
import musicLibrary
import requests
import time
import pyttsx3
import datetime
import psutil
import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyjokes
import shutil
from send2trash import send2trash
from dotenv import load_dotenv
load_dotenv()


# ================== OWNERSHIP ==================
OWNER_NAME = "Jatin"
PROJECT_NAME = "Jarvis Voice Assistant"
PROJECT_TYPE = "Major Project"


recognizer = sr.Recognizer()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")



VOICE_PIN = "1234"   # change this to your desired PIN

def speak(text):
    engine = pyttsx3.init("sapi5")
    engine.setProperty("rate",160)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    
def log_action(action):
    with open("jarvis_log.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.datetime.now()} | Owner: {OWNER_NAME} | {action}\n"
        )

def verify_pin(action_name):
    speak(f"Please say your security pin to {action_name}")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

        spoken_pin = recognizer.recognize_google(audio)
        spoken_pin = spoken_pin.replace(" ", "")

        if spoken_pin == VOICE_PIN:
            speak("Pin verified")
            return True
        else:
            speak("Incorrect pin. Action cancelled")
            return False

    except:
        speak("Pin verification failed. Action cancelled")
        return False


def get_common_path(name):
    user_home = os.path.expanduser("~")

    # Force OneDrive Desktop (your actual desktop)
    onedrive_base = os.path.join(user_home, "OneDrive")

    paths = {
        "desktop": os.path.join(onedrive_base, "Desktop"),
        "documents": os.path.join(onedrive_base, "Documents"),
        "downloads": os.path.join(onedrive_base, "Downloads")
    }

    return paths.get(name)

    
def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level, None)

def processCommand(c):
    #for some apps
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
        log_action("Opened Google")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
        log_action("Opened facebook")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
        log_action("Opened Youtube")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
        log_action("Opened linkedin")
        
        #for time
    elif "time" in c.lower():
        speak(datetime.datetime.now().strftime("The time is %H:%M"))
    
    elif "date" in c.lower():
        current_date = datetime.date.today().strftime("%d %B %Y")
        speak(f"Today's date is {current_date}")
    
        #for battery percentagw
    elif "battery" in c.lower():
        battery = psutil.sensor_battery()
        speak(f"Battery is at {battery.percent} percent")
        
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
        
    elif "joke" in c.lower():
        joke = pyjokes.get_joke(language="en", category="neutral")
        speak(joke)

    elif "volume up" in c.lower():
        set_volume(0.8)
        speak("Volume increased")

    elif "volume down" in c.lower():
        set_volume(0.3)
        speak("Volume decreased")

    elif "mute" in c.lower():
        set_volume(0.0)
        speak("Volume muted")
    
    elif "shutdown" in c.lower():
        if verify_pin("shut down the system"):
            log_action("Shutdown System")
            speak("Shutting down now")
            os.system("shutdown /s /t 5")

    elif "restart" in c.lower():
        if verify_pin("restart the system"):
            log_action("Restart System")
            speak("Restarting now")
            os.system("shutdown /r /t 5")

    elif "sleep" in c.lower():
        if verify_pin("put the system to sleep"):
            log_action("Sleep System")
            speak("Going to sleep mode")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif "who are you" in c.lower():
        speak("I am Jarvis, your personal voice assistant")

    elif "who created you" in c.lower() or "who is your owner" in c.lower():
        speak(f"I was created and owned by {OWNER_NAME}")
        
    elif "change your owner" in c.lower():
        speak(f"My ownership is permanently assigned to {OWNER_NAME}")

    elif "what can you do" in c.lower():
        speak(
            "I can open applications, search the internet, tell jokes, "
            "read news, control system power, check battery and performance, "
            "and assist you with daily tasks"
        )
        
    elif "cpu usage" in c.lower():
        cpu = psutil.cpu_percent()
        speak(f"CPU usage is {cpu} percent")
        print(f"CPU usage is {cpu} percent")

    elif "ram usage" in c.lower():
        ram = psutil.virtual_memory().percent
        speak(f"RAM usage is {ram} percent")
        print(f"RAM usage is {ram} percent")
        
    elif "open notepad" in c.lower():
        speak("Opening Notepad")
        os.system("notepad")

    elif "open calculator" in c.lower():
        speak("Opening Calculator")
        os.system("calc")

    elif "open command prompt" in c.lower():
        speak("Opening Command Prompt")
        os.system("start cmd")
        
    elif "repeat" in c.lower():
        if last_command:
            speak(f"Repeating: {last_command}")
            processCommand(last_command)
        else:
            speak("No previous command found")
        
    elif "search" in c.lower():
        query = c.lower().replace("search", "").strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        log_action(f"Searched:{query}")
        
    elif "open desktop" in c.lower():
        path = get_common_path("desktop")
        speak("Opening Desktop")
        os.startfile(path)

    elif "open documents" in c.lower():
        path = get_common_path("documents")
        speak("Opening Documents")
        os.startfile(path)

    elif "open downloads" in c.lower():
        path = get_common_path("downloads")
        speak("Opening Downloads")
        os.startfile(path)
        
    elif "create folder" in c.lower():
        speak("Tell me the folder name")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)

        folder_name = recognizer.recognize_google(audio)
        path = os.path.join(get_common_path("desktop"), folder_name)

        os.makedirs(path, exist_ok=True)
        log_action(f"Creted folder: {folder_name}")
        speak(f"Folder {folder_name} created on desktop")

    elif "create file" in c.lower():
        speak("Tell me the file name")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)

        file_name = recognizer.recognize_google(audio)
        path = os.path.join(get_common_path("desktop"), file_name + ".txt")

        with open(path, "w") as f:
            f.write("File created by Jarvis")
            f.write(f"Owner: {OWNER_NAME}\n")
            f.write(f"Created on: {datetime.datetime.now()}\n")
            
        log_action(f"Createde file {file_name}")
        speak(f"File {file_name} created on desktop")

    elif "list files" in c.lower():
        path = get_common_path("documents")
        files = os.listdir(path)

        if files:
            speak("Here are the files")
            for f in files[:5]:
                speak(f)
        else:
            speak("The folder is empty")

    elif "delete folder" in c.lower():
        speak("Tell me the folder name")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)

        folder_name = recognizer.recognize_google(audio)
        path = os.path.join(get_common_path("desktop"), folder_name)

        if os.path.exists(path):
            if verify_pin(f"delete the folder {folder_name}"):
                send2trash(path)
                log_action(f"Deleted folder: {folder_name}")
                speak("Folder deleted but get recovered from recycle bin")
                
        else:
            speak("Folder not found")
            
    elif "delete file" in c.lower():
        speak("Tell me the file name")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)

        file_name = recognizer.recognize_google(audio)
        path = os.path.join(get_common_path("desktop"), file_name +".txt")

        if os.path.exists(path):
            if verify_pin(f"delete the file {file_name}"):
                send2trash(path)
                log_action(f"delete file: {file_name}")
                speak("File deleted")
                print(f"but found in recycle bin")
        else:
            speak("File not found")



    elif "news" in c.lower():
        url = "https://api.mediastack.com/v1/news"
        params = {
            "access_key": NEWS_API_KEY,
            "countries": "in",
            "languages": "en",
            "limit": 5
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            speak("Sorry, I could not fetch the news.")
            return

        speak("Here are the top headlines.")

        for article in data["data"]:
            title = article["title"]
            print(title)
            speak(title)
            
    elif "exit jarvis" in c.lower() or "stop jarvis" in c.lower():
        log_action("jarvis stopped")
        speak("Goodbye")
        exit()

    
            
    else:
        #let go to it on openai
        pass
            
    
    
if __name__ == "__main__":
    speak(f"Initializing {PROJECT_NAME}")
    speak(f"Authorized owner is {OWNER_NAME}")
    log_action("Jarvis Started")

    time.sleep(1)
    while True:
    #Listen for the word "jarvis"

        r = sr.Recognizer()
        print("recognizing...")
        
        try:
            with sr.Microphone() as source:
                print("Listening..")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
            
            word = r.recognize_google(audio)
            
            if(word.lower()=="jarvis"):
                print("jarvis active..")
                speak("yes")
                time.sleep(0.5)
                #listen for command
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source,duration=0.5)
                    audio = r.listen(source, timeout=5, phrase_time_limit=3)
                    
                command = r.recognize_google(audio)
                global last_command
                if "repeat" not in command.lower():
                  last_command = command
                processCommand(command)
            
        
           
        except Exception as e:
            print("Error ; {0}".format(e))
            
            
                
        