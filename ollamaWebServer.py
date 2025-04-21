from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ollama
import asyncio
from typing import Optional

# dodatkowe biblioteki do web search
import requests
from bs4 import BeautifulSoup
try:
    from googlesearch import search as google_search
except ImportError:
    # Jeśli pakiet "googlesearch-python" nie jest zainstalowany, można użyć alternatywnej implementacji
    raise ImportError("Zainstaluj pakiet 'googlesearch-python' lub 'beautifulsoup4'.")

global SYSTEM_PROMPT
SYSTEM_PROMPT = ""

global WEB_SEARCH_STATUS, WEB_SEARCH_PAGES
WEB_SEARCH_STATUS = "auto"
WEB_SEARCH_PAGES = 5

global AI_MODEL
AI_MODEL = "gemma3:4b"

global DEBUG
DEBUG = True  # Set to True to enable debug prints

def debug_print(*args):
    """Prints debug information if DEBUG is True."""
    if DEBUG:
        print(*args)

app = FastAPI()
# Ustawienia szablonów HTML
templates = Jinja2Templates(directory="templates")

# Ścieżka do katalogu ze statycznymi plikami
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat-stream")
async def chat_stream(
    prompt: str = Form(...),
    user_questions: Optional[str] = Form(None),
    user_responses: Optional[str] = Form(None)
):
    """
    Handles chat streaming. Optionally includes user questions and responses if provided.
    """
    async def stream():
        debug_print(f"Received prompt: {prompt}")
        
        # Parse user questions and responses if provided
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        debug_print(f"System prompt: {SYSTEM_PROMPT}")
        
        if user_questions and user_responses:
            user_questions_list = eval(user_questions)  # Convert JSON string to list
            user_responses_list = eval(user_responses)  # Convert JSON string to list
            
            # Add user questions and responses to the messages
            for question, response in zip(user_questions_list, user_responses_list):
                messages.append({"role": "user", "content": question})
                messages.append({"role": "assistant", "content": response})
                debug_print(f"Adding history -> User: {question}, Assistant: {response}")
        
        # Add the current user prompt
        messages.append({"role": "user", "content": prompt})
        debug_print(f"Final messages: {messages}")

        # Stream the response
        stream = ollama.chat(
            model=AI_MODEL,
            messages=messages,
            stream=True
        )
        for chunk in stream:
            await asyncio.sleep(0)
            content = chunk["message"]["content"]
            debug_print(f"Streaming chunk: {content}")
            yield f"data: {content}"

    return StreamingResponse(stream(), media_type="text/event-stream")

# @app.post("/web-search")
# async def web_search(query: str = Form(...), num_results: int = Form(5)):
#     """
#     Wykonuje prostą wyszukiwarkę: pobiera listę URL-i za pomocą googlesearch,
#     następnie pobiera zawartość stron i zwraca czysty tekst (bez tagów HTML).
#     """
#     debug_print(f"Web search query: {query}, num_results: {num_results}")
#     results = []
#     # Pobranie URL-i z Google
#     try:
#         urls = list(google_search(query, num_results=num_results))
#         debug_print(f"Found URLs: {urls}")
#     except Exception as e:
#         debug_print(f"Error during Google search: {e}")
#         return JSONResponse({
#             "error": "Błąd podczas wyszukiwania:",
#             "details": str(e)
#         }, status_code=500)

#     # Parsowanie każdej strony i ekstrakcja tekstu
#     for url in urls:
#         try:
#             resp = requests.get(url, timeout=5)
#             resp.raise_for_status()
#             soup = BeautifulSoup(resp.text, 'html.parser')
#             text = soup.get_text(separator=' ', strip=True)
#             results.append({
#                 "url": url,
#                 "content": text
#             })
#             debug_print(f"Processed URL: {url}")
#         except Exception as e:
#             debug_print(f"Error processing URL {url}: {e}")
#             continue

#     debug_print(f"Final web search results: {results}")
#     return JSONResponse({
#         "query": query,
#         "results": results
#     })

class SystemPrompt(BaseModel):
    system_prompt: str

class AiModel(BaseModel):
    ai_model: str

class WebSearchSettings(BaseModel):
    status: str
    pages: int

@app.post("/update-system-prompt")
async def update_system_prompt(prompt: SystemPrompt):
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = prompt.system_prompt
    return {"status": "success"}

@app.post("/update-ai-model")
async def update_system_prompt(aimodel: AiModel):
    global AI_MODEL
    AI_MODEL = aimodel.ai_model
    return {"status": "success"}

@app.post("/update-web-search-settings")
async def update_web_search_settings(settings: WebSearchSettings):
    """
    Updates the web search settings.
    """
    global WEB_SEARCH_STATUS, WEB_SEARCH_PAGES
    WEB_SEARCH_STATUS = settings.status
    WEB_SEARCH_PAGES = settings.pages

    # Validate the status value
    if WEB_SEARCH_STATUS not in ["auto", "always", "never"]:
        return JSONResponse({"status": "error", "message": "Invalid status value."}, status_code=400)

    # Validate the pages value
    if WEB_SEARCH_PAGES < 1 or WEB_SEARCH_PAGES > 20:
        return JSONResponse({"status": "error", "message": "Pages value must be between 1 and 20."}, status_code=400)

    debug_print(f"Updated web search settings: Status={WEB_SEARCH_STATUS}, Pages={WEB_SEARCH_PAGES}")
    return {"status": "success", "settings": {"status": WEB_SEARCH_STATUS, "pages": WEB_SEARCH_PAGES}}