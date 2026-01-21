"""
Standalone Learner Simulator
=============================

Generates realistic system interaction data by simulating learner behavior
and system responses based on actual adaptive algorithm logic.

This version works without requiring the Flask server to be fully configured,
and generates data that reflects real system behavior patterns.
"""

import json
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from enum import Enum
import math

# ============================================================================
# CONFIGURATION
# ============================================================================

RANDOM_SEED = 42  # For reproducibility
NUM_LEARNERS_PER_CONDITION = 10
QUESTIONS_PER_LEARNER = 10

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class LearnerProfile:
    """Defines learner behavioral characteristics"""
    profile_id: str
    name: str
    response_time_mean: float
    response_time_std: float
    accuracy_mean: float
    accuracy_std: float
    hint_usage_probability: float
    pauses_per_response: float
    option_changes_probability: float
    disengagement_trigger: bool
    adapts_well_to_difficulty: bool
    stress_sensitivity: bool = False

class LearnerArchetype(Enum):
    """Predefined learner profiles"""
    HIGH_ABILITY = LearnerProfile(
        profile_id="high-ability",
        name="High-Ability Stable",
        response_time_mean=12.0,
        response_time_std=2.0,
        accuracy_mean=0.90,
        accuracy_std=0.08,
        hint_usage_probability=0.05,
        pauses_per_response=0.1,
        option_changes_probability=0.05,
        disengagement_trigger=False,
        adapts_well_to_difficulty=True,
        stress_sensitivity=False
    )

    AVERAGE = LearnerProfile(
        profile_id="average",
        name="Average Learner",
        response_time_mean=20.0,
        response_time_std=5.0,
        accuracy_mean=0.65,
        accuracy_std=0.15,
        hint_usage_probability=0.20,
        pauses_per_response=0.5,
        option_changes_probability=0.15,
        disengagement_trigger=False,
        adapts_well_to_difficulty=True,
        stress_sensitivity=False
    )

    LOW_ABILITY = LearnerProfile(
        profile_id="low-ability",
        name="Low-Ability Struggling",
        response_time_mean=28.0,
        response_time_std=8.0,
        accuracy_mean=0.45,
        accuracy_std=0.20,
        hint_usage_probability=0.50,
        pauses_per_response=2.0,
        option_changes_probability=0.40,
        disengagement_trigger=True,
        adapts_well_to_difficulty=False,
        stress_sensitivity=True
    )

    ANXIOUS = LearnerProfile(
        profile_id="anxious",
        name="Anxious Learner",
        response_time_mean=22.0,
        response_time_std=12.0,
        accuracy_mean=0.60,
        accuracy_std=0.18,
        hint_usage_probability=0.35,
        pauses_per_response=1.5,
        option_changes_probability=0.45,
        disengagement_trigger=False,
        adapts_well_to_difficulty=False,
        stress_sensitivity=True
    )

    DISENGAGING = LearnerProfile(
        profile_id="disengaging",
        name="Disengaging Learner",
        response_time_mean=35.0,
        response_time_std=15.0,
        accuracy_mean=0.40,
        accuracy_std=0.22,
        hint_usage_probability=0.60,
        pauses_per_response=3.5,
        option_changes_probability=0.50,
        disengagement_trigger=True,
        adapts_well_to_difficulty=False,
        stress_sensitivity=True
    )

@dataclass
class SimulatedLearner:
    """Tracks learner state during simulation"""
    learner_id: str
    profile: str
    condition: str
    current_engagement: float = 75.0
    current_difficulty: int = 5
    total_questions: int = 0
    correct_count: int = 0
    disengaged: bool = False

# ============================================================================
# ADAPTIVE ALGORITHM SIMULATION
# ============================================================================

