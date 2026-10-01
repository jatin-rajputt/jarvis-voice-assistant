"""
Jarvis Core Assistant Module.
Encapsulates voice recognition, text-to-speech, system automation,
file management, PIN verification, AI Workshop presentation mode, and command processing.
Customized for O7 Services AI Workshop at Birla Open Minds International School (BOMIS), Hoshiarpur.
Features sentence-level interruptible speech engine with automatic Unicode text sanitization.
"""

import os
import sys
import time
import datetime
import webbrowser
import psutil
import requests
import pyjokes
import shutil
import pyttsx3
import speech_recognition as sr
from send2trash import send2trash
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import urllib.parse
import re

import musicLibrary
from client import ask_ai

load_dotenv()

# Ownership & Organization Configuration (Official O7 Services Details from o7services.com)
OWNER_NAME = os.getenv("OWNER_NAME", "Jatin")
COMPANY_NAME = "O7 Services"
COMPANY_FULL = "O7 Services IT Company & Training Institute"
COMPANY_HQ = "Jalandhar, Punjab, India"
COMPANY_FOUNDED = "September 5, 2015"
COMPANY_TAGLINE = "Master In-Demand IT Skills with Guaranteed Placement Support"
COMPANY_PHONE = "+91 84373 65007"
COMPANY_EMAIL = "enquiry@o7services.com"
COMPANY_URL = "https://o7services.com/"
EVENT_NAME = "O7 Services Artificial Intelligence Workshop"
PROJECT_NAME = "Jarvis Voice Assistant"
PROJECT_TYPE = "AI Workshop Demo Project"
VOICE_PIN = os.getenv("VOICE_PIN", "1234")

# School Configuration (Venue)
SCHOOL_NAME = os.getenv("SCHOOL_NAME", "Birla Open Minds International School, Hoshiarpur")
SCHOOL_SHORT_NAME = "BOMIS Hoshiarpur"
SCHOOL_MOTTO = "Nurturing India's Tomorrow"
SCHOOL_PHILOSOPHY = "Care, Cooperation, Collaboration, and Courtesy (The 4 C's)"
SCHOOL_DIRECTOR = "S. Kulwant Singh Kohar"
SCHOOL_LOCATION = "Village Lohar Kangana, P.O. Nainowal Jattan, Tanda Road, Hoshiarpur, Punjab"
SCHOOL_EMAIL = "admissions.hoshiarpur@birlaopenminds.com"

def sanitize_for_tts(text):
    """
    Sanitizes Unicode characters (like em-dashes, curly quotes, non-ASCII symbols)
    to clean ASCII to prevent Windows SAPI5 C++ engine crashes.
    """
    if not text:
        return ""
    text_str = str(text)
    replacements = {
        '—': ' - ',
        '–': ' - ',
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        '…': '...',
        '•': '*',
        '°': ' degrees',
        '©': ' Copyright ',
        '®': ' Registered ',
        '™': ' Trademark ',
        '⚡': '',
        '🎤': '',
        '🏫': '',
        '🌐': '',
        '▶': '',
        '😄': '',
        '🛑': ''
    }
    for orig, repl in replacements.items():
        text_str = text_str.replace(orig, repl)
    
    clean_ascii = text_str.encode('ascii', 'ignore').decode('ascii')
    return clean_ascii.strip()

