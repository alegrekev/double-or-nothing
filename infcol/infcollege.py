# infcollege.py

import os
import json
import re
import random
import google.generativeai as genai
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import keyenv

# College Majors List
COLLEGE_MAJORS = [
    "Aerospace Engineering",
    "Agricultural Technology",
    "Ancient Sumerian Irrigation",
    "Ant Farming",
    "Apparel, Housing, and Resource Management",
    "Architecture",
    "Business Information Technology",
    "Chemistry",
    "Civil Engineering",
    "Computer Engineering",
    "Computer Science",
    "Criminology",
    "Cybersecurity",
    "Dairy Science",
    "Economics",
    "Electrical Engineering",
    "English",
    "Finance",
    "Fish and Wildlife Conservation",
    "Forest Resource Management",
    "Geography",
    "History",
    "Horticulture",
    "Industrial and Systems Engineering",
    "Mathematics",
    "Mechanical Engineering",
    "Mining Engineering",
    "Mongolian Throat Singing",
    "Music",
    "Nanoscience",
    "Philosophy",
    "Physics",
    "Psychology",
    "Sociology",
    "Competitive Rock Stacking",
    "Conspiracy Theory Analysis",
    "Cryptozoology",
    "Dungeon Architecture",
    "Feng Shui Engineering",
    "Medieval Siege Economics",
    "Pirate Logistics and Supply Chains",
    "Sandwich Engineering",
    "Underwater Basket Weaving"
]

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
    
    def get_average(self) -> float:
        """Calculate average of all stats"""
        return (self.morale + self.academics + self.health) / 3
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Decision:
    question_num: int
    question: str
    choice: str
    effects: Dict[str, Optional[int]]


@dataclass
class GameEvent:
    """Represents major events like suspensions, warnings, etc."""
    type: str  # 'academic_suspension', 'medical_leave', 'mental_health_crisis', 'dropout_warning'
    message: str
    question_num: int


