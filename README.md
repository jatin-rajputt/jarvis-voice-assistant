# Jarvis Voice Assistant

Author: Jatin

Jarvis is a secure, voice-controlled desktop assistant built with Python.
It can automate system tasks, manage files, fetch news, control audio, and respond intelligently using AI when available.

## ✨ Features

Voice activation (Jarvis)

Open websites (Google, YouTube, Facebook, LinkedIn)

System controls (shutdown, restart, sleep) with PIN protection

File & folder management (create, delete, list)

News fetching (MediaStack API)

CPU, RAM, battery status

Volume control (up, down, mute)

Jokes & time/date

AI-powered responses (optional)

Automatic Google Search fallback (no API required)

## 📁 Project Structure
```
majorproject/
├── src/
│   ├── main.py
│   ├── musicLibrary.py
│   └── _client.py
├── tests/
│   └── test_openai.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```
## 🔑 API Key Setup (Optional)

Jarvis supports AI responses using the OpenAI API.
If you do not set an API key, Jarvis will automatically fall back to Google Search.

✅ Option 1: Using OpenAI API (Recommended)

Create a file named .env in the project root.

Add your API key:

OPENAI_API_KEY=sk-your_api_key_here

NEWS_API_KEY=your_mediastack_api_key


Save the file.

Ensure .env is included in .gitignore.

Jarvis will now answer unknown voice commands intelligently.

✅ Option 2: No API Key (Search Fallback Mode)

If you do not have an OpenAI API key:

Jarvis will not crash

Jarvis will open Google Search automatically

Fully functional without AI

Example:

User: Jarvis
User: what is artificial intelligence
Jarvis: I will search this on Google

## 🔄 How Command Handling Works

Jarvis listens for known commands

If command is recognized → action is executed

If command is unknown:

OpenAI API available → AI response

No API key → Google Search fallback

## ▶️ How to Run the Project
Step 1: Create Virtual Environment
```
python -m venv .venv
```
Step 2: Activate Virtual Environment
```
.venv\Scripts\Activate.ps1
```
Step 3: Install Dependencies
```
pip install -r requirements.txt
```
Step 4: Run Jarvis
```
python src/main.py
```
### 🔐 Security Features

PIN-protected system commands

Ownership verification

Activity logging (jarvis_log.txt)

Sensitive keys stored in .env

### ⚠️ Notes

Microphone access is required

Works best on Windows

Python 3.10 – 3.12 recommended

Python 3.13 may have audio compatibility issues

### 🎓 Academic Use

This project is suitable for:

Major Project submission

Cybersecurity & AI demonstrations

Voice automation systems

Practical Python application

### 👤 Ownership

This project is permanently authored and owned by Jatin.
Unauthorized redistribution is discouraged.

If you want, next I can help you with:

Final .gitignore

Viva explanation

Demo script

Fix remaining audio issues

Just say next.
