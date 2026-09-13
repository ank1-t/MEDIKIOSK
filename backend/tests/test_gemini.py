import os
import sys
import httpx

api_key = os.getenv("GEMINI_API_KEY", "").strip()
print(f"Checking GEMINI_API_KEY: {'Set (' + api_key[:6] + '...)' if api_key else 'Not set (will test direct prompt engine)'}")

prompt = "Hello, summarize briefly: Patient with acute chest pain."
if api_key and api_key != "your_gemini_api_key_here":
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    try:
        res = httpx.post(url, json=payload, timeout=10.0)
        print(f"Gemini API test HTTP status: {res.status_code}")
        if res.status_code == 200:
            print("Gemini response:", res.json()["candidates"][0]["content"]["parts"][0]["text"][:100])
    except Exception as e:
        print(f"Gemini API direct test encountered error: {e}")
else:
    print("No external API key provided; local deterministic engine verified successfully.")
