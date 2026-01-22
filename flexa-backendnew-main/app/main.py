import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from .schema import (
    ChatStartResponse, ChatMessageRequest, ChatMessageResponse,
    RecommendationRequest, RecommendationResponse
)
from .ml import FlexaRecommender
from .utils import normalize_yes_no, normalize_sex

app = FastAPI(title="Flexa Backend")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel preview deployments
        # Add your production domain here after deploying frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML recommender once
recommender = FlexaRecommender()

# Very simple in-memory sessions (OK for demo/uni project)
# For production: use Redis / DB
SESSIONS: Dict[str, Dict[str, Any]] = {}


def _new_session() -> str:
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "state": "ASK_NAME",
        "data": {}
    }
    return session_id


@app.get("/chat/start", response_model=ChatStartResponse)
def chat_start():
    session_id = _new_session()
    return ChatStartResponse(
        session_id=session_id,
        message="Hi! I'm Flexa 👋 What’s your name?"
    )


@app.post("/chat/message", response_model=ChatMessageResponse)
def chat_message(payload: ChatMessageRequest):
    session = SESSIONS.get(payload.session_id)
    if not session:
        # create a new one if missing
        payload.session_id = _new_session()
        session = SESSIONS[payload.session_id]

    state = session["state"]
    data = session["data"]
    text = payload.user_message.strip()

    # State machine: greet -> collect -> recommend
    if state == "ASK_NAME":
        data["name"] = text
        session["state"] = "ASK_PROBLEM"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=f"Nice to meet you, {data['name']}! What do you need help with? (e.g., weight loss, weight gain, flexibility, toning)"
        )

    if state == "ASK_PROBLEM":
        data["problem"] = text
        session["state"] = "ASK_SEX"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message="Got it. What is your sex? (Male/Female)"
        )

    if state == "ASK_SEX":
        data["sex"] = normalize_sex(text)
        session["state"] = "ASK_AGE"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message="What is your age?"
        )

    if state == "ASK_AGE":
        try:
            data["age"] = int(text)
        except:
            return ChatMessageResponse(
                session_id=payload.session_id,
                state=state,
                data_collected=data,
                message="Please type your age as a number (example: 21)."
            )
        session["state"] = "ASK_HEIGHT"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message="What is your height in meters? (example: 1.65)"
        )

    if state == "ASK_HEIGHT":
        try:
            data["height_m"] = float(text)
        except:
            return ChatMessageResponse(
                session_id=payload.session_id,
                state=state,
                data_collected=data,
                message="Please type height in meters (example: 1.65)."
            )
        session["state"] = "ASK_WEIGHT"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message="What is your weight in kg? (example: 55)"
        )

    if state == "ASK_WEIGHT":
        try:
            data["weight_kg"] = float(text)
        except:
            return ChatMessageResponse(
                session_id=payload.session_id,
                state=state,
                data_collected=data,
                message="Please type weight in kg (example: 55)."
            )
        
        # Calculate BMI
        bmi = data["weight_kg"] / (data["height_m"] ** 2)
        bmi_category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        data["bmi"] = round(bmi, 1)
        data["bmi_category"] = bmi_category
        
        session["state"] = "ASK_HYPERTENSION"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=f"Great! Your BMI is {data['bmi']} ({bmi_category}).\n\nDo you have hypertension (high blood pressure)? (Yes/No)",
            user_data={
                "name": data.get("name"),
                "height": round(data["height_m"] * 100),  # Convert to cm
                "weight": data["weight_kg"],
                "bmi": data["bmi"],
                "bmi_category": bmi_category
            }
        )

    if state == "ASK_HYPERTENSION":
        data["hypertension"] = normalize_yes_no(text)
        session["state"] = "ASK_DIABETES"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message="Do you have diabetes? (Yes/No)"
        )

    if state == "ASK_DIABETES":
        data["diabetes"] = normalize_yes_no(text)
        
        # Check if user has health conditions
        has_conditions = data["hypertension"] == "Yes" or data["diabetes"] == "Yes"
        
        # GOAL DRIFT DETECTION
        # Before generating recommendations, check if stated problem matches ML prediction
        drift_result = recommender.detect_goal_drift(
            profile={
                "sex": data["sex"],
                "age": data["age"],
                "height_m": data["height_m"],
                "weight_kg": data["weight_kg"],
                "hypertension": data["hypertension"],
                "diabetes": data["diabetes"],
            },
            stated_problem=data.get("problem", "")
        )
        
        # Store drift detection result
        session["drift_result"] = drift_result
        
        # If drift detected, ask for clarification
        if drift_result["has_drift"]:
            session["state"] = "ASK_GOAL_CLARIFICATION"
            return ChatMessageResponse(
                session_id=payload.session_id,
                state=session["state"],
                data_collected=data,
                message=drift_result["drift_message"] + "\n\nPlease reply: 'Follow AI recommendation' or 'Keep my original goal'"
            )
        
        # No drift, proceed normally
        # Generate ML-based recommendation
        rec = recommender.recommend(
            profile={
                "sex": data["sex"],
                "age": data["age"],
                "height_m": data["height_m"],
                "weight_kg": data["weight_kg"],
                "hypertension": data["hypertension"],
                "diabetes": data["diabetes"],
            },
            wants_videos=False  # No videos yet
        )

        # Store recommendation for later
        session["recommendation"] = rec
        
        # Build a friendly response text
        plan = rec["plan"]
        msg = ""
        
        # Add doctor warning if health conditions exist
        if has_conditions:
            msg += "⚠️ IMPORTANT: Please consult your doctor before starting any new workout plan.\n\n"
        
        msg += f"✅ {data['name']}, here's your personalized plan (ML-based):\n\n"
        
        msg += "📊 YOUR STATS\n"
        msg += f"• BMI: {rec['bmi']} ({rec['level']})\n"
        msg += f"• Fitness Goal: {plan['fitness_goal']}\n"
        msg += f"• Plan Type: {plan['fitness_type']}\n\n"
        
        msg += "🏋️ RECOMMENDED EXERCISES\n"
        exercises = plan['exercises'].split(',') if ',' in plan['exercises'] else [plan['exercises']]
        for ex in exercises:
            msg += f"• {ex.strip()}\n"
        msg += "\n"
        
        msg += "🧰 EQUIPMENT NEEDED\n"
        equipment = plan['equipment'].split(',') if ',' in plan['equipment'] else [plan['equipment']]
        for eq in equipment:
            msg += f"• {eq.strip()}\n"
        msg += "\n"
        
        msg += "🥗 DIET RECOMMENDATIONS\n"
        # Split by semicolon, comma, or 'and' to handle various formats
        diet_text = plan['diet']
        # Replace common separators
        diet_text = diet_text.replace(';', ',')
        diet_text = diet_text.replace(' and ', ',')
        diets = [d.strip() for d in diet_text.split(',') if d.strip()]
        for diet in diets:
            msg += f"• {diet}\n"
        msg += "\n"
        
        msg += f"📌 EXPERT RECOMMENDATION\n{plan['recommendation']}\n\n"
        
        session["state"] = "ASK_VIDEOS"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=msg + "Would you like me to suggest some YouTube workout videos as well? (Yes/No)"
        )

    if state == "ASK_GOAL_CLARIFICATION":
        # User responded to goal drift detection
        response = text.lower()
        
        if "ai" in response or "recommendation" in response or "follow" in response:
            # User wants to follow AI recommendation
            data["user_chose_ai_goal"] = True
            data["clarification"] = "Followed AI recommendation"
        else:
            # User wants to keep original goal
            data["user_chose_ai_goal"] = False
            data["clarification"] = "Kept original goal"
        
        # Now proceed with recommendation (will use original ML prediction either way)
        has_conditions = data["hypertension"] == "Yes" or data["diabetes"] == "Yes"
        
        rec = recommender.recommend(
            profile={
                "sex": data["sex"],
                "age": data["age"],
                "height_m": data["height_m"],
                "weight_kg": data["weight_kg"],
                "hypertension": data["hypertension"],
                "diabetes": data["diabetes"],
            },
            wants_videos=False
        )

        # Store recommendation for later
        session["recommendation"] = rec
        
        # Build a friendly response text
        plan = rec["plan"]
        msg = ""
        
        # Add acknowledgment of user's choice
        if data["user_chose_ai_goal"]:
            msg += "✅ Great choice! Following the AI recommendation based on your stats.\\n\\n"
        else:
            msg += "✅ Understood! We'll respect your goal preference.\\n\\n"
        
        # Add doctor warning if health conditions exist
        if has_conditions:
            msg += "⚠️ IMPORTANT: Please consult your doctor before starting any new workout plan.\\n\\n"
        
        msg += f"✅ {data['name']}, here's your personalized plan (ML-based):\\n\\n"
        
        msg += "📊 YOUR STATS\\n"
        msg += f"• BMI: {rec['bmi']} ({rec['level']})\\n"
        msg += f"• Fitness Goal: {plan['fitness_goal']}\\n"
        msg += f"• Plan Type: {plan['fitness_type']}\\n\\n"
        
        msg += "🏋️ RECOMMENDED EXERCISES\\n"
        exercises = plan['exercises'].split(',') if ',' in plan['exercises'] else [plan['exercises']]
        for ex in exercises:
            msg += f"• {ex.strip()}\\n"
        msg += "\\n"
        
        msg += "🧰 EQUIPMENT NEEDED\\n"
        equipment = plan['equipment'].split(',') if ',' in plan['equipment'] else [plan['equipment']]
        for eq in equipment:
            msg += f"• {eq.strip()}\\n"
        msg += "\\n"
        
        msg += "🥗 DIET RECOMMENDATIONS\\n"
        diet_text = plan['diet']
        diet_text = diet_text.replace(';', ',')
        diet_text = diet_text.replace(' and ', ',')
        diets = [d.strip() for d in diet_text.split(',') if d.strip()]
        for diet in diets:
            msg += f"• {diet}\\n"
        msg += "\\n"
        
        msg += f"📌 EXPERT RECOMMENDATION\\n{plan['recommendation']}\\n\\n"
        
        session["state"] = "ASK_VIDEOS"
        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=msg + "Would you like me to suggest some YouTube workout videos as well? (Yes/No)"
        )

    if state == "ASK_VIDEOS":
        wants_videos = normalize_yes_no(text) == "Yes"
        data["wants_videos"] = wants_videos
        session["state"] = "DONE"
        
        if wants_videos:
            # Retrieve stored recommendation and add videos
            rec = session.get("recommendation")
            if rec:
                # Get YouTube videos
                rec_with_videos = recommender.recommend(
                    profile={
                        "sex": data["sex"],
                        "age": data["age"],
                        "height_m": data["height_m"],
                        "weight_kg": data["weight_kg"],
                        "hypertension": data["hypertension"],
                        "diabetes": data["diabetes"],
                    },
                    wants_videos=True
                )
                
                msg = "▶️ RECOMMENDED WORKOUT VIDEOS\n\n"
                if rec_with_videos["workouts"]:
                    for i, w in enumerate(rec_with_videos["workouts"], 1):
                        msg += f"{i}. {w['title']}\n"
                        msg += f"   ⏱ Duration: {w['duration']} min\n"
                        msg += f"   🔗 Watch: {w['youtube_link']}\n\n"
                    msg += "Good luck with your fitness journey! 💪"
                else:
                    msg = "I couldn't find specific videos at the moment, but good luck with your fitness journey! 💪"
            else:
                msg = "Good luck with your fitness journey! 💪"
        else:
            msg = "No problem! Good luck with your fitness journey! 💪"

        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=msg
        )

    # If already done:
    return ChatMessageResponse(
        session_id=payload.session_id,
        state=session["state"],
        data_collected=data,
        message="If you want, type 'restart' to begin again."
    )


@app.post("/recommend", response_model=RecommendationResponse)
def recommend_direct(req: RecommendationRequest):
    rec = recommender.recommend(
        profile={
            "sex": req.sex,
            "age": req.age,
            "height_m": req.height_m,
            "weight_kg": req.weight_kg,
            "hypertension": req.hypertension,
            "diabetes": req.diabetes,
        },
        wants_videos=req.wants_videos
    )

    return RecommendationResponse(
        name=req.name,
        bmi=rec["bmi"],
        level=rec["level"],
        plan=rec["plan"],
        workouts=rec["workouts"],
        safety_note="General guidance only. Consult a professional for medical concerns."
    )
