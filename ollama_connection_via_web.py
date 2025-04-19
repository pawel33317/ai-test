import requests

# Konfiguracja
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"
PROMPT = "Wytłumacz teorię względności w prosty sposób"

# Treść zapytania
payload = {
    "model": MODEL_NAME,
    "prompt": PROMPT,
    "stream": False  # jeśli chcesz strumieniowanie, ustaw na True i użyj response.iter_lines()
}

# Wysyłanie żądania
response = requests.post(OLLAMA_URL, json=payload)

# Sprawdzanie odpowiedzi
if response.status_code == 200:
    data = response.json()
    print("Odpowiedź od modelu:")
    print(data["response"])
else:
    print(f"Błąd {response.status_code}: {response.text}")