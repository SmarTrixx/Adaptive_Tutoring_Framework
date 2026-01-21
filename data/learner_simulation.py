"""
Learner Simulation Framework
=============================

Simulates realistic learner interactions with the Adaptive Tutoring Framework.
Learners interact with the actual Flask system, generating real system outputs.

Key Design:
- Learner archetypes (High-ability, Average, Low-ability, Anxious, Disengaging)
- Each profile has distinct behavioral patterns
- Profiles interact with BOTH adaptive and non-adaptive modes
- System returns real engagement metrics and adaptation decisions
- All data captured from actual system responses
"""

import requests
import time
import random
import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:5000"  # Flask server
SEED = 42
random.seed(SEED)

# ============================================================================
# LEARNER ARCHETYPES
# ============================================================================

@dataclass
class LearnerProfile:
    """Definition of a learner archetype"""
    profile_id: str
    name: str
    description: str
    
    # Behavioral characteristics
    response_time_mean: float          # seconds
    response_time_std: float           # variance
    accuracy_mean: float               # 0.0-1.0
    accuracy_std: float
    hint_usage_probability: float      # 0.0-1.0
    pauses_per_response: float         # 0-3
    option_changes_probability: float  # how often they change answer
    
    # Engagement dynamics
    disengagement_trigger: bool        # tends to disengage
    engagement_recovery_probability: float  # can recover if adapted
    stress_sensitivity: bool           # reacts to difficulty
    
    # Adaptation response
    adapts_well_to_difficulty: bool    # benefits from adaptive
    
class LearnerArchetype(Enum):
    HIGH_ABILITY = LearnerProfile(
        profile_id="HA",
        name="High-Ability Stable",
        description="Fast, accurate, confident responses. Low engagement risk.",
        response_time_mean=12.0,
        response_time_std=2.0,
        accuracy_mean=0.90,
        accuracy_std=0.05,
        hint_usage_probability=0.05,
        pauses_per_response=0.2,
        option_changes_probability=0.05,
        disengagement_trigger=False,
        engagement_recovery_probability=0.0,  # Already highly engaged
        stress_sensitivity=False,
        adapts_well_to_difficulty=True
    )
    
    AVERAGE = LearnerProfile(
        profile_id="AV",
        name="Average Learner",
        description="Moderate pace, moderate accuracy, stable engagement.",
        response_time_mean=20.0,
        response_time_std=5.0,
        accuracy_mean=0.65,
        accuracy_std=0.10,
        hint_usage_probability=0.30,
        pauses_per_response=0.8,
        option_changes_probability=0.25,
        disengagement_trigger=False,
        engagement_recovery_probability=0.5,
        stress_sensitivity=False,
        adapts_well_to_difficulty=True
    )
    
    LOW_ABILITY = LearnerProfile(
        profile_id="LA",
        name="Low-Ability Struggling",
        description="Slower, lower accuracy, high engagement risk.",
        response_time_mean=28.0,
        response_time_std=8.0,
        accuracy_mean=0.45,
        accuracy_std=0.15,
        hint_usage_probability=0.60,
        pauses_per_response=1.5,
        option_changes_probability=0.50,
        disengagement_trigger=True,
        engagement_recovery_probability=0.8,  # Needs adaptive support
        stress_sensitivity=True,
        adapts_well_to_difficulty=True
    )
    
    ANXIOUS = LearnerProfile(
        profile_id="AN",
        name="Anxious Learner",
        description="Erratic timing, medium accuracy, high hesitation.",
        response_time_mean=22.0,
        response_time_std=12.0,  # High variance = erratic
        accuracy_mean=0.60,
        accuracy_std=0.20,
        hint_usage_probability=0.50,
        pauses_per_response=2.0,  # Lots of thinking/hesitation
        option_changes_probability=0.65,
        disengagement_trigger=True,
        engagement_recovery_probability=0.7,
        stress_sensitivity=True,
        adapts_well_to_difficulty=True
    )
    
    DISENGAGING = LearnerProfile(
        profile_id="DIS",
        name="Disengaging Learner",
        description="Long pauses, low commitment, very high risk.",
        response_time_mean=35.0,
        response_time_std=15.0,
        accuracy_mean=0.40,
        accuracy_std=0.20,
        hint_usage_probability=0.80,
        pauses_per_response=2.5,
        option_changes_probability=0.30,
        disengagement_trigger=True,
        engagement_recovery_probability=0.9,  # Needs strong adaptive support
        stress_sensitivity=True,
        adapts_well_to_difficulty=True
    )

# ============================================================================
# SIMULATED LEARNER
# ============================================================================

@dataclass
class SimulatedLearner:
    """A simulated learner interacting with the system"""
    learner_id: str
    profile: LearnerProfile
    condition: str  # "adaptive" or "non-adaptive"
    
    # State tracking
    current_engagement: float = 0.5
    current_difficulty: float = 0.5
    question_count: int = 0
    correct_count: int = 0
    session_duration: float = 0.0
    has_disengaged: bool = False

