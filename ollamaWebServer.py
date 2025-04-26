from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ollama
import asyncio
from typing import Optional
import aiPrompts
from datetime import date

# dodatkowe biblioteki do web search
import requests
from bs4 import BeautifulSoup
try:
    from googlesearch import search as google_search
except ImportError:
    raise ImportError("Install packet 'googlesearch-python' lub 'beautifulsoup4'.")

global SYSTEM_PROMPT
SYSTEM_PROMPT = "Your knowledge ends in 01.06.2023, Todays date is: "+ date.today().strftime('%d.%m.%Y') + "\nanswer the question only if you are sure you know the answer and you are sure the answer is correct as of " +  date.today().strftime('%d.%m.%Y')

global WEB_SEARCH_STATUS, WEB_SEARCH_PAGES
WEB_SEARCH_STATUS = "auto"
WEB_SEARCH_PAGES = 10

global AI_MODEL
AI_MODEL = "gemma3:4b"

global DEBUG
DEBUG = True  # Set to True to enable debug prints

def debug_print(*args):
    if DEBUG:
        print(*args)

def find_helpful_urls(query):
    debug_print(f"Searching the web for: {query}")
    results = []
    try:
        for j in google_search(query, num_results=WEB_SEARCH_PAGES):
            results.append(j)
    except Exception as e:
        debug_print(f"Error during web search: {e}")
    return results

def get_urls_content_plain_data(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        return None

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
        debug_print(f"Received prompt: {prompt[0:80]}")
        
        # Parse user questions and responses if provided
        finalFessages = [{"role": "system", "content": SYSTEM_PROMPT}]
        debug_print(f"System prompt: {SYSTEM_PROMPT[0:80]}")
        
        searchNeeded = False
        if WEB_SEARCH_STATUS == "auto":
            debug_print(f"Web search question: {aiPrompts.get_do_you_know_the_answer_prompt(prompt)[0:50]}")
            response = ollama.chat(
                model=AI_MODEL,
                messages=[
                    {'role': 'user', 'content': aiPrompts.get_do_you_know_the_answer_prompt(prompt)}
                ],
                stream=False  # wyłącza streamowanie, dostajesz całą odpowiedź
            )
            answer = response['message']['content']
            debug_print("[T/N] Model answer for do you know the answer:", answer)
            if answer.lower().startswith("nie"):
                searchNeeded = True
        elif WEB_SEARCH_STATUS == "always":
            searchNeeded = True

        # Add conversaition history if available
        if user_questions and user_responses:
            user_questions_list = eval(user_questions)  # Convert JSON string to list
            user_responses_list = eval(user_responses)  # Convert JSON string to list
            # Add user questions and responses to the messages
            for question, response in zip(user_questions_list[-2:], user_responses_list[-2:]):
                finalFessages.append({"role": "user", "content": "Previous user question: " + question})
                finalFessages.append({"role": "assistant", "content": response})
                debug_print(f"Adding history -> User: {question[0:50]}, Assistant: {response[0:50]}")
    


        #TODO: znaleźć słowa kluczowe po któych można wyszukiwać w internecie
        if searchNeeded:
            yield "meta: <b>Searching</b>\n"
            urls = find_helpful_urls(prompt)
            # for url in urls:
                # yield f"meta: <a href='{url}'>{url}</a>\n"

            if not urls:
                yield "meta: <b>No results found</b>"
                return
            else:

                for url in urls:
                    urlParsedContent = get_urls_content_plain_data(url)
                    if urlParsedContent:
                        ###AI call
                        debug_print(f"Requesting model to check data from: {url[0:80]}")
                        isContentEnoughResponse = ollama.chat(
                            model=AI_MODEL,
                            messages=[
                                {'role': 'system', 'content': SYSTEM_PROMPT},
                                {'role': 'user', 'content': aiPrompts.get_is_the_answer_in_text(prompt, urlParsedContent)}],
                            stream=False)
                        isContentEnoughAnswer = isContentEnoughResponse['message']['content']
                        debug_print(f"Up to date data from the Internet: " + urlParsedContent[0:100])
                        debug_print("[T/N] Model answer is enough:", isContentEnoughAnswer)

                        if isContentEnoughAnswer.lower().startswith("tak"):
                            yield f"meta: <a href='{url}'>{url}</a>\n"
                            finalFessages.append({"role": "user", "content": "Up to date data from the Internet: " + urlParsedContent})
                            break
                    else:
                        debug_print(f"Error fetching content from {url[0:80]}. Skipping.")

            finalFessages.append({"role": "user", "content": "Use only data provided from the Internet to respond. Detect the language used in below question and use this language to answer below question: \n" + prompt})
        else:
            yield "meta: <b>Search not needed</b>\n"
            finalFessages.append({"role": "user", "content": prompt})
        
        for msg in finalFessages:
            debug_print(f"[FINAL] message to chat: {msg['role']}: {msg['content'][0:120]}")

        # Stream the response
        stream = ollama.chat(
            model=AI_MODEL,
            messages=finalFessages,
            stream=True
        )

        for chunk in stream:
            await asyncio.sleep(0)
            content = chunk["message"]["content"]
            # debug_print(f"Streaming chunk: {content}")
            yield f"data: {content}"
        debug_print("End of response stream\n\n\n")
    return StreamingResponse(stream(), media_type="text/event-stream")

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
    SYSTEM_PROMPT = "Your knowledge ends in 01.06.2023, Todays date is: "+ date.today().strftime('%d.%m.%Y') + "\nanswer the question only if you are sure you know the answer and you are sure the answer is correct as of " +  date.today().strftime('%d.%m.%Y') + "\n" + prompt.system_prompt
    return {"status": "success"}

@app.post("/update-ai-model")
async def update_system_prompt(aimodel: AiModel):
    global AI_MODEL
    AI_MODEL = aimodel.ai_model
    return {"status": "success"}

@app.post("/update-web-search-settings")
async def update_web_search_settings(settings: WebSearchSettings):
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