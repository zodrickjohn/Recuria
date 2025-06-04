import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
import google.generativeai as genai
from dotenv import load_dotenv
import pymongo
from datetime import datetime

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Twilio config
twilio_client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# MongoDB connection
mongo_client = pymongo.MongoClient(os.getenv("DATABASE_URL"))
db = mongo_client[os.getenv("DATABASE_NAME")]
resumes_collection = db.data

# FastAPI app
app = FastAPI()
conv_history = []

# Global state for WebSocket handling
call_state = {
    "candidate": None,
    "candidate_uid": None,
    "stream_sid": None,
    "latest_audio_timestamp": 0,
    "latest_assistant_item": None,
    "response_start_timestamp_twilio": None,
    "mark_queue": []
}

@app.get("/")
async def index():
    return {"message": "Carla is ready to make calls!"}


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle real-time audio stream from Twilio."""
    print("📞 Client connected to Carla's media stream")
    await websocket.accept()

    global call_state

    # Reset call state
    call_state.update({
        "stream_sid": None,
        "latest_audio_timestamp": 0,
        "latest_assistant_item": None,
        "response_start_timestamp_twilio": None,
        "mark_queue": []
    })

    async with websockets.connect(
        "wss://api.deepgram.com/v1/listen",
        extra_headers={
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}"
        },
        ping_interval=5,
        ping_timeout=30
    ) as deepgram_ws:
        print("🎙️ Deepgram connection established")

        async def receive_from_twilio():
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media':
                        payload = base64.b64decode(data['media']['payload'])
                        await deepgram_ws.send(payload)
                    elif data['event'] == 'start':
                        call_state["stream_sid"] = data['start']['streamSid']
                        print(f"📞 Call started - SID: {call_state['stream_sid']}")
                    elif data['event'] == 'stop':
                        print("🛑 Call ended. Saving transcript...")
                        with open('output.txt', 'w') as file:
                            file.write(str(conv_history))
                        print("💾 Transcript saved to output.txt")

                        # Update MongoDB with secondary score
                        extract_and_update(call_state["candidate_uid"])
                        await websocket.close()
            except Exception as e:
                print(f"❌ Error receiving from Twilio: {e}")

        async def send_to_twilio():
            try:
                async for msg in deepgram_ws:
                    transcript = json.loads(msg)
                    if transcript.get("type") == "Results":
                        words = transcript["channel"]["alternatives"][0]["words"]
                        user_text = " ".join(word["word"] for word in words)
                        print(f"🎤 Transcribed: {user_text}")
                        conv_history.append({"user": user_text})

                        # Generate response using Gemini Flash
                        ai_response = gemini_model.generate_content(f"Respond naturally to: {user_text}").text.strip()
                        print(f"🤖 Carla: {ai_response}")
                        conv_history.append({"assistant": ai_response})

                        # Send back via Twilio
                        audio_response = {
                            "event": "media",
                            "streamSid": call_state["stream_sid"],
                            "media": {
                                "payload": base64.b64encode(ai_response.encode()).decode()
                            }
                        }
                        await websocket.send_json(audio_response)

            except Exception as e:
                print(f"❌ Error sending to Twilio: {e}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


def extract_and_update(uid):
    """Use Gemini Flash to evaluate the interview and update MongoDB"""
    try:
        with open('output.txt', 'r') as file:
            log = file.read().strip()

        prompt = f"""
        Grade this candidate on a scale of 1–10 based on this transcript:
        
        Transcript:
        {log}
        
        Rubric:
        - Initial Impression & Cultural Fit (2 pts)
        - Experience & Technical Skills (3 pts)
        - Communication Skills (2 pts)
        - Practical Alignment (2 pts)
        - Red Flags (-0.5 each)
        
        Return final score and justification.
        """
        response = gemini_model.generate_content(prompt)
        content = response.text.strip()

        # Extract score manually from response
        score_match = re.search(r"Final Score:\s*(\d+\.?\d*)", content)
        final_score = float(score_match.group(1)) if score_match else 8.0
        justification = content

        # Update MongoDB
        result = resumes_collection.update_one(
            {"UID": int(uid)},
            {
                "$set": {
                    "secondary_score": final_score,
                    "phone_screen_notes": justification,
                    "phone_screen": "completed"
                }
            }
        )

        print(f"✅ Updated resume for UID {uid}")
        return True

    except Exception as e:
        print(f"❌ Failed to update MongoDB: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    print("🟢 Carla is running and ready to initiate calls")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5050)))