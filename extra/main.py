import os
import json
import http.client
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prompt import build_gemini_prompt

# === Load environment variables from .env ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing. Please check your .env file.")

# === FastAPI setup ===
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# === Enable CORS for frontend access ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request models ===
class StoryRequest(BaseModel):
    story: str

class ChoiceRequest(BaseModel):
    choice: str

# === Serve the homepage ===
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# === Analyze the story ===
@app.post("/analyze/")
async def analyze_story(data: StoryRequest):
    user_story = data.story.strip()

    if not user_story:
        return JSONResponse(content={"error": "No story provided"}, status_code=400)

    # Build prompt
    prompt = build_gemini_prompt(user_story)
    print("🧠 Prompt sent to Gemini:\n", prompt)

    # Gemini API setup
    conn = http.client.HTTPSConnection("generativelanguage.googleapis.com", timeout=15)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    body = json.dumps({
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    })

    try:
        conn.request("POST", "/v1beta/models/gemini-2.5-flash:generateContent", body, headers)
        res = conn.getresponse()
        status = res.status
        raw_result = res.read().decode()

        print("🌐 Gemini API Status:", status)
        print("📦 Raw Gemini API result:\n", raw_result)

        result = json.loads(raw_result)

        ai_response = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print("📜 AI Response Text:\n", ai_response)

        # Try parsing response as JSON
        try:
            ai_data = json.loads(ai_response)
            return JSONResponse(content=ai_data)
        except json.JSONDecodeError as e:
            return JSONResponse(
                content={
                    "error": "❌ AI response is not valid JSON.",
                    "ai_response": ai_response,
                    "decode_error": str(e)
                },
                status_code=500
            )

    except Exception as e:
        print("❗ Gemini API error:", str(e))
        return JSONResponse(
            content={
                "error": "Unexpected Gemini API error",
                "details": str(e)
            },
            status_code=500
        )

# === Handle choice follow-up ===
@app.post("/choice/")
async def analyze_choice(choice_data: ChoiceRequest):
    choice = choice_data.choice.strip()

    follow_ups = {
        "Choice A": "You chose the path of courage. The shadows retreat, but only for now.",
        "Choice B": "You chose caution. A whisper follows you, unseen but near.",
    }

    follow_up = follow_ups.get(choice, "The story takes a mysterious turn...")

    easter_egg = ""
    if random.randint(1, 10) == 1:
        easter_egg = "🕯️ You discovered a secret candle. Use it wisely."

    return JSONResponse(content={
        "follow_up": follow_up,
        "easter_egg": easter_egg
    })