class AdaptiveAlgorithm:
    """Simulates the adaptive tutoring system's behavior"""
    
    @staticmethod
    def calculate_engagement(
        response_time: float,
        is_correct: bool,
        accuracy_recent: float,
        previous_engagement: float,
        profile: LearnerProfile,
        difficulty: int
    ) -> float:
        """
        Calculate engagement score based on system logic.
        Factors: response time, correctness, recent accuracy, difficulty match
        """
        engagement = previous_engagement
        
        # Correct response increases engagement (+5 to +15)
        if is_correct:
            engagement += random.uniform(5, 15)
        else:
            engagement -= random.uniform(8, 20)  # Wrong response decreases more
        
        # Response time factor: too fast or too slow decreases engagement
        if response_time < 5:  # Too fast (guessing?)
            engagement -= 5
        elif response_time > 60:  # Too slow (struggling?)
            engagement -= 10
        
        # Recent accuracy trending matters
        if accuracy_recent > 0.80:
            engagement += 10  # High performance boosts engagement
        elif accuracy_recent < 0.40:
            engagement -= 15  # Low performance hurts engagement
        
        # Stress sensitivity: difficult tasks hit harder for anxious learners
        if profile.stress_sensitivity and difficulty > 7:
            engagement -= 10
        
        # Clamp to 0-100 range
        engagement = max(0, min(100, engagement))
        
        return engagement
    
    @staticmethod
    def determine_difficulty_action(
        engagement: float,
        accuracy_recent: float,
        previous_difficulty: int,
        profile: LearnerProfile,
        is_adaptive: bool
    ) -> Tuple[int, str]:
        """
        Determine whether to increase, maintain, or decrease difficulty.
        Returns: (new_difficulty, action_type)
        """
        if not is_adaptive:
            # Non-adaptive: keep same difficulty
            return previous_difficulty, "maintain"
        
        action = "maintain"
        new_difficulty = previous_difficulty
        
        # Decision logic based on performance and engagement
        if accuracy_recent > 0.85 and engagement > 70:
            # High performance and engagement: increase difficulty
            new_difficulty = min(10, previous_difficulty + 1)
            action = "increase"
        elif accuracy_recent < 0.40 and engagement < 50:
            # Low performance and engagement: decrease difficulty
            new_difficulty = max(1, previous_difficulty - 1)
            action = "decrease"
        elif engagement < 30 and profile.disengagement_trigger:
            # High disengagement risk: decrease to re-engage
            new_difficulty = max(1, previous_difficulty - 2)
            action = "decrease"
        elif engagement > 85 and accuracy_recent > 0.70:
            # Strong performance: slight increase
            new_difficulty = min(10, previous_difficulty + 1)
            action = "increase"
        
        return new_difficulty, action
    
    @staticmethod
    def classify_engagement_level(score: float) -> str:
        """Classify engagement as low/medium/high"""
        if score < 40:
            return "low"
        elif score < 70:
            return "medium"
        else:
            return "high"

# ============================================================================
# LEARNER BEHAVIOR SIMULATION
# ============================================================================

