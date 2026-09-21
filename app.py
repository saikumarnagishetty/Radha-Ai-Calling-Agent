import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="Radha AI Calling Agent")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

RADHA_NAME = os.getenv("RADHA_NAME", "Radha")
FIRST_QUESTION = os.getenv(
    "RADHA_FIRST_QUESTION",
    "Where is your husband?",
)

gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def ask_gemini(answer: str) -> str:
    """Generate Radha's next short spoken response from the caller's answer."""
    if not gemini:
        return "Thank you. I understood your answer."

    response = gemini.models.generate_content(
        model=GEMINI_MODEL,
        contents=answer,
        config=types.GenerateContentConfig(
            system_instruction=(
                f"You are {RADHA_NAME}, a natural Indian phone-call AI assistant. "
                "Speak briefly and naturally. Use simple Telugu/Telgish when appropriate. "
                "Do not invent facts. React only to what the caller said. "
                "Keep every response suitable for being spoken over a phone call. "
                "If the conversation is complete, politely say goodbye."
            ),
            temperature=0.7,
            max_output_tokens=120,
        ),
    )

    return (response.text or "Okay, thank you.").strip()


def build_question_response(question: str) -> str:
    """Build the first TwiML response and collect the caller's speech."""
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",
        language="te-IN",
        speech_timeout="auto",
    )

    gather.say(
        f"Hello, I am {RADHA_NAME}. {question}",
        language="te-IN",
    )

    response.append(gather)

    # Prevent the call from silently hanging up if no speech was detected.
    response.say("I could not hear you. Please try again.", language="te-IN")
    response.redirect("/voice", method="POST")

    return str(response)


@app.get("/")
def home():
    return {
        "agent": RADHA_NAME,
        "status": "running",
        "first_question": FIRST_QUESTION,
    }


@app.post("/voice")
def voice():
    """Twilio calls this webhook when the phone call starts."""
    return build_question_response(FIRST_QUESTION)


@app.post("/gather")
def gather(speech_result: str | None = Form(default=None)):
    """Receive the caller's transcribed speech and generate Radha's reply."""
    answer = (speech_result or "").strip()

    response = VoiceResponse()

    if not answer:
        response.say("Sorry, I did not catch that. Please say it again.", language="te-IN")
        response.redirect("/voice", method="POST")
        return str(response)

    reply = ask_gemini(answer)

    gather_again = Gather(
        input="speech",
        action="/gather",
        method="POST",
        language="te-IN",
        speech_timeout="auto",
    )
    gather_again.say(reply, language="te-IN")
    response.append(gather_again)

    return str(response)


@app.post("/call")
def start_call(to: str):
    """Start an outbound call through Twilio."""
    if not all(
        [TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]
    ):
        raise HTTPException(
            status_code=500,
            detail="Twilio credentials are missing in .env",
        )

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Twilio must be able to reach this HTTPS webhook.
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if not public_base_url:
        raise HTTPException(
            status_code=500,
            detail="PUBLIC_BASE_URL is missing in .env",
        )

    call = client.calls.create(
        to=to,
        from_=TWILIO_FROM_NUMBER,
        url=f"{public_base_url.rstrip('/')}/voice",
        method="POST",
    )

    return {
        "status": "calling",
        "call_sid": call.sid,
        "to": to,
    }
