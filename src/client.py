"""
Client module for Jarvis Voice Assistant.
Provides 100% free AI knowledge retrieval & web search queries
without requiring any OpenAI API key or paid subscription.
All network calls are wrapped in fail-safe try/except blocks to prevent crashes.
"""

import requests
import wikipedia
from bs4 import BeautifulSoup
import re
import urllib.parse

def ask_ai(prompt):
    """
    Search Wikipedia, DuckDuckGo Instant Answers, or web snippets to answer questions.
    Returns a concise string answer if found, or None if fallback to browser search is required.
    Guaranteed never to throw an unhandled exception or crash the app.
    """
    if not prompt or not str(prompt).strip():
        return None

    try:
        clean_prompt = str(prompt).strip()
        
        # Strip common question prefixes for clean search queries
        query = re.sub(
            r'^(who is|what is|tell me about|define|search for|where is|how to|can you tell me about)\s+', 
            '', 
            clean_prompt, 
            flags=re.IGNORECASE
        ).strip()

        if not query:
            query = clean_prompt

        # 1. Try Wikipedia Summary
        try:
            summary = wikipedia.summary(query, sentences=2, auto_suggest=False)
            if summary and len(summary) > 20:
                return summary
        except wikipedia.DisambiguationError as e:
            if hasattr(e, 'options') and e.options:
                try:
                    summary = wikipedia.summary(e.options[0], sentences=2, auto_suggest=False)
                    if summary:
                        return summary
                except Exception:
                    pass
        except Exception:
            pass

        # 2. Try DuckDuckGo Instant Answer API (Free, no API key needed)
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            res = requests.get(url, timeout=3).json()
            abstract = res.get("AbstractText", "")
            if abstract:
                return abstract
            
            # Check Related Topics
            for topic in res.get("RelatedTopics", []):
                if isinstance(topic, dict) and "Text" in topic:
                    text = topic["Text"]
                    if len(text) > 25:
                        return text
        except Exception:
            pass

        # 3. DuckDuckGo HTML Snippet Web Scrape Fallback
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = soup.find_all('a', class_='result__snippet')
                for r in results:
                    snippet = r.get_text(strip=True)
                    if snippet and len(snippet) > 25:
                        return snippet
        except Exception:
            pass

    except Exception as outer_err:
        print(f"[Client Search Exception Handled] {outer_err}")

    return None
