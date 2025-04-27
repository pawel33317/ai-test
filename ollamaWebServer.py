from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ollama
import asyncio
from typing import Optional
import aiPrompts, aiConfig, aiDebug, aiWebEngine, aiApi

# FastAPI app setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve the favicon.ico file."""
    return FileResponse("static/favicon.ico")

@app.post("/chat-stream")
async def chat_stream(
    prompt: str = Form(...),
    user_questions: Optional[str] = Form(None),
    user_responses: Optional[str] = Form(None)
):
    async def stream():
        aiDebug.debug_print(f"Received prompt: {prompt[:80]}")
        messages = [{"role": "system", "content": aiConfig.SYSTEM_PROMPT}]

        # Add conversation history if available
        if user_questions and user_responses:
            add_conversation_history(messages, user_questions, user_responses)

        search_needed = determine_search_needed(prompt, messages)



        # Perform web search if needed
        if search_needed:
            async for result in handle_web_search(prompt, messages):  # Changed to async for
                yield result
        else:
            yield "meta: <b>Search not needed</b>\n"
            messages.append({"role": "user", "content": prompt})

        # Stream the final response
        async for result in stream_ai_response(messages):  # Changed to async for
            yield result

    return StreamingResponse(stream(), media_type="text/event-stream")

def determine_search_needed(prompt, messages_history):
    messages = messages_history.copy()
    if aiConfig.WEB_SEARCH_STATUS == "auto":
        aiDebug.debug_print(f"--- WEB SEARCH NECESSITY CHECK ---")
        messages.append({"role": "user", "content": aiPrompts.get_do_you_know_the_answer_prompt(prompt)})
        answer, _ = aiApi.get_model_answer(messages)
        return answer.lower().startswith("no")
    return aiConfig.WEB_SEARCH_STATUS == "always"

def add_conversation_history(messages, user_questions, user_responses):
    user_questions_list = eval(user_questions)
    user_responses_list = eval(user_responses)
    for question, response in zip(user_questions_list[-2:], user_responses_list[-2:]):
        messages.append({"role": "user", "content": aiPrompts.get_history_prevous_question_prompt(question)})
        messages.append({"role": "assistant", "content": aiPrompts.get_history_prevous_answer_prompt(response)})
        aiDebug.debug_print(f"Adding history -> User: {question[:50]}, Assistant: {response[:50]}")

async def handle_web_search(prompt, FINAL_MESSAGES):
    """Perform a web search and process the results."""
    yield "meta: <b>Searching</b>\n"

    aiDebug.debug_print(f"--- LANGUAGE DETECTION ---")
    messages=[{'role': 'user', 'content': aiPrompts.get_recognize_language(prompt)}]
    language, _ = aiApi.get_model_answer(messages)
    yield f"meta: <a>Language: {language}</a>\n"
    FINAL_MESSAGES.append({'role': 'system', 'content': aiPrompts.get_use_language_prompt(language)})


    aiDebug.debug_print(f"--- WEB SEARCH QUESTION GENERATION ---")
    messages=[{'role': 'system', 'content': aiConfig.SYSTEM_PROMPT},
              {'role': 'system', 'content': aiPrompts.get_use_language_prompt(language)},
              {'role': 'user', 'content': aiPrompts.get_question_to_search_engine_prompt(prompt)}]
    answer, _ = aiApi.get_model_answer(messages)
    yield f"meta: <a>Search query: {answer}</a>\n"
    
    urls = aiWebEngine.find_helpful_urls(answer)
    if not urls:
        yield "meta: <b>No results found</b>"
        return

    outer_break = False  # Flag to break the outer loop
    error_count = 0
    for url in urls:
        if outer_break:  # Check if the outer loop should break
            break

        urlContent = aiWebEngine.get_url_content(url)
        if urlContent:
            aiDebug.debug_print(f"--- URL CONTENT RECEIVED, LEN {len(urlContent)} --- FROM: {url[:80]}")
            # Split content into overlapping chunks
            chunks = []
            chunk_size = 1000
            overlap = 200
            for i in range(0, len(urlContent), chunk_size - overlap):
                chunk = urlContent[i:i + chunk_size]
                chunks.append(chunk)
                if len(chunk) < chunk_size:  # Stop if the last chunk is smaller than chunk_size
                    break

            for chunk in chunks:
                aiDebug.debug_print(f"   Processing chunk, len: {len(chunk)}: {chunk[:100]}")
                messages=[{'role': 'system', 'content': aiConfig.SYSTEM_PROMPT},
                          {'role': 'user', 'content': aiPrompts.get_is_the_answer_in_text_prompt(prompt, chunk)}]
                answer, error = aiApi.get_model_answer(messages)
                if error:
                    error_count += 1
                    aiDebug.debug_print(f"   Error in model response: {error}")
                    if error_count >= 3:
                        yield "meta: <b>Too many errors, stopping search</b>"
                        exit()   
                if answer.lower().startswith("yes"):
                    yield f"meta: <a href='{url}'>{url}</a>\n"
                    FINAL_MESSAGES.append({"role": "user", "content": aiPrompts.get_data_from_internet_prompt(chunk)})
                    outer_break = True  # Set the flag to break the outer loop
                    break
        else:
            aiDebug.debug_print(f"   Skipping URL due to fetch error: {url[:80]}")
    FINAL_MESSAGES.append({"role": "user", "content": aiPrompts.get_answer_with_internet_data_prompt(prompt)})

async def stream_ai_response(messages):
    aiDebug.debug_print(f"--- FINAL QUESTION REQUEST TO MODEL ---")
    stream, error = aiApi.get_model_answer_stream(messages)
    aiDebug.debug_print("--- Start of response stream ---")
    for chunk in stream:
        await asyncio.sleep(0)  # Ensure proper async behavior
        yield f"data: {chunk['message']['content']}"
    aiDebug.debug_print("--- End of response stream ---")

# API endpoints for updating settings
class SystemPrompt(BaseModel):
    system_prompt: str

class AiModel(BaseModel):
    ai_model: str

class WebSearchSettings(BaseModel):
    status: str
    pages: int

@app.post("/update-system-prompt")
async def update_system_prompt(prompt: SystemPrompt):
    aiConfig.SYSTEM_PROMPT = aiPrompts.get_system_prompt(prompt.system_prompt)
    return {"status": "success"}

@app.post("/update-ai-model")
async def update_ai_model(aimodel: AiModel):
    aiConfig.AI_MODEL = aimodel.ai_model
    return {"status": "success"}

@app.post("/update-web-search-settings")
async def update_web_search_settings(settings: WebSearchSettings):
    aiConfig.WEB_SEARCH_STATUS = settings.status
    aiConfig.WEB_SEARCH_PAGES = settings.pages

    # Validate settings
    if aiConfig.WEB_SEARCH_STATUS not in ["auto", "always", "never"]:
        return JSONResponse({"status": "error", "message": "Invalid status value."}, status_code=400)
    if not (1 <= aiConfig.WEB_SEARCH_PAGES <= 20):
        return JSONResponse({"status": "error", "message": "Pages value must be between 1 and 20."}, status_code=400)

    aiDebug.debug_print(f"Updated web search settings: Status={aiConfig.WEB_SEARCH_STATUS}, Pages={aiConfig.WEB_SEARCH_PAGES}")
    return {"status": "success", "settings": {"status": aiConfig.WEB_SEARCH_STATUS, "pages": aiConfig.WEB_SEARCH_PAGES}}