class CollegeSimulator:
    SYSTEM_PROMPT = """You are a college life simulator game master. Your role is to generate realistic college scenarios that create a compelling narrative journey from Year 1 to Graduation.

## Your Task
Generate college life questions/situations with two choice options. Each choice affects three stats: Morale (Mental Health), Academics (Academic Success), and Health (Physical Health). Stats range from 0-100.

## Guidelines
1. **Narrative Continuity**: Base questions on the student's past decisions, current stats, AND their chosen major
2. **Major-Specific Content**: Incorporate the student's major into scenarios (major-specific classes, labs, projects, career opportunities, internships, etc.)
3. **Realistic Scenarios**: Create situations that college students actually face, with major-specific flavor
4. **VARIED CHOICES - IMPORTANT**: 
   - NOT all choices should be balanced trade-offs
   - Sometimes one choice is clearly better or worse (but still tempting for different reasons)
   - Sometimes both choices are bad (choosing the lesser evil)
   - Sometimes both choices are good (choosing priorities)
   - Mix obviously good decisions, obviously bad decisions, and difficult trade-offs
5. **Stat Effects - IMPORTANT VARIETY RULES**: 
   - Use values between -40 to +40 for impacts (occasionally go to extremes like -50 or +50 for major events)
   - **DO NOT always affect all three stats** - many choices should only affect 1 or 2 stats
   - Use null liberally when a choice doesn't impact a particular stat
   - Create asymmetric choices: one option might affect all stats while the other only affects one
   - Examples of good variety:
     * Choice A: morale +30, academics null, health null (pure social benefit)
     * Choice B: morale -20, academics +40, health -30 (grueling all-nighter studying)
     * Choice A: morale +10, academics null, health +15 (light exercise)
     * Choice B: morale -40, academics -30, health -25 (destructive spiral)
6. **Tempting Bad Choices**: Make clearly negative options still feel tempting in the moment (procrastination, unhealthy coping, avoiding responsibility)
7. **Progression**: Questions should reflect the student's year (freshman, sophomore, junior, senior) and previous choices
8. **Variety**: Mix academic, social, health, financial, and personal scenarios - but tie them to the student's major when relevant
9. **Major Events**: If the student has experienced major setbacks (academic suspension, medical leave, mental health crisis), incorporate these into the narrative naturally
10. **Consequence Realism**: Poor choices should have significant negative impacts. Good choices should meaningfully help. The player should be able to spiral down OR climb up based on their decisions.

## Response Format
Always respond with valid JSON in this exact structure:
{
  "question": "The situation/scenario the student faces",
  "year": "Year 1" | "Year 2" | "Year 3" | "Year 4",
  "summary": "A 2-3 sentence summary of this question and its context in the student's journey",
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

## SUMMARY FIELD REQUIREMENTS
The "summary" field should:
- Be 2-3 sentences describing this scenario's significance
- Capture the key decision point and its implications
- Reflect the student's current situation (stats, major, year)
- Be concise but informative for tracking the narrative arc
- Example: "After struggling academically last semester, you face a critical decision about your Computer Science project. Your low morale and health are taking a toll, but this project could turn things around."

## CRITICAL JSON FORMATTING RULES
- Effect values MUST be integers without the plus sign: use 30, not +30
- Use negative numbers with minus sign: -10 is correct
- Use null (not "null" in quotes) when there is no effect
- Do NOT include any + symbols in the JSON
- Examples: "morale": 15, "academics": -10, "health": null

## Examples of Good Choice Variety:

**Example 1: Clear Good vs Bad**
Question: "You have a major exam tomorrow morning."
A1: "Pull an all-nighter cramming" → morale: -25, academics: +35, health: -40
A2: "Go to bed early and hope for the best" → morale: null, academics: -15, health: +20

**Example 2: Both Good (Priority Choice)**
Question: "You received a surprise scholarship check!"
A1: "Invest in a gym membership and healthy meal prep" → morale: +15, academics: null, health: +35
A2: "Pay down student loans and reduce stress" → morale: +30, academics: +10, health: null

**Example 3: Both Bad (Lesser Evil)**
Question: "You're completely overwhelmed and breaking down."
A1: "Withdraw from a class and lighten your load" → morale: -15, academics: -35, health: null
A2: "Push through even though you're suffering" → morale: -40, academics: null, health: -30

**Example 4: Tempting But Destructive**
Question: "Your friends are partying all weekend before finals."
A1: "Join them - you need to blow off steam" → morale: +25, academics: -45, health: -20
A2: "Stay in and study alone" → morale: -10, academics: +30, health: null

**Example 5: Only One Stat Affected**
Question: "The campus rec center is offering free yoga classes."
A1: "Sign up and attend regularly" → morale: null, academics: null, health: +25
A2: "Skip it - you're too busy" → morale: null, academics: null, health: null

**Example 6: Major-Specific Scenario (Computer Science)**
Question: "Your CS project partner hasn't contributed anything with 48 hours until the deadline."
A1: "Do their part yourself to ensure a good grade" → morale: -30, academics: +20, health: -25
A2: "Report them to the TA and risk the deadline" → morale: -10, academics: -15, health: null

**Example 7: Major-Specific Scenario (Mechanical Engineering)**
Question: "You have the opportunity to join the Formula SAE racing team, but it's a huge time commitment during your toughest semester."
A1: "Join the team - hands-on experience is invaluable" → morale: +25, academics: -20, health: -15
A2: "Focus on grades this semester, maybe next year" → morale: -10, academics: +15, health: null

## Context Awareness
When provided with game state (current stats, past decisions, current year, major, major events), tailor the question to reflect:
- Consequences of previous choices
- Major-specific challenges (difficult classes, labs, projects typical for that major)
- Major-specific opportunities (clubs, internships, research related to the major)
- Current stat levels (low health might lead to illness scenarios, low academics to academic probation, etc.)
- Major events that have occurred (academic suspension, medical leave, mental health crisis)
- Recovery opportunities if stats are dangerously low
- Downward spiral opportunities if player keeps making bad choices
- Time in college (early years vs. senior year priorities, intro classes vs. capstone projects)
- Building a coherent story arc that reflects the journey through their specific major

Generate engaging, realistic scenarios that make the player feel the weight of their decisions throughout their college journey. Don't be afraid to punish bad decisions harshly or reward good decisions well."""
    
    # Thresholds
    DROPOUT_WARNING_THRESHOLD = 35  # Average below this triggers dropout warning
    DROPOUT_CHECK_THRESHOLD = 35    # Average must rise above this to avoid dropout
    CRITICAL_STAT_THRESHOLD = 15    # Individual stat threshold for crisis events
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.stats = Stats()
        self.decisions: List[Decision] = []
        self.events: List[GameEvent] = []
        self.question_count = 0
        self.current_year = 1
        self.dropout_warning_active = False
        self.warning_avg = 0.0
        self.major: Optional[str] = None
        self.offered_majors: List[str] = []
        self.current_question: Optional[Dict] = None  # Store current question for API
        self.long_term_summary: str = ""  # Cumulative summary of past decisions
        self.question_summaries: List[str] = []  # Store all question summaries
        
    def get_year_label(self) -> str:
        """Convert question count to year label"""
        years = {1: "Year 1", 2: "Year 2", 3: "Year 3", 4: "Year 4"}
        # Roughly 10 questions per year for a 40-question game
        year_num = min(4, (self.question_count // 5) + 1)
        return years[year_num]
    
    def is_past_first_year(self) -> bool:
        """Check if player is past first year (question 11+)"""
        return self.question_count >= 5
    
    def generate_major_selection_question(self) -> Dict:
        """Generate the first question to select a major"""
        # Select two random majors
        self.offered_majors = random.sample(COLLEGE_MAJORS, 2)
        
        question_data = {
            "question": f"Welcome to college! It's time to declare your major. You've narrowed it down to two fields that interest you. Which path will you choose?",
            "year": "Year 1",
            "answers": [
                {
                    "id": "A1",
                    "text": f"Declare {self.offered_majors[0]} as your major",
                    "effects": {
                        "morale": 15,
                        "academics": None,
                        "health": None
                    }
                },
                {
                    "id": "A2",
                    "text": f"Declare {self.offered_majors[1]} as your major",
                    "effects": {
                        "morale": 15,
                        "academics": None,
                        "health": None
                    }
                }
            ]
        }
        
        self.question_count += 1
        return question_data
    
    def set_major_from_choice(self, choice_id: str):
        """Set the student's major based on their choice"""
        if choice_id == "A1":
            self.major = self.offered_majors[0]
        else:
            self.major = self.offered_majors[1]
        
        print(f"\n🎓 You've declared {self.major} as your major!")
    
    def build_context_prompt(self) -> str:
        """Build context from previous decisions and current stats"""
        if not self.major:
            # This shouldn't happen after the first question
            return "This is the first question. The student is just starting their college journey as a freshman."
        
        context = f"""
Current Game State:
- Year: {self.get_year_label()}
- Major: {self.major}
- Current Stats: Morale: {self.stats.morale}, Academics: {self.stats.academics}, Health: {self.stats.health}
- Average Stats: {self.stats.get_average():.1f}
- Questions Answered: {self.question_count}
"""
        
        # Add long-term summary if it exists
        if self.long_term_summary:
            context += f"\nLong-term Journey Summary:\n{self.long_term_summary}\n"
        
        # Add stat warnings
        stat_warnings = []
        if self.stats.morale < 30:
            stat_warnings.append("⚠️ Morale is very low - student is struggling mentally")
        if self.stats.academics < 30:
            stat_warnings.append("⚠️ Academics are very low - student is at risk of failing")
        if self.stats.health < 30:
            stat_warnings.append("⚠️ Health is very low - student is physically struggling")
        
        if stat_warnings:
            context += "\nCurrent Struggles:\n"
            for warning in stat_warnings:
                context += f"- {warning}\n"
        
        # Add major events to context
        if self.events:
            context += "\nMajor Events:\n"
            for event in self.events[-3:]:  # Last 3 events
                context += f"- {event.message}\n"
        
        # Add dropout warning if active
        if self.dropout_warning_active:
            context += f"\n⚠️ CRITICAL: Student is on dropout warning! Average was {self.warning_avg:.1f}. They need to improve their overall situation or they may drop out. Generate a scenario that offers opportunities for recovery but also risks of further decline.\n"
        
        context += "\nRecent Decisions:\n"
        # Include last 3 decisions for context
        for decision in self.decisions[-3:]:
            context += f"- Q{decision.question_num}: {decision.question}\n  Choice: {decision.choice}\n"
        
        context += f"\nGenerate the next question that follows naturally from these past decisions, current stats, major events, and the student's major ({self.major}). Remember to vary your choice structures - not every choice should be a balanced trade-off! Incorporate major-specific content when appropriate."
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
        response_text = re.sub(r':\s*\+(\d+)', r': \1', response_text)
        
        return response_text.strip()
    
    def generate_question(self) -> Dict:
        """Request Gemini to generate a new question"""
        # First question is always major selection
        if self.question_count == 0:
            return self.generate_major_selection_question()
        
        context = self.build_context_prompt()
        
        prompt = f"{self.SYSTEM_PROMPT}\n\n{context}\n\nRespond ONLY with the JSON object, no additional text."
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract and clean JSON from response
            response_text = self.clean_json_response(response.text)
            
            question_data = json.loads(response_text)
            self.question_count += 1
            
            # Store the summary from this question
            current_summary = question_data.get('summary', '')
            if current_summary:
                self.question_summaries.append(current_summary)
            
            # Update long-term summary using 3rd most recent
            # When we have 3+ summaries, compound the 3rd most recent into long-term
            if len(self.question_summaries) >= 3:
                # Get the 3rd most recent summary (index -3)
                third_most_recent = self.question_summaries[-3]
                
                # Compound it into long-term summary
                if self.long_term_summary:
                    # Add to existing summary
                    self.long_term_summary = f"{self.long_term_summary} {third_most_recent}"
                else:
                    # First time: start with the 3rd summary
                    self.long_term_summary = third_most_recent
            
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
        
        # If this is the first question, set the major
        if self.question_count == 1:
            self.set_major_from_choice(choice_id)
        
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
    
    def check_stat_crisis_events(self):
        """Check for crisis events when individual stats are critically low"""
        events_triggered = []
        
        # Academic crisis
        if self.stats.academics <= self.CRITICAL_STAT_THRESHOLD and not any(e.type == 'academic_suspension' for e in self.events[-2:]):
            event = GameEvent(
                type='academic_suspension',
                message=f"⚠️ ACADEMIC PROBATION: Your GPA has fallen to {self.stats.academics}/100. You've been placed on academic probation and must meet with your advisor.",
                question_num=self.question_count
            )
            self.events.append(event)
            events_triggered.append(event)
        
        # Health crisis
        if self.stats.health <= self.CRITICAL_STAT_THRESHOLD and not any(e.type == 'medical_leave' for e in self.events[-2:]):
            event = GameEvent(
                type='medical_leave',
                message=f"🏥 MEDICAL CONCERN: Your physical health has deteriorated to {self.stats.health}/100. Student health services has reached out to schedule an urgent appointment.",
                question_num=self.question_count
            )
            self.events.append(event)
            events_triggered.append(event)
        
        # Mental health crisis
        if self.stats.morale <= self.CRITICAL_STAT_THRESHOLD and not any(e.type == 'mental_health_crisis' for e in self.events[-2:]):
            event = GameEvent(
                type='mental_health_crisis',
                message=f"💔 MENTAL HEALTH ALERT: Your mental health is at {self.stats.morale}/100. The counseling center has been notified and wants to schedule an urgent session.",
                question_num=self.question_count
            )
            self.events.append(event)
            events_triggered.append(event)
        
        return events_triggered
    
    def check_dropout_warning(self):
        """Check if player should receive dropout warning"""
        if not self.is_past_first_year():
            return False
        
        avg = self.stats.get_average()
        
        # Trigger warning if average is below threshold and warning not already active
        if avg < self.DROPOUT_WARNING_THRESHOLD and not self.dropout_warning_active:
            self.dropout_warning_active = True
            self.warning_avg = avg
            
            event = GameEvent(
                type='dropout_warning',
                message=f"⚠️ DROPOUT WARNING: Your overall performance (avg: {avg:.1f}/100) is concerning. You need to turn things around soon or you may need to consider taking a leave of absence.",
                question_num=self.question_count
            )
            self.events.append(event)
            
            print("\n" + "!"*60)
            print(event.message)
            print("!"*60)
            return True
        
        return False
    
    def check_dropout_resolution(self) -> Optional[str]:
        """
        Check if dropout warning should be resolved or trigger dropout.
        Returns 'improved', 'dropout', or None
        """
        if not self.dropout_warning_active:
            return None
        
        current_avg = self.stats.get_average()
        
        # Player improved - warning lifted
        if current_avg > self.DROPOUT_CHECK_THRESHOLD:
            improvement = current_avg - self.warning_avg
            self.dropout_warning_active = False
            
            print("\n" + "="*60)
            print(f"✅ IMPROVEMENT NOTICED: Your average has risen to {current_avg:.1f}!")
            print(f"The dropout warning has been lifted. Keep up the progress!")
            print("="*60)
            return 'improved'
        
        # Player didn't improve - calculate dropout chance
        # Lower average = higher dropout chance
        # Below 15: 90% chance, 15-20: 75% chance, 20-25: 60% chance, 25-30: 45% chance, 30-35: 30% chance
        if current_avg < 15:
            dropout_chance = 0.90
        elif current_avg < 20:
            dropout_chance = 0.75
        elif current_avg < 25:
            dropout_chance = 0.60
        elif current_avg < 30:
            dropout_chance = 0.45
        else:
            dropout_chance = 0.30
        
        # Roll for dropout
        roll = random.random()
        print(f"\n⚠️ Dropout check: Average {current_avg:.1f}, Chance: {dropout_chance*100:.0f}%, Roll: {roll:.2f}")
        
        if roll < dropout_chance:
            return 'dropout'
        
        # Warning continues
        print(f"⚠️ You barely avoided dropping out. Your average is still critically low ({current_avg:.1f}). You MUST improve!")
        return None
    
    def display_question(self, question_data: Dict):
        """Display question in terminal"""
        print("\n" + "="*60)
        print(f"YEAR: {question_data.get('year', self.get_year_label())}")
        if self.major:
            print(f"MAJOR: {self.major}")
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
            else:
                print(f"   Effects: No change")
            print()
    
    def display_stats(self):
        """Display current stats"""
        avg = self.stats.get_average()
        print("\n" + "-"*60)
        print("CURRENT STATS")
        print("-"*60)
        print(f"Morale (Mental Health):    {self.stats.morale}/100 {'⚠️ CRITICAL!' if self.stats.morale < 25 else '⚠️ LOW' if self.stats.morale < 40 else ''}")
        print(f"Academics:                 {self.stats.academics}/100 {'⚠️ CRITICAL!' if self.stats.academics < 25 else '⚠️ LOW' if self.stats.academics < 40 else ''}")
        print(f"Health (Physical Health):  {self.stats.health}/100 {'⚠️ CRITICAL!' if self.stats.health < 25 else '⚠️ LOW' if self.stats.health < 40 else ''}")
        print(f"Average:                   {avg:.1f}/100 {'⚠️ DROPOUT RISK!' if avg < 35 else '⚠️ STRUGGLING' if avg < 50 else ''}")
        print("-"*60)
        
        # Show dropout warning status
        if self.dropout_warning_active:
            print("🚨 DROPOUT WARNING ACTIVE - Improve your stats NOW!")
            print("-"*60)
    
    def display_events(self, events: List[GameEvent]):
        """Display triggered events"""
        for event in events:
            print("\n" + "!"*60)
            print(event.message)
            print("!"*60)
    
    def check_graduation(self) -> bool:
        """Check if player has completed enough questions to graduate"""
        return self.question_count >= 20  # 4 years * ~10 questions per year
    
    def display_ending(self):
        """Display graduation message based on final stats"""
        print("\n" + "="*60)
        print("🎓 CONGRATULATIONS! YOU'VE GRADUATED! 🎓")
        print("="*60)
        print(f"\nYou've earned your degree in {self.major}!")
        
        avg_stat = self.stats.get_average()
        
        if avg_stat >= 80:
            print("\n🌟 Summa Cum Laude! You excelled in all aspects of college life!")
        elif avg_stat >= 70:
            print("\n⭐ Magna Cum Laude! You had a well-rounded college experience!")
        elif avg_stat >= 60:
            print("\n✨ Cum Laude! You successfully balanced the challenges of college!")
        else:
            print("\n🎓 You made it through! College was tough, but you persevered!")
        
        # Show major events overcome
        if self.events:
            print("\nChallenges Overcome:")
            event_types = set(e.type for e in self.events)
            if 'academic_suspension' in event_types:
                print("  - Recovered from academic probation")
            if 'medical_leave' in event_types:
                print("  - Overcame health challenges")
            if 'mental_health_crisis' in event_types:
                print("  - Battled through mental health struggles")
            if 'dropout_warning' in event_types:
                print("  - Fought back from the brink of dropping out")
        
        self.display_stats()
    
    def display_dropout_ending(self):
        """Display dropout ending"""
        print("\n" + "="*60)
        print("📚 COLLEGE JOURNEY ENDED - DROPOUT")
        print("="*60)
        print(f"\nAfter {self.question_count} questions into your {self.major} degree,")
        print("the weight of your struggles became too much to bear.")
        print("Your decisions led to a downward spiral that you couldn't recover from.")
        print("\nThis isn't the end of your story - it's a tough lesson.")
        print("Many people face setbacks and come back stronger.")
        print("You can always return to college when you're in a better place.")
        print("="*60)
        
        self.display_stats()
        
        if self.events:
            print("\nChallenges You Faced:")
            for event in self.events:
                print(f"  - {event.message}")


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
    print("\nYou'll start by choosing your major, which will influence")
    print("the scenarios you face throughout your college journey.")
    print("\nTry to maintain balance and make it to graduation!")
    print("\n⚠️  Warning: Poor choices have REAL consequences!")
    print("If your overall performance drops too low after your first year,")
    print("you may drop out!")
    print("\nPress Ctrl+C at any time to quit.\n")
    
    input("Press Enter to start your college journey...")
    
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
            if simulator.question_count > 1:  # Don't show stats for major selection
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
            
            # Skip crisis checks for major selection question
            if simulator.question_count > 1:
                # Check for crisis events (non-terminal)
                crisis_events = simulator.check_stat_crisis_events()
                if crisis_events:
                    simulator.display_events(crisis_events)
                
                # Check for dropout warning (only after first year)
                if simulator.is_past_first_year():
                    simulator.check_dropout_warning()
                    
                    # Check if dropout warning resolves
                    dropout_result = simulator.check_dropout_resolution()
                    if dropout_result == 'dropout':
                        simulator.display_dropout_ending()
                        break
            
            # Check graduation
            if simulator.check_graduation():
                simulator.display_ending()
                break
            
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        if simulator.major:
            print(f"Major: {simulator.major}")
        simulator.display_stats()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()