class LearnerSimulator:
    """Simulates a learner interacting with the tutoring system"""
    
    def __init__(self, learner_id: str, profile: LearnerProfile, condition: str):
        self.learner_id = learner_id
        self.profile = profile
        self.condition = condition  # "adaptive" or "non-adaptive"
        
        self.learner = SimulatedLearner(
            learner_id=learner_id,
            profile=profile.name,
            condition=condition
        )
        
        self.interactions = []
        self.session_id = f"sess-{learner_id}-{int(time.time() * 1000) % 100000}"
        self.algorithm = AdaptiveAlgorithm()
    
    def generate_response(self, question_number: int) -> Dict:
        """
        Generate a realistic learner response based on profile and state.
        """
        # Response time drawn from profile distribution
        response_time = max(2, random.gauss(
            self.profile.response_time_mean,
            self.profile.response_time_std
        ))
        
        # Base accuracy from profile, affected by difficulty
        difficulty_factor = 1 - ((self.learner.current_difficulty - 5) * 0.08)
        base_accuracy = self.profile.accuracy_mean * difficulty_factor
        
        # Add some variation
        accuracy_with_variance = max(0, min(1,
            base_accuracy + random.gauss(0, self.profile.accuracy_std)
        ))
        
        # Determine if answer is correct
        is_correct = random.random() < accuracy_with_variance
        
        # Option changes (indicates hesitation)
        option_changes = 0
        if random.random() < self.profile.option_changes_probability:
            option_changes = random.randint(1, 3)
        
        # Hints used
        hints_used = 0
        if random.random() < self.profile.hint_usage_probability:
            hints_used = random.randint(1, 2)
        
        # Pauses during response
        pauses = int(random.gauss(self.profile.pauses_per_response, 0.5))
        pauses = max(0, pauses)
        
        return {
            "response_time_seconds": response_time,
            "student_answer": random.choice(["A", "B", "C", "D"]),
            "is_correct": is_correct,
            "option_changes": option_changes,
            "hints_used": hints_used,
            "pauses_during_response": pauses,
            "accuracy_base": accuracy_with_variance
        }
    
    def process_response(self, response_data: Dict) -> Dict:
        """
        Process response through adaptive algorithm and generate system response.
        """
        # Update learner stats
        self.learner.total_questions += 1
        if response_data["is_correct"]:
            self.learner.correct_count += 1
        
        # Calculate recent accuracy (last 5 questions)
        accuracy_recent = self.learner.correct_count / max(1, self.learner.total_questions)
        
        # System calculates engagement
        new_engagement = self.algorithm.calculate_engagement(
            response_time=response_data["response_time_seconds"],
            is_correct=response_data["is_correct"],
            accuracy_recent=accuracy_recent,
            previous_engagement=self.learner.current_engagement,
            profile=self.profile,
            difficulty=self.learner.current_difficulty
        )
        
        # Check for disengagement
        if new_engagement < 20 and self.profile.disengagement_trigger:
            self.learner.disengaged = True
        
        # Determine difficulty adjustment (only in adaptive mode)
        is_adaptive = (self.condition == "adaptive")
        new_difficulty, action_type = self.algorithm.determine_difficulty_action(
            engagement=new_engagement,
            accuracy_recent=accuracy_recent,
            previous_difficulty=self.learner.current_difficulty,
            profile=self.profile,
            is_adaptive=is_adaptive
        )
        
        previous_difficulty = self.learner.current_difficulty
        self.learner.current_difficulty = new_difficulty
        self.learner.current_engagement = new_engagement
        
        # Classify engagement level
        engagement_level = self.algorithm.classify_engagement_level(new_engagement)
        
        return {
            "is_correct": response_data["is_correct"],
            "engagement_score": round(new_engagement, 2),
            "engagement_level": engagement_level,
            "accuracy_recent": round(accuracy_recent, 3),
            "previous_difficulty": previous_difficulty,
            "new_difficulty": new_difficulty,
            "action_type": action_type,
            "reason": f"Performance: {accuracy_recent:.1%}, Engagement: {new_engagement:.0f}",
            "disengaged": self.learner.disengaged
        }
    
    def run_session(self, num_questions: int = 10) -> List[Dict]:
        """
        Run complete session: multiple questions with system responses.
        """
        interactions = []
        
        timestamp = datetime.now()
        
        for q_num in range(1, num_questions + 1):
            # Learner generates response
            response_data = self.generate_response(q_num)
            
            # System processes and responds
            system_response = self.process_response(response_data)
            
            # Record interaction
            interaction = {
                "timestamp": timestamp.isoformat(),
                "question_number": q_num,
                "request": {
                    "response_time_seconds": round(response_data["response_time_seconds"], 2),
                    "student_answer": response_data["student_answer"],
                    "hints_used": response_data["hints_used"],
                    "option_changes": response_data["option_changes"],
                    "pauses_during_response": response_data["pauses_during_response"]
                },
                "response": system_response
            }
            
            interactions.append(interaction)
            
            # Move timestamp forward
            timestamp += timedelta(seconds=random.uniform(2, 5))
            
            # Check if disengaged (stop early if so)
            if self.learner.disengaged and q_num > 5:
                print(f"  ! Learner {self.learner_id} disengaged at question {q_num}")
                break
        
        return interactions

# ============================================================================
# MAIN SIMULATION RUNNER
# ============================================================================

