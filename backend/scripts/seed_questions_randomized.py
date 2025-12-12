#!/usr/bin/env python3
"""
Improved seed script with randomized correct answer positions.
Run from backend directory: python scripts/seed_questions_randomized.py
"""

import os
import sys
import random
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, db
from app.models.question import Question, QuestionDifficulty

# Sample questions with answer content (before randomization)
SAMPLE_QUESTIONS = {
    'Mathematics': {
        'Algebra': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'What is 2 + 2?',
                'answers': ['3', '4', '5', '6'],  # Correct answer is at index 1 (4)
                'correct_index': 1,
                'explanation': 'When we add 2 + 2, we count two units and then two more units, giving us 4 total.',
                'hints': ['Count on your fingers: 1, 2, 3, 4', 'Think of two pairs of things']
            },
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'Solve for x: x + 3 = 7',
                'answers': ['x = 3', 'x = 4', 'x = 5', 'x = 10'],  # Correct is x = 4 (index 1)
                'correct_index': 1,
                'explanation': 'To solve x + 3 = 7, subtract 3 from both sides: x = 7 - 3 = 4',
                'hints': ['Think about what number plus 3 equals 7', 'Move the 3 to the other side by subtracting it']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'Expand: (x + 2)(x + 3)',
                'answers': ['x² + 5x + 6', 'x² + 6x + 5', 'x² + 5x + 5', 'x² + 3x + 6'],  # Correct at index 0
                'correct_index': 0,
                'explanation': '(x + 2)(x + 3) = x² + 3x + 2x + 6 = x² + 5x + 6 (using FOIL method)',
                'hints': ['Use the FOIL method: First, Outer, Inner, Last', 'Multiply: x·x + x·3 + 2·x + 2·3']
            },
            {
                'difficulty': 0.8,  # HARD
                'question_text': 'Solve: 2x² - 5x + 3 = 0',
                'answers': ['x = 1 or x = 3/2', 'x = 2 or x = 1/2', 'x = 3 or x = 1', 'x = -1 or x = -3/2'],  # Correct at index 0
                'correct_index': 0,
                'explanation': 'Using quadratic formula: x = (5 ± √(25-24))/4 = (5 ± 1)/4, giving x = 3/2 or x = 1',
                'hints': ['Try factoring: (2x - 3)(x - 1) = 0', 'Use the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a']
            }
        ],
        'Geometry': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'What is the area of a rectangle with length 5 and width 3?',
                'answers': ['8', '15', '10', '16'],  # Correct is 15 (index 1)
                'correct_index': 1,
                'explanation': 'Area of rectangle = length × width = 5 × 3 = 15',
                'hints': ['Area = length × width', 'Multiply 5 by 3']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'In a right triangle, if one leg is 3 and the hypotenuse is 5, what is the other leg?',
                'answers': ['2', '4', '6', '8'],  # Correct is 4 (index 1)
                'correct_index': 1,
                'explanation': 'Using Pythagorean theorem: a² + 3² = 5², so a² + 9 = 25, therefore a² = 16, and a = 4',
                'hints': ['Use Pythagorean theorem: a² + b² = c²', 'We need: x² + 9 = 25, so x² = 16']
            },
            {
                'difficulty': 0.8,  # HARD
                'question_text': 'Find the area of a circle with radius 7',
                'answers': ['14π', '49π', '98π', '7π'],  # Correct is 49π (index 1)
                'correct_index': 1,
                'explanation': 'Area of circle = πr² = π(7)² = 49π',
                'hints': ['The formula for circle area is πr²', 'r = 7, so r² = 49']
            }
        ]
    },
    'Science': {
        'Physics': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'What is the SI unit of force?',
                'answers': ['Kilogram', 'Newton', 'Joule', 'Watt'],  # Correct is Newton (index 1)
                'correct_index': 1,
                'explanation': 'The Newton (N) is the SI unit of force, named after Sir Isaac Newton.',
                'hints': ['It is named after a famous physicist', 'This unit equals kg·m/s²']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'What is the formula for kinetic energy?',
                'answers': ['KE = mv', 'KE = ½mv²', 'KE = mgh', 'KE = ma'],  # Correct at index 1
                'correct_index': 1,
                'explanation': 'Kinetic energy is the energy of motion. KE = ½mv², where m is mass and v is velocity.',
                'hints': ['Kinetic energy depends on velocity squared', 'It is proportional to ½ × mass × velocity²']
            }
        ],
        'Chemistry': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'What is the chemical symbol for oxygen?',
                'answers': ['O', 'Ox', 'Og', 'Os'],  # Correct at index 0
                'correct_index': 0,
                'explanation': 'The chemical symbol for oxygen is O. It is atomic number 8.',
                'hints': ['It is a single letter symbol', 'Think of the word oxygen']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'What is the pH of a neutral solution?',
                'answers': ['0', '5', '7', '14'],  # Correct is 7 (index 2)
                'correct_index': 2,
                'explanation': 'A neutral solution has a pH of 7. Pure water at 25°C has a pH of 7.',
                'hints': ['The pH scale goes from 0 to 14', 'Middle of the scale is neutral']
            }
        ]
    },
    'English': {
        'Grammar': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'Which sentence is grammatically correct?',
                'answers': ['She go to school', 'She goes to school', 'She going to school', 'She gone to school'],  # Correct at index 1
                'correct_index': 1,
                'explanation': 'With third-person singular subjects (she), we use the verb form "goes" in present tense.',
                'hints': ['Think about subject-verb agreement', 'She is singular, so use "goes" not "go"']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'Identify the correct use of its/it\'s',
                'answers': ['The cat licked it\'s paws', 'The cat licked its paws', 'Its important to learn grammar', 'It\'s happy when it plays'],  # Correct at index 1
                'correct_index': 1,
                'explanation': '"Its" is possessive (belonging to), while "it\'s" is a contraction of "it is".',
                'hints': ['its = possessive', 'it\'s = it is']
            }
        ],
        'Vocabulary': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'What does the word "benign" mean?',
                'answers': ['Harmful', 'Harmless', 'Angry', 'Confused'],  # Correct is Harmless (index 1)
                'correct_index': 1,
                'explanation': 'Benign means not harmful, benevolent, or (in medical terms) not cancerous.',
                'hints': ['It is the opposite of harmful', 'Often used in medical contexts']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'Which word best describes "ambiguous"?',
                'answers': ['Clear and distinct', 'Having more than one possible meaning', 'Ambitious', 'Ambitious and successful'],  # Correct at index 1
                'correct_index': 1,
                'explanation': 'Ambiguous means unclear, having multiple possible interpretations or meanings.',
                'hints': ['Think of something that could mean two things', 'It relates to unclear meaning']
            }
        ]
    },
    'History': {
        'Ancient History': [
            {
                'difficulty': 0.2,  # EASY
                'question_text': 'Which ancient wonder was located in Egypt?',
                'answers': ['Hanging Gardens', 'Great Pyramid of Giza', 'Colossus of Rhodes', 'Lighthouse of Alexandria'],  # Correct at index 1
                'correct_index': 1,
                'explanation': 'The Great Pyramid of Giza, built around 2560 BC, is the only surviving ancient wonder.',
                'hints': ['It is still standing today', 'It was built as a tomb']
            },
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'In which year did Julius Caesar cross the Rubicon?',
                'answers': ['49 BC', '50 BC', '48 BC', '51 BC'],  # Correct at index 0
                'correct_index': 0,
                'explanation': 'Julius Caesar crossed the Rubicon River in 49 BC, starting a civil war in Rome.',
                'hints': ['It was before he became dictator', 'This phrase means passing a point of no return']
            }
        ],
        'Modern History': [
            {
                'difficulty': 0.5,  # MEDIUM
                'question_text': 'In what year did World War II end?',
                'answers': ['1944', '1945', '1946', '1943'],  # Correct is 1945 (index 1)
                'correct_index': 1,
                'explanation': 'World War II ended in 1945 with Germany\'s surrender in May and Japan\'s in September.',
                'hints': ['It was around 6 years after it started in 1939', 'Think of VE Day and VJ Day']
            }
        ]
    }
}