class LearnerSimulator:
    """Controls a simulated learner interacting with the system"""
    
    def __init__(self, learner: SimulatedLearner, api_url: str = API_BASE_URL):
        self.learner = learner
        self.api_url = api_url
        self.session_id: Optional[str] = None
        self.interaction_log: List[Dict] = []
        
    def start_session(self) -> Dict:
        """Initialize a session with the system"""
        payload = {
            "student_id": self.learner.learner_id,
            "subject": "cbtest",
            "preferred_difficulty": self.learner.profile.accuracy_mean
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/session/start",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.learner.current_difficulty = data.get('current_difficulty', 0.5)
                print(f"✓ Session started: {self.session_id}")
                return data
            else:
                print(f"✗ Failed to start session: {response.status_code}")
                return {}
        except Exception as e:
            print(f"✗ Error starting session: {e}")
            return {}
    
    def generate_response(self) -> Dict:
        """
        Simulate a learner's response to a question.
        Returns the response that will be submitted.
        """
        profile = self.learner.profile
        
        # Generate response time (realistic distribution)
        response_time = max(3.0, random.gauss(profile.response_time_mean, profile.response_time_std))
        response_time = min(90.0, response_time)  # Cap at 90 seconds
        
        # Determine correctness (influenced by ability and difficulty alignment)
        difficulty_gap = abs(self.learner.current_difficulty - profile.accuracy_mean)
        adjusted_accuracy = profile.accuracy_mean - (difficulty_gap * 0.3)  # Harder = lower accuracy
        adjusted_accuracy = max(0.1, min(0.95, adjusted_accuracy))
        
        is_correct = random.random() < adjusted_accuracy
        
        # Hint usage
        hints_used = 0
        if not is_correct and random.random() < profile.hint_usage_probability:
            hints_used = 1
        
        # Option changes (hesitation)
        option_changes = 0
        if random.random() < profile.option_changes_probability:
            option_changes = random.randint(1, 3)
        
        # Pauses
        pauses = max(0, int(random.gauss(profile.pauses_per_response, 1.0)))
        
        return {
            "student_answer": f"option_{random.randint(1, 4)}",
            "response_time_seconds": round(response_time, 2),
            "option_changes": option_changes,
            "hints_used": hints_used,
            "pauses_during_response": pauses,
            "is_correct": is_correct
        }
    
    def submit_response(self, response_data: Dict) -> Dict:
        """Submit a response to the system and capture returned data"""
        if not self.session_id:
            print("✗ No active session")
            return {}
        
        # Wait realistic time before submission (think time + response time)
        time.sleep(random.uniform(0.5, 2.0))
        
        payload = {
            "session_id": self.session_id,
            "student_answer": response_data["student_answer"],
            "response_time_seconds": response_data["response_time_seconds"],
            "option_changes": response_data["option_changes"],
            "hints_used": response_data["hints_used"],
            "pauses_during_response": response_data["pauses_during_response"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/response/submit",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                system_data = response.json()
                
                # Update learner state from system response
                self.learner.question_count += 1
                if response_data["is_correct"]:
                    self.learner.correct_count += 1
                
                # Update difficulty if adaptive
                if 'new_difficulty' in system_data:
                    self.learner.current_difficulty = system_data['new_difficulty']
                
                # Update engagement
                if 'engagement_score' in system_data:
                    self.learner.current_engagement = system_data['engagement_score']
                    if system_data['engagement_score'] < 0.3:
                        self.learner.has_disengaged = True
                
                # Log the complete interaction
                self.interaction_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "request": payload,
                    "response": system_data,
                    "learner_state": asdict(self.learner)
                })
                
                return system_data
            else:
                print(f"✗ Submit failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"✗ Error submitting response: {e}")
            return {}
    
    def run_session(self, num_questions: int = 10) -> List[Dict]:
        """Run a complete session for this learner"""
        print(f"\n{'='*70}")
        print(f"LEARNER: {self.learner.learner_id} ({self.learner.profile.name})")
        print(f"CONDITION: {self.learner.condition}")
        print(f"QUESTIONS: {num_questions}")
        print(f"{'='*70}")
        
        # Start session
        session_info = self.start_session()
        if not session_info:
            return []
        
        session_start = time.time()
        
        # Process questions
        for q_num in range(num_questions):
            print(f"\nQuestion {q_num + 1}/{num_questions}...", end=" ")
            
            # Generate and submit response
            response = self.generate_response()
            system_response = self.submit_response(response)
            
            if system_response:
                # Extract key info
                engagement = system_response.get('engagement_score', self.learner.current_engagement)
                difficulty = system_response.get('new_difficulty', self.learner.current_difficulty)
                correct = response['is_correct']
                
                print(f"{'✓' if correct else '✗'} | "
                      f"Eng: {engagement:.2f} | "
                      f"Diff: {difficulty:.2f}")
            else:
                print("✗ Failed")
            
            # Simulate fatigue/engagement decay
            if self.learner.has_disengaged:
                if random.random() < self.learner.profile.engagement_recovery_probability:
                    self.learner.has_disengaged = False
        
        session_end = time.time()
        self.learner.session_duration = session_end - session_start
        
        # Summary
        accuracy = self.learner.correct_count / self.learner.question_count if self.learner.question_count > 0 else 0
        print(f"\nSession Summary:")
        print(f"  Accuracy: {accuracy:.1%}")
        print(f"  Final Engagement: {self.learner.current_engagement:.2f}")
        print(f"  Final Difficulty: {self.learner.current_difficulty:.2f}")
        print(f"  Duration: {self.learner.session_duration:.1f}s")
        
        return self.interaction_log

# ============================================================================
# SIMULATION RUNNER
# ============================================================================

def run_simulation(
    num_learners: int = 10,
    questions_per_learner: int = 10,
    output_dir: str = "/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/simulated"
) -> Dict:
    """
    Run complete simulation:
    - 10 learners in adaptive mode
    - 10 learners in non-adaptive mode
    - Capture all system outputs
    """
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    all_data = {
        'adaptive': [],
        'non_adaptive': [],
        'raw_interactions': []
    }
    
    # Create learner pool (mix of archetypes)
    learner_archetypes = [
        LearnerArchetype.HIGH_ABILITY.value,
        LearnerArchetype.AVERAGE.value,
        LearnerArchetype.LOW_ABILITY.value,
        LearnerArchetype.ANXIOUS.value,
        LearnerArchetype.DISENGAGING.value
    ]
    
    learner_counter = 1
    
    # =====================================================================
    # PHASE 1: ADAPTIVE CONDITION
    # =====================================================================
    print("\n" + "="*70)
    print("PHASE 1: ADAPTIVE CONDITION (10 learners)")
    print("="*70)
    
    for i in range(num_learners):
        # Select archetype (round-robin)
        archetype = learner_archetypes[i % len(learner_archetypes)]
        learner = SimulatedLearner(
            learner_id=f"ADAPT_{learner_counter:03d}",
            profile=archetype,
            condition="adaptive"
        )
        learner_counter += 1
        
        # Run simulation
        simulator = LearnerSimulator(learner)
        interactions = simulator.run_session(num_questions=questions_per_learner)
        
        # Store data
        all_data['adaptive'].append({
            'learner_id': learner.learner_id,
            'profile': learner.profile.name,
            'interactions': interactions,
            'final_state': asdict(learner)
        })
        all_data['raw_interactions'].extend(interactions)
    
    # =====================================================================
    # PHASE 2: NON-ADAPTIVE CONDITION
    # =====================================================================
    print("\n" + "="*70)
    print("PHASE 2: NON-ADAPTIVE CONDITION (10 learners)")
    print("="*70)
    
    for i in range(num_learners):
        # Select same archetypes (same learner types in both conditions)
        archetype = learner_archetypes[i % len(learner_archetypes)]
        learner = SimulatedLearner(
            learner_id=f"NONADAPT_{learner_counter:03d}",
            profile=archetype,
            condition="non-adaptive"
        )
        learner_counter += 1
        
        # Run simulation
        simulator = LearnerSimulator(learner)
        interactions = simulator.run_session(num_questions=questions_per_learner)
        
        # Store data
        all_data['non_adaptive'].append({
            'learner_id': learner.learner_id,
            'profile': learner.profile.name,
            'interactions': interactions,
            'final_state': asdict(learner)
        })
        all_data['raw_interactions'].extend(interactions)
    
    # =====================================================================
    # SAVE DATA
    # =====================================================================
    print("\n" + "="*70)
    print("SAVING DATA")
    print("="*70)
    
    # Save complete JSON
    output_file = f"{output_dir}/simulation_complete.json"
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"✓ Complete data: {output_file}")
    
    return all_data

if __name__ == "__main__":
    print("="*70)
    print("LEARNER SIMULATION FRAMEWORK")
    print("Adaptive Tutoring Framework")
    print("="*70)
    print("\nThis script simulates 20 learners (10 adaptive, 10 non-adaptive)")
    print("interacting with the actual Flask system.")
    print("\nMake sure Flask server is running on http://localhost:5000")
    print("="*70)
    
    # Run simulation
    simulation_data = run_simulation(
        num_learners=10,
        questions_per_learner=10
    )
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print(f"Adaptive learners: {len(simulation_data['adaptive'])}")
    print(f"Non-adaptive learners: {len(simulation_data['non_adaptive'])}")
    print(f"Total interactions: {len(simulation_data['raw_interactions'])}")
    print("\nData saved to: data/simulated/")
    print("="*70)