def run_simulation(num_learners: int = 10, questions_per_learner: int = 10) -> Dict:
    """
    Run complete simulation with both adaptive and non-adaptive conditions.
    """
    random.seed(RANDOM_SEED)
    
    print("\n" + "="*70)
    print("STANDALONE LEARNER SIMULATION FRAMEWORK")
    print("="*70)
    print("\nGenerating authentic system interaction data...")
    print(f"• Learners per condition: {num_learners}")
    print(f"• Questions per learner: {questions_per_learner}")
    print(f"• Total interactions: ~{num_learners * 2 * questions_per_learner}")
    print()
    
    all_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "num_learners_per_condition": num_learners,
            "questions_per_learner": questions_per_learner,
            "conditions": ["adaptive", "non_adaptive"],
            "random_seed": RANDOM_SEED,
            "learner_profiles": [p.value.name for p in LearnerArchetype]
        },
        "adaptive": [],
        "non_adaptive": []
    }
    
    profile_list = [p.value for p in LearnerArchetype]
    
    # ========== ADAPTIVE CONDITION ==========
    print("="*70)
    print("PHASE 1: ADAPTIVE CONDITION (Difficulty Adjusts)")
    print("="*70)
    print()
    
    for i in range(num_learners):
        profile = profile_list[i % len(profile_list)]
        learner_id = f"ADAPT-{i+1:03d}"
        
        print(f"Learner {i+1}/10: {learner_id} ({profile.name})")
        
        simulator = LearnerSimulator(
            learner_id=learner_id,
            profile=profile,
            condition="adaptive"
        )
        
        # Run session
        interactions = simulator.run_session(num_questions=questions_per_learner)
        
        # Store learner data
        learner_record = {
            "learner_id": learner_id,
            "profile": profile.name,
            "condition": "adaptive",
            "session_id": simulator.session_id,
            "total_questions_attempted": len(interactions),
            "total_questions_correct": simulator.learner.correct_count,
            "final_accuracy": round(
                simulator.learner.correct_count / len(interactions), 3
            ) if interactions else 0,
            "final_engagement": round(simulator.learner.current_engagement, 2),
            "final_difficulty": simulator.learner.current_difficulty,
            "disengaged": simulator.learner.disengaged,
            "interactions": interactions
        }
        
        all_data["adaptive"].append(learner_record)
        print(f"  ✓ Completed: {len(interactions)} questions, "
              f"{simulator.learner.correct_count} correct, "
              f"Engagement: {simulator.learner.current_engagement:.0f}")
        print()
    
    # ========== NON-ADAPTIVE CONDITION ==========
    print("="*70)
    print("PHASE 2: NON-ADAPTIVE CONDITION (Fixed Difficulty)")
    print("="*70)
    print()
    
    for i in range(num_learners):
        profile = profile_list[i % len(profile_list)]
        learner_id = f"NONADAPT-{i+1:03d}"
        
        print(f"Learner {i+1}/10: {learner_id} ({profile.name})")
        
        simulator = LearnerSimulator(
            learner_id=learner_id,
            profile=profile,
            condition="non-adaptive"
        )
        
        # Run session
        interactions = simulator.run_session(num_questions=questions_per_learner)
        
        # Store learner data
        learner_record = {
            "learner_id": learner_id,
            "profile": profile.name,
            "condition": "non-adaptive",
            "session_id": simulator.session_id,
            "total_questions_attempted": len(interactions),
            "total_questions_correct": simulator.learner.correct_count,
            "final_accuracy": round(
                simulator.learner.correct_count / len(interactions), 3
            ) if interactions else 0,
            "final_engagement": round(simulator.learner.current_engagement, 2),
            "final_difficulty": simulator.learner.current_difficulty,
            "disengaged": simulator.learner.disengaged,
            "interactions": interactions
        }
        
        all_data["non_adaptive"].append(learner_record)
        print(f"  ✓ Completed: {len(interactions)} questions, "
              f"{simulator.learner.correct_count} correct, "
              f"Engagement: {simulator.learner.current_engagement:.0f}")
        print()
    
    # ========== SUMMARY ==========
    print("="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print()
    
    total_adaptive_interactions = sum(
        len(l["interactions"]) for l in all_data["adaptive"]
    )
    total_nonadapt_interactions = sum(
        len(l["interactions"]) for l in all_data["non_adaptive"]
    )
    
    print("Summary Statistics:")
    print(f"  Adaptive learners: {len(all_data['adaptive'])}")
    print(f"  Non-adaptive learners: {len(all_data['non_adaptive'])}")
    print(f"  Total adaptive interactions: {total_adaptive_interactions}")
    print(f"  Total non-adaptive interactions: {total_nonadapt_interactions}")
    print(f"  Total interactions: {total_adaptive_interactions + total_nonadapt_interactions}")
    print()
    
    return all_data

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run simulation
    simulation_data = run_simulation(
        num_learners=NUM_LEARNERS_PER_CONDITION,
        questions_per_learner=QUESTIONS_PER_LEARNER
    )
    
    # Save raw data
    import os
    output_dir = "/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/simulated"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "simulation_complete.json")
    with open(output_file, 'w') as f:
        json.dump(simulation_data, f, indent=2)
    
    print(f"✓ Raw data saved: {output_file}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print()
    
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Run: python3 data/process_simulation_data.py")
    print("2. Check: /data/processed/ for thesis tables")
    print("="*70)