def randomize_answers(answers, correct_index):
    """
    Randomize the position of answers while tracking the new correct position.
    
    Args:
        answers: List of answer strings
        correct_index: Original index of correct answer
    
    Returns:
        Tuple of (shuffled_answers, new_correct_index, correct_option_letter)
    """
    # Get the correct answer
    correct_answer = answers[correct_index]
    
    # Create list of (answer, is_correct) tuples
    answer_tuples = [(ans, ans == correct_answer) for ans in answers]
    
    # Shuffle
    random.shuffle(answer_tuples)
    
    # Extract shuffled answers and find new correct index
    shuffled_answers = [ans for ans, _ in answer_tuples]
    new_correct_index = next(i for i, (_, is_correct) in enumerate(answer_tuples) if is_correct)
    correct_option = chr(65 + new_correct_index)  # Convert index to letter (A, B, C, D)
    
    return shuffled_answers, new_correct_index, correct_option

def seed_questions():
    """Seed the database with sample questions with randomized answers."""
    with app.app_context():
        # Check if questions already exist
        existing_count = Question.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} questions.")
            response = input("Do you want to clear and reseed? (yes/no): ").lower()
            if response != 'yes':
                print("Seeding cancelled.")
                return
            Question.query.delete()
            db.session.commit()
            print("Cleared existing questions.\n")

        # Add questions with randomized answers
        total_added = 0
        answer_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for subject, topics in SAMPLE_QUESTIONS.items():
            for topic, questions in topics.items():
                for q_data in questions:
                    # Randomize answers
                    shuffled_answers, _, correct_option = randomize_answers(
                        q_data['answers'], 
                        q_data['correct_index']
                    )
                    
                    # Track distribution of correct answers
                    answer_distribution[correct_option] += 1
                    
                    # Create question
                    question = Question(
                        subject=subject,
                        topic=topic,
                        difficulty=q_data['difficulty'],
                        question_text=q_data['question_text'],
                        option_a=shuffled_answers[0],
                        option_b=shuffled_answers[1],
                        option_c=shuffled_answers[2],
                        option_d=shuffled_answers[3],
                        correct_option=correct_option,
                        explanation=q_data['explanation'],
                        hints=q_data['hints']
                    )
                    db.session.add(question)
                    total_added += 1

        db.session.commit()
        print(f"✅ Successfully seeded {total_added} questions with randomized answers!\n")

        # Print summary by subject
        print("Seeded questions by subject:")
        for subject in SAMPLE_QUESTIONS.keys():
            count = Question.query.filter_by(subject=subject).count()
            print(f"  {subject}: {count} questions")

        # Print difficulty breakdown
        print("\nSeeded questions by difficulty:")
        difficulty_map = {0.2: 'EASY', 0.5: 'MEDIUM', 0.8: 'HARD'}
        for diff_val, diff_name in sorted(difficulty_map.items()):
            count = Question.query.filter_by(difficulty=diff_val).count()
            print(f"  {diff_name} ({diff_val*100:.0f}%): {count} questions")

        # Print correct answer distribution
        print("\nCorrect answer position distribution:")
        for option in ['A', 'B', 'C', 'D']:
            count = answer_distribution[option]
            pct = (count / total_added) * 100 if total_added > 0 else 0
            print(f"  Option {option}: {count} ({pct:.1f}%)")
        
        print("\n✅ Distribution is randomized - not concentrated on any single option!")

if __name__ == '__main__':
    print("=" * 60)
    print("Tutoring System Database Seeding Script (Randomized Answers)")
    print("=" * 60 + "\n")
    random.seed()  # Seed the random number generator
    seed_questions()
    print("\n✅ Seeding complete!")
