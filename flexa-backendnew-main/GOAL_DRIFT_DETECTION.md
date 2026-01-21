# Goal Drift Detection Feature

## Overview
The Goal Drift Detection feature uses machine learning to identify conflicts between a user's stated fitness goal and what their physical metrics suggest would be optimal. This ensures users receive health-appropriate recommendations and prevents potentially harmful goal selections.

## How It Works

### 1. Data Collection
The system collects:
- User's stated problem/goal (e.g., "I want to lose weight")
- Physical metrics: sex, age, height, weight
- Health conditions: hypertension, diabetes

### 2. ML Prediction
The trained ML model analyzes physical metrics to predict the optimal fitness goal based on:
- BMI calculation
- BMI category (Underweight, Normal, Overweight, Obese)
- Historical training data patterns

### 3. Goal Comparison
The system compares:
- **Stated Goal**: Extracted from user's problem description
- **Predicted Goal**: ML model's recommendation

### 4. Drift Detection Logic

```python
User Says: "weight loss" → Expected Goals: ["Weight Loss", "Toning"]
ML Predicts: "Weight Gain"
Result: ⚠️ DRIFT DETECTED
```

### 5. Intelligent Response
When drift is detected:
- Shows user their BMI and category
- Explains the conflict
- Provides context (e.g., "Your weight is already low for your height")
- Offers choice: Follow AI recommendation or keep original goal

## Example Scenarios

### Scenario 1: Underweight User Wants Weight Loss
```
User Input: "I want to lose weight"
Stats: Height 1.70m, Weight 48kg → BMI 16.6 (Underweight)
ML Prediction: "Weight Gain"

AI Response:
"🤔 GOAL DRIFT DETECTED

Your BMI is 16.6 (Underweight), and based on your physical stats, 
our AI suggests a 'Weight Gain' plan. However, you mentioned wanting 
to lose weight.

This could mean:
• Your current weight is already low for your height
• Gaining muscle mass might be healthier than losing weight

Would you like to reconsider your goal, or shall we proceed with 
your stated preference?"
```

### Scenario 2: Overweight User Wants Weight Gain
```
User Input: "I want to build muscle and gain weight"
Stats: Height 1.75m, Weight 95kg → BMI 31.0 (Obese)
ML Prediction: "Weight Loss"

AI Response:
"🤔 GOAL DRIFT DETECTED

Your BMI is 31.0 (Obese), and based on your physical stats, our AI 
suggests a 'Weight Loss' plan. However, you mentioned wanting to 
gain weight or build muscle.

This could mean:
• Your current weight is higher than ideal for your height
• Losing fat first might be healthier before building muscle

Would you like to reconsider your goal, or shall we proceed with 
your stated preference?"
```

### Scenario 3: No Drift (Goal Aligned)
```
User Input: "I want to lose weight"
Stats: Height 1.65m, Weight 75kg → BMI 27.5 (Overweight)
ML Prediction: "Weight Loss"

Result: ✅ No drift detected - proceeds normally
```

## Implementation Details

### Backend (ml.py)
```python
def detect_goal_drift(self, profile, stated_problem):
    """
    1. Get ML prediction
    2. Map user's problem to expected goals
    3. Compare predicted vs expected
    4. Generate contextual drift message
    """
```

### State Machine (main.py)
```
ASK_NAME → ASK_PROBLEM → ASK_SEX → ASK_AGE → 
ASK_HEIGHT → ASK_WEIGHT → ASK_HYPERTENSION → ASK_DIABETES →
[GOAL DRIFT CHECK] → 
  If Drift: ASK_GOAL_CLARIFICATION → [proceed]
  No Drift: [proceed directly]
→ ASK_VIDEOS → DONE
```

### API Flow
```
POST /chat/message
{
  "session_id": "...",
  "user_message": "No" (to diabetes question)
}

↓ Triggers drift detection ↓

Response (if drift):
{
  "state": "ASK_GOAL_CLARIFICATION",
  "message": "🤔 GOAL DRIFT DETECTED...",
  "data_collected": {...}
}

User responds: "Follow AI recommendation" or "Keep my original goal"

↓ System proceeds with recommendation ↓
```

