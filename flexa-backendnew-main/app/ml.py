import json
import joblib
import pandas as pd
from typing import Dict, Any, List

from .utils import compute_bmi, bmi_level, normalize_yes_no, normalize_sex

MODEL_PATH = "models/flexa_plan_model.joblib"
WORKOUTS_PATH = "data/workouts.json"


class FlexaRecommender:
    """
    Loads the trained ML pipeline + the original dataset,
    and can produce a recommended plan + relevant workouts.
    """

    def __init__(self):
        bundle = joblib.load(MODEL_PATH)
        self.pipeline = bundle["pipeline"]
        self.df: pd.DataFrame = bundle["dataset"]

        with open(WORKOUTS_PATH, "r", encoding="utf-8") as f:
            self.workouts_data = json.load(f)["workouts"]

    def recommend(self, profile: Dict[str, Any], wants_videos: bool = True) -> Dict[str, Any]:
        """
        profile must contain:
        sex, age, height_m, weight_kg, hypertension, diabetes
        """
        sex = normalize_sex(profile["sex"])
        age = int(profile["age"])
        height_m = float(profile["height_m"])
        weight_kg = float(profile["weight_kg"])
        hypertension = normalize_yes_no(profile["hypertension"])
        diabetes = normalize_yes_no(profile["diabetes"])

        bmi = compute_bmi(height_m, weight_kg)
        level = bmi_level(bmi)

        # Build a single-row dataframe for prediction (must match training columns)
        X = pd.DataFrame([{
            "Sex": sex,
            "Age": age,
            "Height": height_m,
            "Weight": weight_kg,
            "Hypertension": hypertension,
            "Diabetes": diabetes,
            "BMI": bmi,
            "Level": level
        }])

        # Predict closest plan ID
        pred_id = int(self.pipeline.predict(X)[0])

        # Fetch that plan row
        row = self.df[self.df["ID"] == pred_id].iloc[0]

        plan = {
            "id": int(row["ID"]),
            "fitness_goal": row["Fitness Goal"],
            "fitness_type": row["Fitness Type"],
            "exercises": row["Exercises"],
            "equipment": row["Equipment"],
            "diet": row["Diet"],
            "recommendation": row["Recommendation"]
        }

        workouts = []
        if wants_videos:
            workouts = self._pick_workouts(plan_goal=plan["fitness_goal"], plan_type=plan["fitness_type"])

        return {
            "bmi": round(float(bmi), 2),
            "level": level,
            "plan": plan,
            "workouts": workouts
        }

    def _pick_workouts(self, plan_goal: str, plan_type: str) -> List[Dict[str, Any]]:
        """
        Map your dataset goal/type to the workout JSON goal/category.
        """
        goal_map = {
            "Weight Loss": "weight_loss",
            "Weight Gain": "muscle_gain",
            "Toning": "toning",
            "Flexibility": "flexibility"
        }

        # Default mapping; adjust based on your dataset wording
        target_goal = goal_map.get(str(plan_goal).strip(), None)

        # Filter workouts
        pool = self.workouts_data
        if target_goal:
            pool = [w for w in pool if str(w.get("goal")).strip() == target_goal]

        # Optional: also align by category if possible
        # Example: muscular fitness -> strength
        type_map = {
            "Muscular Fitness": "Strength",
            "Cardio": "Cardio",
            "HIIT": "HIIT",
            "Yoga": "Yoga"
        }
        target_cat = type_map.get(str(plan_type).strip(), None)
        if target_cat:
            filtered = [w for w in pool if str(w.get("category")).strip().lower() == target_cat.lower()]
            if filtered:
                pool = filtered

        # Return top 3 (simple)
        return pool[:3]

    def detect_goal_drift(self, profile: Dict[str, Any], stated_problem: str) -> Dict[str, Any]:
        """
        Detect if user's stated problem conflicts with ML-predicted fitness goal.
        Returns drift detection result with suggested clarification.
        """
        # Get ML prediction
        rec = self.recommend(profile, wants_videos=False)
        predicted_goal = rec["plan"]["fitness_goal"]
        
        # Map user's stated problem to expected goals
        problem_goal_map = {
            "weight loss": ["Weight Loss", "Toning"],
            "lose weight": ["Weight Loss", "Toning"],
            "fat loss": ["Weight Loss"],
            "weight gain": ["Weight Gain"],
            "gain weight": ["Weight Gain"],
            "build muscle": ["Weight Gain"],
            "muscle gain": ["Weight Gain"],
            "tone up": ["Toning"],
            "toning": ["Toning"],
            "flexibility": ["Flexibility"],
            "stretching": ["Flexibility"],
        }
        
        # Find expected goals based on stated problem
        stated_lower = stated_problem.lower()
        expected_goals = []
        for key, goals in problem_goal_map.items():
            if key in stated_lower:
                expected_goals.extend(goals)
        
        # Check for drift
        has_drift = False
        drift_message = ""
        
        if expected_goals and predicted_goal not in expected_goals:
            has_drift = True
            bmi = rec["bmi"]
            bmi_level = rec["level"]
            
            # Generate contextual drift message
            if "weight loss" in stated_lower or "lose weight" in stated_lower:
                if predicted_goal == "Weight Gain":
                    drift_message = f"🤔 GOAL DRIFT DETECTED\n\nYour BMI is {bmi} ({bmi_level}), and based on your physical stats, our AI suggests a '{predicted_goal}' plan. However, you mentioned wanting to lose weight.\n\nThis could mean:\n• Your current weight is already low for your height\n• Gaining muscle mass might be healthier than losing weight\n\nWould you like to reconsider your goal, or shall we proceed with your stated preference?"
            elif "weight gain" in stated_lower or "gain weight" in stated_lower or "build muscle" in stated_lower:
                if predicted_goal == "Weight Loss":
                    drift_message = f"🤔 GOAL DRIFT DETECTED\n\nYour BMI is {bmi} ({bmi_level}), and based on your physical stats, our AI suggests a '{predicted_goal}' plan. However, you mentioned wanting to gain weight or build muscle.\n\nThis could mean:\n• Your current weight is higher than ideal for your height\n• Losing fat first might be healthier before building muscle\n\nWould you like to reconsider your goal, or shall we proceed with your stated preference?"
            else:
                drift_message = f"🤔 GOAL DRIFT DETECTED\n\nBased on your stats (BMI: {bmi}, {bmi_level}), our AI recommends a '{predicted_goal}' plan, which differs from what you described.\n\nWould you like to reconsider, or proceed with your original goal?"
        
        return {
            "has_drift": has_drift,
            "predicted_goal": predicted_goal,
            "stated_problem": stated_problem,
            "drift_message": drift_message,
            "bmi": rec["bmi"],
            "bmi_level": rec["level"]
        }
