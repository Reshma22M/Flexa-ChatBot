"""
Test Goal Drift Detection Feature
This demonstrates how the ML model detects conflicts between user's stated goal and predicted goal
"""
from app.ml import FlexaRecommender

def test_goal_drift():
    recommender = FlexaRecommender()
    
    print("="*60)
    print("GOAL DRIFT DETECTION TEST")
    print("="*60)
    
    # Test Case 1: User says "weight loss" but BMI suggests weight gain
    print("\n\n🔍 TEST CASE 1: User with low BMI wants to lose weight")
    print("-" * 60)
    profile1 = {
        "sex": "Female",
        "age": 25,
        "height_m": 1.70,
        "weight_kg": 48,  # Very low weight - BMI ~16.6 (Underweight)
        "hypertension": "No",
        "diabetes": "No"
    }
    
    drift1 = recommender.detect_goal_drift(profile1, "I want to lose weight")
    
    print(f"📊 User Stats: Age {profile1['age']}, Height {profile1['height_m']}m, Weight {profile1['weight_kg']}kg")
    print(f"💬 Stated Problem: 'I want to lose weight'")
    print(f"📈 BMI: {drift1['bmi']} ({drift1['bmi_level']})")
    print(f"🤖 AI Predicted Goal: {drift1['predicted_goal']}")
    print(f"⚠️  Drift Detected: {drift1['has_drift']}")
    if drift1['has_drift']:
        print(f"\n💡 AI Message to User:\n{drift1['drift_message']}")
    
    # Test Case 2: User says "weight gain" but BMI suggests weight loss
    print("\n\n🔍 TEST CASE 2: User with high BMI wants to gain weight")
    print("-" * 60)
    profile2 = {
        "sex": "Male",
        "age": 30,
        "height_m": 1.75,
        "weight_kg": 95,  # High weight - BMI ~31 (Obese)
        "hypertension": "No",
        "diabetes": "No"
    }
    
    drift2 = recommender.detect_goal_drift(profile2, "I want to build muscle and gain weight")
    
    print(f"📊 User Stats: Age {profile2['age']}, Height {profile2['height_m']}m, Weight {profile2['weight_kg']}kg")
    print(f"💬 Stated Problem: 'I want to build muscle and gain weight'")
    print(f"📈 BMI: {drift2['bmi']} ({drift2['bmi_level']})")
    print(f"🤖 AI Predicted Goal: {drift2['predicted_goal']}")
    print(f"⚠️  Drift Detected: {drift2['has_drift']}")
    if drift2['has_drift']:
        print(f"\n💡 AI Message to User:\n{drift2['drift_message']}")
    
    # Test Case 3: No drift - goal matches prediction
    print("\n\n🔍 TEST CASE 3: User goal matches AI prediction (no drift)")
    print("-" * 60)
    profile3 = {
        "sex": "Female",
        "age": 28,
        "height_m": 1.65,
        "weight_kg": 75,  # BMI ~27.5 (Overweight)
        "hypertension": "No",
        "diabetes": "No"
    }
    
    drift3 = recommender.detect_goal_drift(profile3, "I want to lose weight")
    
    print(f"📊 User Stats: Age {profile3['age']}, Height {profile3['height_m']}m, Weight {profile3['weight_kg']}kg")
    print(f"💬 Stated Problem: 'I want to lose weight'")
    print(f"📈 BMI: {drift3['bmi']} ({drift3['bmi_level']})")
    print(f"🤖 AI Predicted Goal: {drift3['predicted_goal']}")
    print(f"⚠️  Drift Detected: {drift3['has_drift']}")
    if not drift3['has_drift']:
        print(f"✅ No conflict detected - user goal aligns with AI recommendation")
    
    print("\n" + "="*60)
    print("ACADEMIC VALUE:")
    print("="*60)
    print("""
    This feature demonstrates:
    
    1️⃣ BEHAVIORAL ANALYTICS
       - Analyzing user statements vs physiological data
       - Pattern recognition in user goals vs body metrics
    
    2️⃣ CONSISTENCY CHECKING
       - Cross-validation between stated intentions and ML predictions
       - Conflict resolution through intelligent prompting
    
    3️⃣ INTELLIGENT SYSTEMS
       - Context-aware decision making
       - Proactive user guidance based on data analysis
       - Human-in-the-loop validation
    
    4️⃣ PERSONALIZATION
       - BMI-contextualized messaging
       - Adaptive communication based on health metrics
       - User autonomy in final decision
    
    This approach improves user outcomes by preventing potentially
    harmful goal selections while respecting user autonomy.
    """)

if __name__ == "__main__":
    test_goal_drift()
