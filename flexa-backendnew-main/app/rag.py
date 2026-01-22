"""
RAG (Retrieval-Augmented Generation) Module for Flexa AI
Uses ChromaDB + sentence-transformers for fitness knowledge retrieval
"""

import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class FlexaRAG:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize RAG with lightweight model optimized for Render free tier"""
        print("Initializing Flexa RAG system...")
        
        # Use lightweight model (~80MB) - perfect for free tier
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("fitness_knowledge")
            print(f"✅ Loaded existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="fitness_knowledge",
                metadata={"description": "Fitness and nutrition knowledge base"}
            )
            self._populate_knowledge_base()
            print(f"✅ Created new collection with {self.collection.count()} documents")
    
    def _populate_knowledge_base(self):
        """Populate with fitness knowledge - exercises, nutrition, tips"""
        
        fitness_docs = [
            {
                "content": "Push-ups are a compound exercise that work chest, shoulders, and triceps. Proper form: hands shoulder-width apart, body straight, lower until chest nearly touches ground, push back up. Start with knee push-ups if regular ones are too difficult.",
                "metadata": {"category": "exercise", "muscle_group": "chest", "difficulty": "beginner"},
                "id": "doc_1"
            },
            {
                "content": "Squats are the king of lower body exercises. They target quadriceps, hamstrings, glutes, and core. Keep feet shoulder-width apart, chest up, push hips back like sitting in a chair, lower until thighs are parallel to ground. Never let knees go past toes.",
                "metadata": {"category": "exercise", "muscle_group": "legs", "difficulty": "beginner"},
                "id": "doc_2"
            },
            {
                "content": "Protein is essential for muscle building and repair. Aim for 1.6-2.2g per kg of body weight daily. Good sources: chicken breast (31g protein per 100g), eggs (6g per egg), Greek yogurt (10g per 100g), lentils (9g per 100g), tofu (8g per 100g).",
                "metadata": {"category": "nutrition", "topic": "protein", "importance": "high"},
                "id": "doc_3"
            },
            {
                "content": "Weight loss requires a caloric deficit: consume fewer calories than you burn. Safe rate: 0.5-1kg per week. Calculate TDEE (Total Daily Energy Expenditure), subtract 500 calories for gradual loss. Combine with exercise for best results. Never go below 1200 calories (women) or 1500 calories (men).",
                "metadata": {"category": "nutrition", "topic": "weight_loss", "importance": "critical"},
                "id": "doc_4"
            },
            {
                "content": "Deadlifts are a full-body compound movement. They work back, glutes, hamstrings, core, and grip strength. Proper form is CRITICAL to prevent injury: feet hip-width, grip bar outside legs, keep back straight, push through heels, drive hips forward. Start light and master form.",
                "metadata": {"category": "exercise", "muscle_group": "back", "difficulty": "advanced"},
                "id": "doc_5"
            },
            {
                "content": "Carbohydrates are your body's primary energy source. Complex carbs (oats, brown rice, sweet potato, quinoa) provide sustained energy. Simple carbs (fruits, honey) give quick energy. Aim for 45-65% of daily calories from carbs. Timing matters: eat carbs before/after workouts for optimal performance.",
                "metadata": {"category": "nutrition", "topic": "carbohydrates", "importance": "high"},
                "id": "doc_6"
            },
            {
                "content": "Rest and recovery are as important as training. Muscles grow during rest, not during workouts. Aim for 7-9 hours of sleep. Rest days prevent overtraining and injury. Active recovery (light walking, yoga) helps. Never train same muscle group on consecutive days.",
                "metadata": {"category": "recovery", "topic": "rest", "importance": "critical"},
                "id": "doc_7"
            },
            {
                "content": "Plank is the ultimate core exercise. It strengthens abs, back, and shoulders. Proper form: forearms on ground, body straight line from head to heels, engage core, don't let hips sag. Hold 30-60 seconds, repeat 3 sets. Progress to side planks for obliques.",
                "metadata": {"category": "exercise", "muscle_group": "core", "difficulty": "beginner"},
                "id": "doc_8"
            },
            {
                "content": "Hydration is crucial for performance and health. Drink at least 2-3 liters of water daily, more when exercising. Signs of dehydration: dark urine, fatigue, headache, dizziness. During workouts: 200-300ml every 15-20 minutes. Electrolytes important for intense exercise over 1 hour.",
                "metadata": {"category": "nutrition", "topic": "hydration", "importance": "critical"},
                "id": "doc_9"
            },
            {
                "content": "Progressive overload is key to muscle growth. Gradually increase weight, reps, or sets over time. Your body adapts to stress by getting stronger. Aim to increase weight by 2.5-5kg or add 1-2 reps each week. Track your workouts to ensure progress.",
                "metadata": {"category": "training_principle", "topic": "progressive_overload", "importance": "high"},
                "id": "doc_10"
            },
            {
                "content": "Burpees are a full-body cardio exercise. They burn calories fast and improve cardiovascular fitness. How to: start standing, drop into squat, kick feet back to plank, do a push-up, jump feet to hands, explosive jump up. Modify by removing push-up or jump.",
                "metadata": {"category": "exercise", "muscle_group": "full_body", "difficulty": "intermediate"},
                "id": "doc_11"
            },
            {
                "content": "Healthy fats are essential for hormone production and vitamin absorption. Include omega-3s (salmon, walnuts, flaxseed), avocado, olive oil, nuts. Aim for 20-35% of daily calories from fat. Avoid trans fats completely. Fats are calorie-dense (9 calories per gram) so watch portions.",
                "metadata": {"category": "nutrition", "topic": "fats", "importance": "high"},
                "id": "doc_12"
            },
            {
                "content": "HIIT (High-Intensity Interval Training) alternates short bursts of intense exercise with recovery periods. Burns fat efficiently in less time. Example: 30 seconds sprint, 30 seconds walk, repeat 10 times. Great for weight loss and improving cardiovascular fitness. 2-3 times per week maximum.",
                "metadata": {"category": "cardio", "topic": "HIIT", "importance": "high"},
                "id": "doc_13"
            },
            {
                "content": "Lunges strengthen legs and glutes while improving balance. Forward lunge: step forward, lower until both knees at 90 degrees, push back to start. Keep front knee behind toes, chest up. Reverse lunges are easier on knees. Walking lunges increase difficulty.",
                "metadata": {"category": "exercise", "muscle_group": "legs", "difficulty": "beginner"},
                "id": "doc_14"
            },
            {
                "content": "Pre-workout nutrition fuels your training. Eat 1-2 hours before: carbs for energy (banana, oatmeal, toast), small amount of protein. Avoid heavy fats and fiber right before training. If training early morning, at least have a banana or energy drink.",
                "metadata": {"category": "nutrition", "topic": "pre_workout", "importance": "medium"},
                "id": "doc_15"
            },
            {
                "content": "Post-workout nutrition helps recovery and muscle growth. Within 30-60 minutes after training: protein (20-30g) and carbs (0.5-0.7g per kg body weight). Examples: protein shake with banana, chicken with rice, Greek yogurt with granola. The 'anabolic window' is real!",
                "metadata": {"category": "nutrition", "topic": "post_workout", "importance": "high"},
                "id": "doc_16"
            },
            {
                "content": "BMI (Body Mass Index) is calculated as weight(kg) / height(m)². Under 18.5: underweight, 18.5-24.9: normal, 25-29.9: overweight, 30+: obese. Note: BMI doesn't account for muscle mass. Very muscular people may have high BMI but low body fat. Use in combination with other metrics.",
                "metadata": {"category": "health_metric", "topic": "BMI", "importance": "medium"},
                "id": "doc_17"
            },
            {
                "content": "Warm-up prevents injury and improves performance. Spend 5-10 minutes before training: light cardio (jogging, jumping jacks), dynamic stretches (arm circles, leg swings), movement-specific warm-up with light weights. Never stretch cold muscles. Save static stretching for after workout.",
                "metadata": {"category": "training_principle", "topic": "warm_up", "importance": "critical"},
                "id": "doc_18"
            },
            {
                "content": "Pull-ups and chin-ups are excellent for back and arm development. Pull-ups (palms away) emphasize lats, chin-ups (palms toward) emphasize biceps. Can't do one yet? Start with negatives (jump up, lower slowly) or assisted pull-ups. Progress takes time - be patient!",
                "metadata": {"category": "exercise", "muscle_group": "back", "difficulty": "advanced"},
                "id": "doc_19"
            },
            {
                "content": "Yoga improves flexibility, balance, and mental well-being. Great for active recovery days. Benefits: reduces muscle soreness, prevents injury, improves mobility, reduces stress. Try beginner classes first. Even 15 minutes daily makes a difference. Popular styles: Hatha (gentle), Vinyasa (flowing), Yin (deep stretching).",
                "metadata": {"category": "flexibility", "topic": "yoga", "importance": "medium"},
                "id": "doc_20"
            }
        ]
        
        # Add documents to collection
        self.collection.add(
            documents=[doc["content"] for doc in fitness_docs],
            metadatas=[doc["metadata"] for doc in fitness_docs],
            ids=[doc["id"] for doc in fitness_docs]
        )
        
        print(f"✅ Added {len(fitness_docs)} documents to knowledge base")
    
    def query(self, question: str, n_results: int = 3) -> List[Dict]:
        """Query the knowledge base and return relevant information"""
        
        # Search for relevant documents
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "relevance_score": 1.0 - results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return formatted_results
    
    def answer_question(self, question: str) -> str:
        """Get an answer to a fitness question using RAG"""
        
        # Query knowledge base
        results = self.query(question, n_results=2)
        
        if not results:
            return "I don't have specific information about that. Let me connect you with our ML recommendations based on your profile!"
        
        # Combine top results into an answer
        answer_parts = []
        for i, result in enumerate(results, 1):
            if result['relevance_score'] > 0.3:  # Only include relevant results
                answer_parts.append(f"📚 {result['content']}")
        
        if answer_parts:
            return "\n\n".join(answer_parts)
        else:
            return "I found some information, but I'm not confident it fully answers your question. Could you rephrase or ask something more specific?"
    
    def add_document(self, content: str, metadata: Dict, doc_id: str):
        """Add a new document to the knowledge base"""
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"✅ Added document: {doc_id}")

# Global RAG instance (initialized once on server startup)
_rag_instance = None

def get_rag_instance():
    """Get or create RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = FlexaRAG()
    return _rag_instance
