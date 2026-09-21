# Radha AI Calling Agent

Radha is a voice-calling agent designed to:

1. Start an outbound phone call.
2. Introduce herself as Radha.
3. Ask a configured question.
4. Listen to the person's spoken answer.
5. Send the answer to Gemini.
6. Generate the next response dynamically.
7. Continue the conversation until Radha decides to end it.

## Architecture

Phone call → Twilio Voice → FastAPI → Gemini → TwiML response → Phone

## Current stack

- Python
- FastAPI
- Twilio Voice
- Gemini API
- python-dotenv

## Setup

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Add your Gemini and Twilio credentials.
5. Start the server:

```bash
uvicorn app:app --reload --port 8000
```

6. Expose the local server with HTTPS using a tunneling service such as ngrok.
7. Configure your Twilio Voice number's webhook to:

```
POST https://YOUR-DOMAIN/voice
```

## Important

Never commit `.env`. It contains private credentials.

The caller should be informed that they are speaking with an AI where required by applicable law, platform rules, or your use case.

## Roadmap

- [x] Gemini conversation logic
- [x] FastAPI voice webhooks
- [x] Speech collection
- [ ] Natural Telugu TTS
- [ ] Conversation memory
- [ ] Call logs
- [ ] Dashboard
- [ ] Production deployment
