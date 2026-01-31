# api_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import uuid

# Import the college simulator
from infcollege import CollegeSimulator

app = FastAPI()

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and CRA dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active game sessions
games: Dict[str, CollegeSimulator] = {}

# Pydantic models for request/response
class GameCreateResponse(BaseModel):
    game_id: str
    message: str

class AnswerData(BaseModel):
    id: str
    text: str

class QuestionResponse(BaseModel):
    question: str
    year: str
    major: Optional[str] = None
    answers: List[AnswerData]
    question_number: int
    total_questions: int = 40
    game_over: bool = False
    game_over_message: Optional[str] = None

class ChoiceRequest(BaseModel):
    game_id: str
    choice_id: str


@app.post("/api/game/new", response_model=GameCreateResponse)
async def create_game():
    """Create a new game session"""
    api_key = os.environ.get('GEMINI_KEY')
    
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_KEY not configured")
    
    game_id = str(uuid.uuid4())
    games[game_id] = CollegeSimulator(api_key)
    
    return GameCreateResponse(
        game_id=game_id,
        message="Game created successfully"
    )


@app.get("/api/game/{game_id}/question", response_model=QuestionResponse)
async def get_question(game_id: str):
    """Get the current/next question for a game"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    simulator = games[game_id]
    
    try:
        question_data = simulator.generate_question()
        
        # Store the question for later use when submitting choice
        simulator.current_question = question_data
        
        # Remove effects from answers - only send id and text
        clean_answers = [
            AnswerData(
                id=answer["id"],
                text=answer["text"]
            )
            for answer in question_data["answers"]
        ]
        
        return QuestionResponse(
            question=question_data["question"],
            year=question_data["year"],
            major=simulator.major,
            answers=clean_answers,
            question_number=simulator.question_count,
            total_questions=40,
            game_over=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.post("/api/game/choice", response_model=QuestionResponse)
async def submit_choice(choice: ChoiceRequest):
    """Submit a choice and get the next question"""
    if choice.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    simulator = games[choice.game_id]
    
    try:
        # Check if we have a current question
        if not hasattr(simulator, 'current_question') or simulator.current_question is None:
            raise HTTPException(status_code=400, detail="No active question")
        
        # Apply the choice
        simulator.apply_choice(simulator.current_question, choice.choice_id)
        
        # Check for game over conditions
        game_over = False
        game_over_message = None
        
        # Check crisis events (non-terminal)
        if simulator.question_count > 1:
            crisis_events = simulator.check_stat_crisis_events()
            
            # Check for dropout
            if simulator.is_past_first_year():
                simulator.check_dropout_warning()
                dropout_result = simulator.check_dropout_resolution()
                
                if dropout_result == 'dropout':
                    game_over = True
                    game_over_message = f"After {simulator.question_count} questions into your {simulator.major} degree, the weight of your struggles became too much to bear. You've decided to take a leave of absence from college."
        
        # Check graduation
        if simulator.check_graduation():
            game_over = True
            avg_stat = simulator.stats.get_average()
            
            if avg_stat >= 80:
                game_over_message = f"🎓 Congratulations! You've graduated with your degree in {simulator.major} - Summa Cum Laude! You excelled in all aspects of college life!"
            elif avg_stat >= 70:
                game_over_message = f"🎓 Congratulations! You've graduated with your degree in {simulator.major} - Magna Cum Laude! You had a well-rounded college experience!"
            elif avg_stat >= 60:
                game_over_message = f"🎓 Congratulations! You've graduated with your degree in {simulator.major} - Cum Laude! You successfully balanced the challenges of college!"
            else:
                game_over_message = f"🎓 Congratulations! You've graduated with your degree in {simulator.major}! College was tough, but you persevered!"
        
        if game_over:
            return QuestionResponse(
                question=game_over_message or "",
                year=simulator.get_year_label(),
                major=simulator.major,
                answers=[],
                question_number=simulator.question_count,
                total_questions=40,
                game_over=True,
                game_over_message=game_over_message
            )
        
        # Generate next question
        question_data = simulator.generate_question()
        simulator.current_question = question_data  # Store for next choice submission
        
        # Remove effects from answers
        clean_answers = [
            AnswerData(
                id=answer["id"],
                text=answer["text"]
            )
            for answer in question_data["answers"]
        ]
        
        return QuestionResponse(
            question=question_data["question"],
            year=question_data["year"],
            major=simulator.major,
            answers=clean_answers,
            question_number=simulator.question_count,
            total_questions=40,
            game_over=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing choice: {str(e)}")


@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """Delete a game session"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del games[game_id]
    return {"message": "Game deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