## Academic Value

### 1. Behavioral Analytics
- **Pattern Recognition**: Identifying discrepancies between stated intentions and physiological data
- **User Behavior Analysis**: Understanding goal-setting patterns across different BMI categories
- **Decision-Making Insights**: Studying how users respond to AI recommendations vs. personal preferences

### 2. Consistency Checking
- **Cross-Validation**: Verifying alignment between multiple data sources (text input + metrics)
- **Conflict Resolution**: Implementing intelligent prompts to resolve data inconsistencies
- **Data Quality**: Ensuring recommendation accuracy through multi-factor validation

### 3. Intelligent Systems
- **Context-Aware Computing**: Adapting responses based on user's physiological context
- **Proactive Assistance**: Intervening before potentially harmful decisions
- **Human-in-the-Loop**: Maintaining user autonomy while providing AI guidance
- **Explainable AI**: Transparent reasoning for why recommendations differ

### 4. Health Informatics
- **Preventive Care**: Identifying potentially unhealthy goal selections
- **Personalized Medicine**: Tailoring recommendations to individual health profiles
- **Risk Assessment**: Flagging high-risk scenarios (e.g., underweight person wanting weight loss)

## Research Applications

### Publications
This feature could contribute to papers on:
- "Behavioral Consistency Checking in AI Health Applications"
- "Goal Drift Detection Using Physiological Metrics"
- "Human-AI Collaboration in Fitness Recommendation Systems"
- "Preventing Harmful User Intentions through Proactive ML Intervention"

### Metrics to Track
1. **Drift Detection Rate**: % of users with detected drift
2. **User Choice Distribution**: How many follow AI vs. keep original goal
3. **Outcome Correlation**: Relationship between choice and success metrics
4. **BMI Category Patterns**: Drift patterns across different weight categories

### Future Enhancements
1. **Temporal Drift Detection**: Monitor goal consistency over multiple sessions
2. **Activity Pattern Analysis**: Compare stated goals with actual workout behavior
3. **Progressive Recommendation**: Suggest intermediate goals when drift is large
4. **Psychological Profiling**: Understand motivation behind conflicting goals

## Testing

Run the test suite:
```bash
cd flexa-backendnew-main
python test_goal_drift.py
```

This will demonstrate drift detection across multiple scenarios.

## API Usage

The drift detection runs automatically during the chat flow. No additional API calls needed.

State progression:
```
ASK_DIABETES → detect_goal_drift() → 
  [if drift] → ASK_GOAL_CLARIFICATION
  [no drift] → ASK_VIDEOS
```

## Configuration

### Goal Mapping (ml.py)
Modify `problem_goal_map` to customize goal detection:
```python
problem_goal_map = {
    "weight loss": ["Weight Loss", "Toning"],
    "weight gain": ["Weight Gain"],
    "muscle gain": ["Weight Gain"],
    "flexibility": ["Flexibility"],
    # Add more mappings...
}
```

### Drift Messages
Customize messages in `detect_goal_drift()` method for different scenarios.

## Benefits

### For Users
- ✅ Prevents unhealthy goal selections
- ✅ Educates about BMI and healthy ranges
- ✅ Maintains autonomy in final decision
- ✅ Builds trust through transparency

### For System
- ✅ Improves recommendation accuracy
- ✅ Reduces harmful outcomes
- ✅ Demonstrates AI intelligence
- ✅ Creates research opportunities

### For Research
- ✅ Novel approach to user safety
- ✅ Publishable methodology
- ✅ Real-world data collection opportunity
- ✅ Behavioral analytics insights

## Conclusion

Goal Drift Detection represents a sophisticated approach to ensuring user safety while respecting autonomy. By combining ML predictions with behavioral analysis, the system can proactively identify and address potentially harmful goal selections, making it a valuable feature for both practical application and academic research.
