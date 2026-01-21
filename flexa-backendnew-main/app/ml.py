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
