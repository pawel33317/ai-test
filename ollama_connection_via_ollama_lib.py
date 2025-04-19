import ollama

# Nazwa modelu
model = 'gemma3:4b'

# Historia rozmowy
messages = [
    {'role': 'system', 'content': 'Jesteś pomocnym asystentem AI.'},
    {'role': 'user', 'content': 'ile wynosi pierwiastek kwadratowy liczby 5?'}
]

# Wysłanie zapytania z użyciem stream=True
print("Odpowiedź od modelu:")

stream = ollama.chat(
    model=model,
    messages=messages,
    stream=True
)

# Wyświetlanie odpowiedzi "na żywo"
for chunk in stream:from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import ollama
import asyncio

app = FastAPI()

# Ustawienia szablonów HTML
templates = Jinja2Templates(directory="templates")

# Ścieżka do katalogu ze statycznymi plikami
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat-stream")
async def chat_stream(prompt: str = Form(...)):
    async def stream():
        stream = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            await asyncio.sleep(0)
            content = chunk["message"]["content"]
            yield f"data: {content}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

    print(chunk['message']['content'], end='', flush=True)

# Dodanie odpowiedzi do historii
last_content = ''
for chunk in stream:
    if 'message' in chunk and 'content' in chunk['message']:
        last_content += chunk['message']['content']

messages.append({'role': 'assistant', 'content': last_content})

# Drugie pytanie
second_prompt = 'a ile liczby 6?'
messages.append({'role': 'user', 'content': second_prompt})

# Odpowiedź na drugie pytanie (również w trybie strumieniowym)
print("\n\nOdpowiedź na drugie pytanie:")

stream = ollama.chat(
    model=model,
    messages=messages,
    stream=True
)

last_content = ''
for chunk in stream:
    content_piece = chunk['message']['content']
    print(content_piece, end='', flush=True)
    last_content += content_piece