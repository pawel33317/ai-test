from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ollama
import asyncio

global SYSTEM_PROMPT
SYSTEM_PROMPT = ""

global AI_MODEL
AI_MODEL = "gemma3:4b"

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
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        for chunk in stream:
            await asyncio.sleep(0)
            content = chunk["message"]["content"]
            yield f"data: {content}"

    return StreamingResponse(stream(), media_type="text/event-stream")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class SystemPrompt(BaseModel):
    system_prompt: str

class AiModel(BaseModel):
    ai_model: str

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