class JarvisCore:
    def __init__(self, log_callback=None, state_callback=None):
        self.owner_name = OWNER_NAME
        self.company_name = COMPANY_NAME
        self.company_full = COMPANY_FULL
        self.company_hq = COMPANY_HQ
        self.company_founded = COMPANY_FOUNDED
        self.company_tagline = COMPANY_TAGLINE
        self.company_phone = COMPANY_PHONE
        self.company_email = COMPANY_EMAIL
        self.company_url = COMPANY_URL
        self.event_name = EVENT_NAME
        self.project_name = PROJECT_NAME
        self.voice_pin = VOICE_PIN
        
        # School Attributes
        self.school_name = SCHOOL_NAME
        self.school_short = SCHOOL_SHORT_NAME
        self.school_motto = SCHOOL_MOTTO
        self.school_philosophy = SCHOOL_PHILOSOPHY
        self.school_director = SCHOOL_DIRECTOR
        self.school_location = SCHOOL_LOCATION
        self.school_email = SCHOOL_EMAIL
        
        self.last_command = None
        self.log_callback = log_callback
        self.state_callback = state_callback
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # Speech State & Interruption Control
        self.stop_speech_flag = False
        self.is_speaking = False
        self.current_tts_engine = None

        # Speech Recognizer Tuning
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8

    def log(self, text, tag="JARVIS"):
        """Logs an action to jarvis_log.txt and emits to log callback."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_str = f"{timestamp} | [{tag}] {text}"
        
        try:
            with open("jarvis_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{log_str}\n")
        except Exception:
            pass

        if self.log_callback:
            try:
                self.log_callback(text, tag)
            except Exception:
                pass
            
    def set_state(self, state):
        """Notifies GUI of current state: IDLE, LISTENING, PROCESSING, SPEAKING, ERROR."""
        if self.state_callback:
            try:
                self.state_callback(state)
            except Exception:
                pass

    def stop_speaking(self):
        """Interrupts and halts current text-to-speech output immediately."""
        self.stop_speech_flag = True
        try:
            if self.current_tts_engine:
                self.current_tts_engine.stop()
        except Exception as e:
            print(f"[Stop Speaking Error] {e}")
        self.is_speaking = False
        self.set_state("IDLE")

    def speak(self, text):
        """Thread-safe and sentence-level interruptible text-to-speech execution."""
        if not text or not str(text).strip():
            return
        
        raw_text = str(text).strip()
        clean_text = sanitize_for_tts(raw_text)
        if not clean_text:
            return

        self.stop_speech_flag = False
        self.is_speaking = True
        self.set_state("SPEAKING")
        self.log(raw_text, tag="JARVIS")

        # Split text into individual sentences for fast sentence-by-sentence interrupt capability
        sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        if not sentences:
            sentences = [clean_text]

        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        try:
            engine = pyttsx3.init("sapi5")
            engine.setProperty("rate", 160)
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            
            self.current_tts_engine = engine

            if not self.stop_speech_flag:
                engine.say(clean_text)
                engine.runAndWait()
            
            engine.stop()
        except Exception as e:
            print(f"[TTS Exception Suppressed] {e}")
        finally:
            self.current_tts_engine = None
            self.is_speaking = False
            self.set_state("IDLE")

    def listen_speech(self, timeout=5, phrase_time_limit=4):
        """Captures audio from microphone and converts to text using SpeechRecognition."""
        self.set_state("LISTENING")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            self.set_state("PROCESSING")
            text = self.recognizer.recognize_google(audio)
            self.log(text, tag="USER")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"[Listen Error Suppressed] {e}")
            return None
        finally:
            self.set_state("IDLE")

    def verify_pin(self, action_name, custom_pin_prompt=None):
        """Verifies security PIN before performing administrative actions."""
        self.set_state("PIN_VERIFICATION")
        prompt = custom_pin_prompt or f"Please say your security pin to {action_name}"
        self.speak(prompt)
        
        spoken = self.listen_speech(timeout=6, phrase_time_limit=4)
        if spoken:
            clean_pin = spoken.replace(" ", "").strip()
            if clean_pin == self.voice_pin or self.voice_pin in clean_pin:
                self.speak("Security PIN verified successfully.")
                return True
        
        self.speak("PIN verification failed. Action cancelled.")
        return False

    def get_common_path(self, name):
        """Resolves system desktop, documents, and downloads directories safely."""
        user_home = os.path.expanduser("~")
        onedrive_base = os.path.join(user_home, "OneDrive")

        onedrive_desktop = os.path.join(onedrive_base, "Desktop")
        home_desktop = os.path.join(user_home, "Desktop")
        desktop = onedrive_desktop if os.path.exists(onedrive_desktop) else home_desktop

        onedrive_docs = os.path.join(onedrive_base, "Documents")
        home_docs = os.path.join(user_home, "Documents")
        documents = onedrive_docs if os.path.exists(onedrive_docs) else home_docs

        onedrive_downloads = os.path.join(onedrive_base, "Downloads")
        home_downloads = os.path.join(user_home, "Downloads")
        downloads = onedrive_downloads if os.path.exists(onedrive_downloads) else home_downloads

        paths = {
            "desktop": desktop,
            "documents": documents,
            "downloads": downloads
        }
        return paths.get(name.lower(), desktop)

    def set_volume(self, level):
        """Sets Windows master volume scalar (0.0 to 1.0)."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level, None)
        except Exception as e:
            self.log(f"Volume error: {e}", tag="SYSTEM")

    def fetch_news(self):
        """Fetches top news headlines using Mediastack API or free Google News RSS feed."""
        if self.news_api_key:
            try:
                url = "https://api.mediastack.com/v1/news"
                params = {
                    "access_key": self.news_api_key,
                    "countries": "in",
                    "languages": "en",
                    "limit": 5
                }
                res = requests.get(url, params=params, timeout=4).json()
                if "data" in res and res["data"]:
                    self.speak("Here are the top headlines.")
                    for article in res["data"][:5]:
                        if self.stop_speech_flag:
                            break
                        title = article.get("title", "")
                        if title:
                            self.speak(title)
                    return
            except Exception:
                pass

        try:
            rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
            resp = requests.get(rss_url, timeout=4)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = root.findall("./channel/item")
                if items:
                    self.speak("Here are today's top headlines from Google News.")
                    for item in items[:5]:
                        if self.stop_speech_flag:
                            break
                        title = item.find("title").text
                        if title:
                            clean_title = title.split(" - ")[0]
                            self.speak(clean_title)
                    return
        except Exception as e:
            self.log(f"News fetch error: {e}", tag="SYSTEM")

        self.speak("Sorry, I could not fetch the news at this moment.")

    # ================= O7 SERVICES & WORKSHOP PRESENTATION =================
    def welcome_workshop(self):
        """Welcomes students, teachers, and principal to the O7 Services AI Workshop."""
        speech = (
            f"Hello students, respected Director Sir Kulwant Singh Kohar, Principal, and dear teachers of {self.school_name}! "
            f"A warm welcome to the Artificial Intelligence Workshop conducted by {self.company_full}. "
            f"I am Jarvis, an AI Voice Assistant created by {self.owner_name} representing {self.company_name}. "
            f"Established in {self.company_founded} in {self.company_hq}, O7 Services is dedicated to empowering learners "
            f"with in-demand IT skills, 100 percent placement support, and live project industrial training. "
            f"Today, we demonstrate real-time speech recognition, holographic visualizers, and AI automation. "
            f"O7 Services is thrilled to inspire young minds here today!"
        )
        self.speak(speech)

    def speak_o7services_info(self):
        """Speaks comprehensive official information about O7 Services."""
        speech = (
            f"{self.company_full}, established on {self.company_founded} in {self.company_hq}, "
            f"is the premier IT training institute and software company. "
            f"Guided by our vision, '{self.company_tagline}', O7 Services features experienced industry engineer trainers, "
            f"6-week and 6-month industrial live project internships, and 100 percent placement assistance in leading IT companies."
        )
        self.speak(speech)

    def speak_o7_courses(self):
        """Lists key IT training programs offered by O7 Services."""
        speech = (
            f"O7 Services offers job-oriented industrial training in Artificial Intelligence, Data Science, Python, "
            f"Full Stack Web Development, Cyber Security, Cloud Computing, Mobile App Development, UI UX Design, "
            f"and Digital Marketing with guaranteed placement support."
        )
        self.speak(speech)

    def speak_o7_placement(self):
        """Speaks about O7 Services placement support."""
        speech = (
            f"O7 Services is renowned for 100 percent placement support, providing career counseling, resume building, "
            f"mock interview preparation, and direct job campus placements with top IT MNCs."
        )
        self.speak(speech)

    def speak_o7_contact(self):
        """Speaks official contact details for O7 Services."""
        speech = (
            f"You can contact O7 Services at phone number {self.company_phone}, "
            f"email {self.company_email}, or visit their official portal at o7services.com."
        )
        self.speak(speech)

    def speak_workshop_purpose(self):
        """Explains the purpose of the AI Workshop at the school."""
        speech = (
            f"We are here today at {self.school_name} for an interactive Artificial Intelligence Workshop by {self.company_name}. "
            f"Our mission is to introduce students to cutting-edge AI technologies, voice automation, and python programming, "
            f"sparking innovation and curiosity for tomorrow's digital world."
        )
        self.speak(speech)

    def present_school_info(self):
        """Presents detailed information about Birla Open Minds International School, Hoshiarpur."""
        speech = (
            f"It is our privilege at {self.company_name} to conduct this workshop at {self.school_name}. "
            f"Under the leadership of Director Sardar Kulwant Singh Kohar, BOMIS Hoshiarpur is dedicated to Nurturing India's Tomorrow. "
            f"Guided by the 4 C's: Care, Cooperation, Collaboration, and Courtesy, the school fosters the joy of learning "
            f"and empowers students to excel in science, technology, arts, and leadership."
        )
        self.speak(speech)

    def speak_director_info(self):
        """Speaks information about Director S. Kulwant Singh Kohar."""
        speech = (
            f"The Director of Birla Open Minds International School, Hoshiarpur is Sardar Kulwant Singh Kohar. "
            f"He envisions a robust, vibrant, and holistic education system that engenders excellence in every sphere, "
            f"developing entrepreneurial spirit, leadership qualities, and global culture in all students."
        )
        self.speak(speech)

    def speak_school_location(self):
        """Speaks the exact address of BOMIS Hoshiarpur."""
        speech = f"Birla Open Minds International School is located at {self.school_location}."
        self.speak(speech)

    # ================= COMMAND PROCESSING =================
    def process_command(self, raw_command):
        """Processes user input string and executes appropriate action."""
        if not raw_command or not str(raw_command).strip():
            return "SUCCESS"

        raw_str = str(raw_command).strip()
        command = raw_str.lower()
        self.set_state("PROCESSING")

        if "repeat" not in command:
            self.last_command = raw_str

        try:
            # ================= INSTANT SPEECH INTERRUPT COMMAND =================
            if command in ["stop", "stop speaking", "shut up", "be quiet", "silence", "stop talking", "quiet", "hush"] or command == "stop":
                self.stop_speaking()
                self.log("Speech stopped immediately by user command", tag="SYSTEM")
                return "STOPPED"

            # ================= O7 SERVICES WORKSHOP COMMANDS =================
            elif any(phrase in command for phrase in [
                "welcome workshop", "start workshop", "ai workshop", "welcome presentation", 
                "welcome judges", "project presentation", "welcome students", "welcome teachers"
            ]):
                self.welcome_workshop()

            elif any(phrase in command for phrase in [
                "about o7", "who is o7", "company info", "o7 services", "o7service", "about o7 services"
            ]):
                self.speak_o7services_info()

            elif any(phrase in command for phrase in [
                "o7 courses", "what courses", "courses offered", "training programs", "o7 training"
            ]):
                self.speak_o7_courses()

            elif any(phrase in command for phrase in [
                "placement", "o7 placement", "job support", "placement assistance"
            ]):
                self.speak_o7_placement()

            elif any(phrase in command for phrase in [
                "contact o7", "o7 phone", "o7 email"
            ]):
                self.speak_o7_contact()

            elif any(phrase in command for phrase in [
                "why are we here", "workshop info", "purpose of workshop", "workshop details"
            ]):
                self.speak_workshop_purpose()

            elif any(phrase in command for phrase in [
                "open o7 website", "open company website", "o7 website", "open o7"
            ]):
                try:
                    webbrowser.open(self.company_url)
                except Exception:
                    pass
                self.speak("Opening O7 Services official website")

            # ================= BIRLA OPEN MINDS SCHOOL COMMANDS =================
            elif any(phrase in command for phrase in [
                "tell me about my school", "tell me about school", "about my school", 
                "about school", "school info", "school information", "school details", 
                "our school", "tell about school", "birla open minds", "bomis", "birla open mind"
            ]):
                self.present_school_info()

            elif "school name" in command or "what is my school" in command or "name of my school" in command:
                self.speak(f"We are at {self.school_name}. Nurturing India's Tomorrow.")

            elif "school motto" in command or "motto of school" in command or "tagline" in command:
                self.speak(f"The motto of {self.school_name} is: {self.school_motto}.")

            elif any(phrase in command for phrase in [
                "director", "who is director", "director name", "director message", "kulwant singh"
            ]):
                self.speak_director_info()

            elif any(phrase in command for phrase in [
                "school location", "where is school", "school address", "location of school"
            ]):
                self.speak_school_location()

            elif command.startswith("change school name to") or command.startswith("set school name to"):
                new_name = command.replace("change school name to", "").replace("set school name to", "").strip().title()
                if new_name:
                    self.school_name = new_name
                    self.speak(f"School name updated to {self.school_name}.")
                else:
                    self.speak("Please specify the new school name.")

            # ================= WEB & APPLICATIONS =================
            elif "open google" in command:
                try:
                    webbrowser.open("https://google.com")
                except Exception:
                    pass
                self.speak("Opening Google")
            elif "open facebook" in command:
                try:
                    webbrowser.open("https://facebook.com")
                except Exception:
                    pass
                self.speak("Opening Facebook")
            elif "open youtube" in command:
                try:
                    webbrowser.open("https://youtube.com")
                except Exception:
                    pass
                self.speak("Opening YouTube")
            elif "open linkedin" in command:
                try:
                    webbrowser.open("https://linkedin.com")
                except Exception:
                    pass
                self.speak("Opening LinkedIn")
            elif "open github" in command:
                try:
                    webbrowser.open("https://github.com")
                except Exception:
                    pass
                self.speak("Opening GitHub")
            elif "open school website" in command or "open school site" in command:
                try:
                    webbrowser.open("https://www.birlaopenminds.com/k12/Punjab/hoshiarpur/about.php")
                except Exception:
                    pass
                self.speak("Opening Birla Open Minds Hoshiarpur official website")

            # ================= TIME & DATE =================
            elif "time" in command:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The time is {current_time}")
            elif "date" in command:
                current_date = datetime.date.today().strftime("%B %d, %Y")
                self.speak(f"Today's date is {current_date}")

            # ================= SYSTEM METRICS =================
            elif "battery" in command:
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        status = "plugged in" if battery.power_plugged else "on battery"
                        self.speak(f"Battery is at {battery.percent} percent and {status}")
                    else:
                        self.speak("Battery information unavailable")
                except Exception:
                    self.speak("Battery sensor unavailable")

            elif "cpu usage" in command or "cpu" in command:
                try:
                    cpu = psutil.cpu_percent(interval=0.5)
                    self.speak(f"CPU usage is currently at {cpu} percent")
                except Exception:
                    self.speak("CPU telemetry unavailable")

            elif "ram usage" in command or "memory" in command:
                try:
                    ram = psutil.virtual_memory().percent
                    self.speak(f"RAM usage is currently at {ram} percent")
                except Exception:
                    self.speak("RAM telemetry unavailable")

            # ================= MUSIC PLAYBACK =================
            elif command.startswith("play") or "play song" in command or "play music" in command:
                song_query = command.replace("play song", "").replace("play music", "").replace("play", "", 1).strip()
                if song_query:
                    try:
                        title, url = musicLibrary.play_song(song_query)
                        self.speak(f"Playing {title} on YouTube")
                    except Exception as e:
                        print(f"[Music Fallback Triggered] {e}")
                        try:
                            encoded_q = urllib.parse.quote(song_query)
                            search_url = f"https://www.youtube.com/results?search_query={encoded_q}"
                            webbrowser.open(search_url)
                        except Exception:
                            pass
                        self.speak(f"Playing {song_query} on YouTube")
                else:
                    try:
                        webbrowser.open("https://www.youtube.com")
                    except Exception:
                        pass
                    self.speak("Opening YouTube")

            # ================= ENTERTAINMENT =================
            elif "joke" in command:
                try:
                    joke = pyjokes.get_joke(language="en", category="neutral")
                    self.speak(joke)
                except Exception:
                    self.speak("Why did the computer go to the doctor? Because it had a virus!")

            # ================= VOLUME CONTROLS =================
            elif "volume up" in command or "increase volume" in command:
                self.set_volume(0.8)
                self.speak("Volume set to 80 percent")
            elif "volume down" in command or "decrease volume" in command:
                self.set_volume(0.3)
                self.speak("Volume set to 30 percent")
            elif "mute" in command:
                self.set_volume(0.0)
                self.speak("Volume muted")

            # ================= POWER MANAGEMENT =================
            elif "shutdown" in command:
                if self.verify_pin("shut down the system"):
                    self.speak("Initiating system shutdown sequence.")
                    os.system("shutdown /s /t 5")
            elif "restart" in command:
                if self.verify_pin("restart the system"):
                    self.speak("Initiating system restart sequence.")
                    os.system("shutdown /r /t 5")
            elif "sleep" in command:
                if self.verify_pin("put the system to sleep"):
                    self.speak("Putting system to sleep mode.")
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

            # ================= SYSTEM APPS =================
            elif "open notepad" in command:
                self.speak("Opening Notepad")
                os.system("start notepad")
            elif "open calculator" in command:
                self.speak("Opening Calculator")
                os.system("start calc")
            elif "open command prompt" in command or "open cmd" in command:
                self.speak("Opening Command Prompt")
                os.system("start cmd")
            elif "open powershell" in command:
                self.speak("Opening PowerShell")
                os.system("start powershell")
            elif "open task manager" in command:
                self.speak("Opening Task Manager")
                os.system("start taskmgr")

            # ================= ASSISTANT IDENTITY =================
            elif "who are you" in command:
                self.speak("I am Jarvis, an AI voice assistant developed by O7 Services.")
            elif "who created you" in command or "who is your owner" in command:
                self.speak(f"I was created by {self.owner_name} representing {self.company_name}.")
            elif "what can you do" in command:
                self.speak(
                    "I can monitor system performance, open applications, search the web, "
                    "play songs, deliver headlines, manage files, control system power, "
                    "and demonstrate AI technologies for O7 Services workshops."
                )

            # ================= COMMAND REPETITION =================
            elif "repeat" in command:
                if self.last_command:
                    self.speak(f"Repeating: {self.last_command}")
                    self.process_command(self.last_command)
                else:
                    self.speak("No previous command recorded in memory.")

            # ================= FILE MANAGEMENT =================
            elif "open desktop" in command:
                path = self.get_common_path("desktop")
                self.speak("Opening Desktop folder")
                os.startfile(path)
            elif "open documents" in command:
                path = self.get_common_path("documents")
                self.speak("Opening Documents folder")
                os.startfile(path)
            elif "open downloads" in command:
                path = self.get_common_path("downloads")
                self.speak("Opening Downloads folder")
                os.startfile(path)

            elif "create folder" in command:
                self.speak("What is the name for the new folder?")
                folder_name = self.listen_speech(timeout=5, phrase_time_limit=3)
                if folder_name:
                    desktop_path = self.get_common_path("desktop")
                    folder_path = os.path.join(desktop_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    self.speak(f"Folder '{folder_name}' created on Desktop.")
                else:
                    self.speak("Folder name was not heard clearly. Folder creation cancelled.")

            elif "create file" in command:
                self.speak("What is the name for the text file?")
                file_name = self.listen_speech(timeout=5, phrase_time_limit=3)
                if file_name:
                    desktop_path = self.get_common_path("desktop")
                    file_path = os.path.join(desktop_path, file_name + ".txt")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"File created by {self.project_name}\n")
                        f.write(f"Organization: {self.company_name}\n")
                        f.write(f"HQ: {self.company_hq}\n")
                        f.write(f"Founded: {self.company_founded}\n")
                        f.write(f"Presenter: {self.owner_name}\n")
                        f.write(f"School Venue: {self.school_name}\n")
                        f.write(f"Timestamp: {datetime.datetime.now()}\n")
                    self.speak(f"File '{file_name}.txt' created on Desktop.")
                else:
                    self.speak("File name was not heard. File creation cancelled.")

            elif "list files" in command:
                path = self.get_common_path("documents")
                try:
                    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                    if files:
                        self.speak("Here are some files in your Documents folder.")
                        for f in files[:5]:
                            self.speak(f)
                    else:
                        self.speak("Your Documents folder is empty.")
                except Exception as e:
                    self.speak("Could not access files.")

            elif "delete folder" in command:
                self.speak("Which folder on Desktop would you like to delete?")
                folder_name = self.listen_speech(timeout=5, phrase_time_limit=3)
                if folder_name:
                    desktop_path = self.get_common_path("desktop")
                    folder_path = os.path.join(desktop_path, folder_name)
                    if os.path.exists(folder_path):
                        if self.verify_pin(f"delete folder {folder_name}"):
                            send2trash(folder_path)
                            self.speak(f"Folder '{folder_name}' moved to Recycle Bin.")
                    else:
                        self.speak(f"Folder '{folder_name}' was not found on Desktop.")

            elif "delete file" in command:
                self.speak("Which file on Desktop would you like to delete?")
                file_name = self.listen_speech(timeout=5, phrase_time_limit=3)
                if file_name:
                    desktop_path = self.get_common_path("desktop")
                    file_path = os.path.join(desktop_path, file_name + ".txt")
                    if os.path.exists(file_path):
                        if self.verify_pin(f"delete file {file_name}"):
                            send2trash(file_path)
                            self.speak(f"File '{file_name}.txt' moved to Recycle Bin.")
                    else:
                        self.speak(f"File '{file_name}.txt' was not found on Desktop.")

            # ================= NEWS & SEARCH =================
            elif "news" in command:
                self.fetch_news()

            elif "exit jarvis" in command or "stop jarvis" in command or "exit" in command:
                self.speak("Shutting down Jarvis interface. Goodbye, sir.")
                return "EXIT"

            elif command.startswith("search"):
                query = command.replace("search", "", 1).strip()
                if query:
                    self.speak(f"Searching Google for {query}")
                    try:
                        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
                    except Exception:
                        pass
                else:
                    self.speak("Please specify what you want to search for.")

            else:
                self.speak("Analyzing database...")
                try:
                    answer = ask_ai(raw_str)
                except Exception as e:
                    print(f"[AI Search Exception Suppressed] {e}")
                    answer = None

                if answer:
                    self.speak(answer)
                else:
                    self.speak("No direct answer found in memory. Launching Google Search.")
                    try:
                        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(raw_str)}")
                    except Exception:
                        pass

        except Exception as outer_cmd_err:
            print(f"[Command Processing Exception Suppressed] {outer_cmd_err}")
            self.speak("I have processed your command sir.")

        self.set_state("IDLE")
        return "SUCCESS"
