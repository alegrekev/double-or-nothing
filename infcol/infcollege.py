# college_simulator_backend.py

import os
import json
import re
import google.generativeai as genai
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import keyenv

@dataclass
class Stats:
    morale: int = 50
    academics: int = 50
    health: int = 50
    
    def apply_effects(self, effects: Dict[str, Optional[int]]):
        """Apply stat changes and clamp values between 0-100"""
        self.morale = max(0, min(100, self.morale + (effects.get('morale') or 0)))
        self.academics = max(0, min(100, self.academics + (effects.get('academics') or 0)))
        self.health = max(0, min(100, self.health + (effects.get('health') or 0)))
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Decision:
    question_num: int
    question: str
    choice: str
    effects: Dict[str, Optional[int]]


class CollegeSimulator:
    SYSTEM_PROMPT = """You are a college life simulator game master. Your role is to generate realistic college scenarios that create a compelling narrative journey from Year 1 to Graduation.

## Your Task
Generate college life questions/situations with two choice options. Each choice affects three stats: Morale (Mental Health), Academics (Academic Success), and Health (Physical Health). Stats range from 0-100.

## Guidelines
1. **Narrative Continuity**: Base questions on the student's past decisions and current stats (except the first question)
2. **Realistic Scenarios**: Create situations that college students actually face
3. **Balanced Choices**: Both options should have trade-offs; avoid obviously "correct" answers
4. **Stat Effects**: 
   - Use values between -30 to +30 for significant impacts
   - Use null for no effect (treated as 0)
   - Consider cumulative effects on the student's journey
5. **Progression**: Questions should reflect the student's year (freshman, sophomore, junior, senior) and previous choices
6. **Variety**: Mix academic, social, health, financial, and personal scenarios

## Response Format
Always respond with valid JSON in this exact structure:
{
  "question": "The situation/scenario the student faces",
  "year": "Year 1" | "Year 2" | "Year 3" | "Year 4",
  "answers": [
    {
      "id": "A1",
      "text": "First choice description",
      "effects": {
        "morale": <integer or null>,
        "academics": <integer or null>,
        "health": <integer or null>
      }
    },
    {
      "id": "A2",
      "text": "Second choice description",
      "effects": {
        "morale": <integer or null>,
        "academics": <integer or null>,
        "health": <integer or null>
      }
    }
  ]
}

## CRITICAL JSON FORMATTING RULES
- Effect values MUST be integers without the plus sign: use 30, not +30
- Use negative numbers with minus sign: -10 is correct
- Use null (not "null" in quotes) when there is no effect
- Do NOT include any + symbols in the JSON
- Examples: "morale": 15, "academics": -10, "health": null

## Context Awareness
When provided with game state (current stats, past decisions, current year), tailor the question to reflect:
- Consequences of previous choices
- Current stat levels (low health might lead to illness scenarios, low academics to academic probation, etc.)
- Time in college (early years vs. senior year priorities)
- Building a coherent story arc

Generate engaging, realistic scenarios that make the player feel the weight of their decisions throughout their college journey."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.stats = Stats()
        self.decisions: List[Decision] = []
        self.question_count = 0
        self.current_year = 1
        
    def get_year_label(self) -> str:
        """Convert question count to year label"""
        years = {1: "Year 1", 2: "Year 2", 3: "Year 3", 4: "Year 4"}
        # Roughly 10 questions per year for a 40-question game
        year_num = min(4, (self.question_count // 10) + 1)
        return years[year_num]
    
    def build_context_prompt(self) -> str:
        """Build context from previous decisions and current stats"""
        if not self.decisions:
            return "This is the first question. The student is just starting their college journey as a freshman."
        
        context = f"""
Current Game State:
- Year: {self.get_year_label()}
- Current Stats: Morale: {self.stats.morale}, Academics: {self.stats.academics}, Health: {self.stats.health}
- Questions Answered: {self.question_count}

