from openai import OpenAI, OpenAIError
import time

client = OpenAI()

def ask_ai(prompt, max_retries=3, base_delay=2):
    messages = [
        {"role": "system", "content": "You are a helpful virtual assistant."},
        {"role": "user", "content": prompt}
    ]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content

        except OpenAIError as e:
            if "rate limit" in str(e).lower():
                time.sleep(base_delay * (2 ** attempt))
            else:
                raise e

    return "AI service unavailable right now."
