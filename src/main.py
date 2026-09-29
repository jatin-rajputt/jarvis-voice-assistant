"""
Project: Jarvis Voice Assistant
Author: Jatin
Type: Major Project
Description:
Ironman-inspired Voice Assistant with Arc Reactor GUI, System Automation,
Free Knowledge Search (No OpenAI API key required), and Security Access Controls.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_cli():
    """CLI Fallback Mode."""
    from jarvis_core import JarvisCore
    import speech_recognition as sr
    import time

    jarvis = JarvisCore()
    print("==================================================")
    print("       JARVIS VOICE ASSISTANT (CLI MODE)          ")
    print("==================================================")
    jarvis.speak("Initializing Jarvis CLI Mode")
    jarvis.speak(f"Authorized owner is {jarvis.owner_name}")

    while True:
        try:
            print("\nListening for wake word 'Jarvis'...")
            word = jarvis.listen_speech(timeout=5, phrase_time_limit=3)
            
            if word and "jarvis" in word.lower():
                print("Jarvis active...")
                jarvis.speak("Yes sir?")
                time.sleep(0.3)

                print("Listening for command...")
                command = jarvis.listen_speech(timeout=6, phrase_time_limit=4)
                if command:
                    res = jarvis.process_command(command)
                    if res == "EXIT":
                        break
        except KeyboardInterrupt:
            print("\nExiting Jarvis CLI...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


def main():
    # If user explicitly passes --cli flag in command line, run CLI mode
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--cli":
        run_cli()
    else:
        # Default: Launch Professional Ironman Arc Reactor GUI
        from gui import launch_gui
        launch_gui()


if __name__ == "__main__":
    main()