Recent Decisions:
"""
        # Include last 3 decisions for context
        for decision in self.decisions[-3:]:
            context += f"- Q{decision.question_num}: {decision.question}\n  Choice: {decision.choice}\n"
        
        context += "\nGenerate the next question that follows naturally from these past decisions and current stats."
        return context
    
    def clean_json_response(self, response_text: str) -> str:
        """Clean the JSON response to fix common formatting issues"""
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
            if response_text.startswith('json'):
                response_text = '\n'.join(response_text.split('\n')[1:])
        
        # Remove plus signs before numbers in the effects (e.g., +30 -> 30, +15 -> 15)
        # This regex looks for a plus sign followed by digits in the context of JSON values
        response_text = re.sub(r':\s*\+(\d+)', r': \1', response_text)
        
        return response_text.strip()
    
    def generate_question(self) -> Dict:
        """Request Gemini to generate a new question"""
        context = self.build_context_prompt()
        
        prompt = f"{self.SYSTEM_PROMPT}\n\n{context}\n\nRespond ONLY with the JSON object, no additional text."
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract and clean JSON from response
            response_text = self.clean_json_response(response.text)
            
            question_data = json.loads(response_text)
            self.question_count += 1
            
            return question_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            print(f"Cleaned text: {response_text}")
            raise
        except Exception as e:
            print(f"Error generating question: {e}")
            raise
    
    def apply_choice(self, question_data: Dict, choice_id: str):
        """Apply the effects of a chosen answer"""
        choice = next((a for a in question_data['answers'] if a['id'] == choice_id), None)
        
        if not choice:
            raise ValueError(f"Invalid choice ID: {choice_id}")
        
        # Record the decision
        decision = Decision(
            question_num=self.question_count,
            question=question_data['question'],
            choice=choice['text'],
            effects=choice['effects']
        )
        self.decisions.append(decision)
        
        # Apply stat changes
        self.stats.apply_effects(choice['effects'])
    
    def display_question(self, question_data: Dict):
        """Display question in terminal"""
        print("\n" + "="*60)
        print(f"YEAR: {question_data.get('year', self.get_year_label())}")
        print(f"Question #{self.question_count}")
        print("="*60)
        print(f"\n{question_data['question']}\n")
        
        for i, answer in enumerate(question_data['answers'], 1):
            print(f"{i}. {answer['text']}")
            effects = answer['effects']
            effect_str = []
            for stat, value in effects.items():
                if value is not None and value != 0:
                    sign = "+" if value > 0 else ""
                    effect_str.append(f"{stat.capitalize()}: {sign}{value}")
            if effect_str:
                print(f"   Effects: {', '.join(effect_str)}")
            print()
    
    def display_stats(self):
        """Display current stats"""
        print("\n" + "-"*60)
        print("CURRENT STATS")
        print("-"*60)
        print(f"Morale (Mental Health):    {self.stats.morale}/100")
        print(f"Academics:                 {self.stats.academics}/100")
        print(f"Health (Physical Health):  {self.stats.health}/100")
        print("-"*60)
    
    def check_game_over(self) -> bool:
        """Check if any stat has hit 0 (game over condition)"""
        if self.stats.morale <= 0:
            print("\n💔 GAME OVER: Your mental health has deteriorated too much. You took a leave of absence from college.")
            return True
        if self.stats.academics <= 0:
            print("\n📚 GAME OVER: Your academic performance dropped too low. You were placed on academic suspension.")
            return True
        if self.stats.health <= 0:
            print("\n🏥 GAME OVER: Your physical health declined severely. You had to withdraw for medical reasons.")
            return True
        return False
    
    def check_graduation(self) -> bool:
        """Check if player has completed enough questions to graduate"""
        return self.question_count >= 40  # 4 years * ~10 questions per year
    
    def display_ending(self):
        """Display graduation message based on final stats"""
        print("\n" + "="*60)
        print("🎓 CONGRATULATIONS! YOU'VE GRADUATED! 🎓")
        print("="*60)
        
        avg_stat = (self.stats.morale + self.stats.academics + self.stats.health) / 3
        
        if avg_stat >= 80:
            print("\n🌟 Summa Cum Laude! You excelled in all aspects of college life!")
        elif avg_stat >= 70:
            print("\n⭐ Magna Cum Laude! You had a well-rounded college experience!")
        elif avg_stat >= 60:
            print("\n✨ Cum Laude! You successfully balanced the challenges of college!")
        else:
            print("\n🎓 You made it through! College was tough, but you persevered!")
        
        self.display_stats()


def main():
    """Main game loop for terminal testing"""
    api_key = os.environ.get('GEMINI_KEY')
    
    if not api_key:
        print("Error: GEMINI_KEY environment variable not set")
        return
    
    print("="*60)
    print("WELCOME TO COLLEGE SIMULATOR")
    print("="*60)
    print("\nNavigate your way through college by making choices that")
    print("affect your Mental Health, Academic Success, and Physical Health.")
    print("\nTry to maintain balance and make it to graduation!")
    print("\nPress Ctrl+C at any time to quit.\n")
    
    input("Press Enter to start your freshman year...")
    
    simulator = CollegeSimulator(api_key)
    
    try:
        while True:
            # Generate question
            try:
                question_data = simulator.generate_question()
            except Exception as e:
                print(f"\nError generating question: {e}")
                break
            
            # Display question
            simulator.display_question(question_data)
            simulator.display_stats()
            
            # Get user choice
            while True:
                choice = input("\nEnter your choice (1 or 2): ").strip()
                if choice in ['1', '2']:
                    choice_id = f"A{choice}"
                    break
                print("Invalid choice. Please enter 1 or 2.")
            
            # Apply choice
            simulator.apply_choice(question_data, choice_id)
            
            # Check game over conditions
            if simulator.check_game_over():
                simulator.display_stats()
                break
            
            # Check graduation
            if simulator.check_graduation():
                simulator.display_ending()
                break
            
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        simulator.display_stats()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()