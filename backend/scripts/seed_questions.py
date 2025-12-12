#!/usr/bin/env python3
"""
Seed script to populate Questions database with sample data.
Run from backend directory: python scripts/seed_questions.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, db
from app.models.question import Question, QuestionDifficulty

# Sample questions organized by subject and topic
SAMPLE_QUESTIONS = {
    'Mathematics': {
        'Algebra': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is 2 + 2?',
                'option_a': '3',
                'option_b': '4',
                'option_c': '5',
                'option_d': '6',
                'correct_option': 'B',
                'explanation': 'When we add 2 + 2, we count two units and then two more units, giving us 4 total.',
                'hints': [
                    'Count on your fingers: 1, 2, 3, 4',
                    'Think of two pairs of things'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Solve for x: x + 3 = 7',
                'option_a': 'x = 3',
                'option_b': 'x = 4',
                'option_c': 'x = 5',
                'option_d': 'x = 10',
                'correct_option': 'B',
                'explanation': 'To solve x + 3 = 7, subtract 3 from both sides: x = 7 - 3 = 4',
                'hints': [
                    'Think about what number plus 3 equals 7',
                    'Move the 3 to the other side by subtracting it'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Expand: (x + 2)(x + 3)',
                'option_a': 'x² + 5x + 6',
                'option_b': 'x² + 6x + 5',
                'option_c': 'x² + 5x + 5',
                'option_d': 'x² + 3x + 6',
                'correct_option': 'A',
                'explanation': '(x + 2)(x + 3) = x² + 3x + 2x + 6 = x² + 5x + 6 (using FOIL method)',
                'hints': [
                    'Use the FOIL method: First, Outer, Inner, Last',
                    'Multiply: x·x + x·3 + 2·x + 2·3'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Solve: 2x² - 5x + 3 = 0',
                'option_a': 'x = 1 or x = 3/2',
                'option_b': 'x = 2 or x = 1/2',
                'option_c': 'x = 3 or x = 1',
                'option_d': 'x = -1 or x = -3/2',
                'correct_option': 'A',
                'explanation': 'Using quadratic formula: x = (5 ± √(25-24))/4 = (5 ± 1)/4, giving x = 3/2 or x = 1',
                'hints': [
                    'Try factoring: (2x - 3)(x - 1) = 0',
                    'Use the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a'
                ]
            }
        ],
        'Geometry': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the area of a rectangle with length 5 and width 3?',
                'option_a': '8',
                'option_b': '15',
                'option_c': '10',
                'option_d': '16',
                'correct_option': 'B',
                'explanation': 'Area of rectangle = length × width = 5 × 3 = 15',
                'hints': [
                    'Area = length × width',
                    'Multiply 5 by 3'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'In a right triangle, if one leg is 3 and the hypotenuse is 5, what is the other leg?',
                'option_a': '2',
                'option_b': '4',
                'option_c': '6',
                'option_d': '8',
                'correct_option': 'B',
                'explanation': 'Using Pythagorean theorem: a² + 3² = 5², so a² + 9 = 25, therefore a² = 16, and a = 4',
                'hints': [
                    'Use Pythagorean theorem: a² + b² = c²',
                    'We need: x² + 9 = 25, so x² = 16'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Find the area of a circle with radius 7',
                'option_a': '14π',
                'option_b': '49π',
                'option_c': '98π',
                'option_d': '7π',
                'correct_option': 'B',
                'explanation': 'Area of circle = πr² = π(7)² = 49π',
                'hints': [
                    'The formula for circle area is πr²',
                    'r = 7, so r² = 49'
                ]
            }
        ]
    },
    'Science': {
        'Physics': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the SI unit of force?',
                'option_a': 'Kilogram',
                'option_b': 'Newton',
                'option_c': 'Joule',
                'option_d': 'Watt',
                'correct_option': 'B',
                'explanation': 'The Newton (N) is the SI unit of force, named after Sir Isaac Newton.',
                'hints': [
                    'It is named after a famous physicist',
                    'This unit equals kg·m/s²'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the formula for kinetic energy?',
                'option_a': 'KE = mv',
                'option_b': 'KE = ½mv²',
                'option_c': 'KE = mgh',
                'option_d': 'KE = ma',
                'correct_option': 'B',
                'explanation': 'Kinetic energy is the energy of motion. KE = ½mv², where m is mass and v is velocity.',
                'hints': [
                    'Kinetic energy depends on velocity squared',
                    'It is proportional to ½ × mass × velocity²'
                ]
            }
        ],
        'Chemistry': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the chemical symbol for oxygen?',
                'option_a': 'O',
                'option_b': 'Ox',
                'option_c': 'Og',
                'option_d': 'Os',
                'correct_option': 'A',
                'explanation': 'The chemical symbol for oxygen is O. It is atomic number 8.',
                'hints': [
                    'It is a single letter symbol',
                    'Think of the word oxygen'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the pH of a neutral solution?',
                'option_a': '0',
                'option_b': '5',
                'option_c': '7',
                'option_d': '14',
                'correct_option': 'C',
                'explanation': 'A neutral solution has a pH of 7. Pure water at 25°C has a pH of 7.',
                'hints': [
                    'The pH scale goes from 0 to 14',
                    'Middle of the scale is neutral'
                ]
            }
        ]
    },
    'English': {
        'Grammar': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Which sentence is grammatically correct?',
                'option_a': 'She go to school',
                'option_b': 'She goes to school',
                'option_c': 'She going to school',
                'option_d': 'She gone to school',
                'correct_option': 'B',
                'explanation': 'With third-person singular subjects (she), we use the verb form "goes" in present tense.',
                'hints': [
                    'Think about subject-verb agreement',
                    'She is singular, so use "goes" not "go"'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Identify the correct use of its/it\'s',
                'option_a': 'The cat licked it\'s paws',
                'option_b': 'The cat licked its paws',
                'option_c': 'Its important to learn grammar',
                'option_d': 'It\'s happy when it plays',
                'correct_option': 'B',
                'explanation': '"Its" is possessive (belonging to), while "it\'s" is a contraction of "it is".',
                'hints': [
                    'its = possessive',
                    'it\'s = it is'
                ]
            }
        ],
        'Vocabulary': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What does the word "benign" mean?',
                'option_a': 'Harmful',
                'option_b': 'Harmless',
                'option_c': 'Angry',
                'option_d': 'Confused',
                'correct_option': 'B',
                'explanation': 'Benign means not harmful, benevolent, or (in medical terms) not cancerous.',
                'hints': [
                    'It is the opposite of harmful',
                    'Often used in medical contexts'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Which word best describes "ambiguous"?',
                'option_a': 'Clear and distinct',
                'option_b': 'Having more than one possible meaning',
                'option_c': 'Ambitious',
                'option_d': 'Ambitious and successful',
                'correct_option': 'B',
                'explanation': 'Ambiguous means unclear, having multiple possible interpretations or meanings.',
                'hints': [
                    'Think of something that could mean two things',
                    'It relates to unclear meaning'
                ]
            }
        ]
    },
    'History': {
        'Ancient History': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Which ancient wonder was located in Egypt?',
                'option_a': 'Hanging Gardens',
                'option_b': 'Great Pyramid of Giza',
                'option_c': 'Colossus of Rhodes',
                'option_d': 'Lighthouse of Alexandria',
                'correct_option': 'B',
                'explanation': 'The Great Pyramid of Giza, built around 2560 BC, is the only surviving ancient wonder.',
                'hints': [
                    'It is still standing today',
                    'It was built as a tomb'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'In which year did Julius Caesar cross the Rubicon?',
                'option_a': '49 BC',
                'option_b': '50 BC',
                'option_c': '48 BC',
                'option_d': '51 BC',
                'correct_option': 'A',
                'explanation': 'Julius Caesar crossed the Rubicon River in 49 BC, starting a civil war in Rome.',
                'hints': [
                    'It was before he became dictator',
                    'This phrase means passing a point of no return'
                ]
            }
        ],
        'Modern History': [
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'In what year did World War II end?',
                'option_a': '1944',
                'option_b': '1945',
                'option_c': '1946',
                'option_d': '1943',
                'correct_option': 'B',
                'explanation': 'World War II ended in 1945 with Germany\'s surrender in May and Japan\'s in September.',
                'hints': [
                    'It was around 6 years after it started in 1939',
                    'Think of VE Day and VJ Day'
                ]
            }
        ]
    }
}


def seed_questions():
    """Seed the database with sample questions."""
    with app.app_context():
        # Check if questions already exist
        existing_count = Question.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} questions.")
            response = input("Do you want to clear and reseed? (yes/no): ").lower()
            if response == 'yes':
                Question.query.delete()
                db.session.commit()
                print("Cleared existing questions.")
            else:
                print("Seeding cancelled.")
                return

        # Add questions
        total_added = 0
        for subject, topics in SAMPLE_QUESTIONS.items():
            for topic, questions in topics.items():
                for q_data in questions:
                    question = Question(
                        subject=subject,
                        topic=topic,
                        difficulty=q_data['difficulty'].value if isinstance(q_data['difficulty'], QuestionDifficulty) else q_data['difficulty'],
                        question_text=q_data['question_text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_option=q_data['correct_option'],
                        explanation=q_data['explanation'],
                        hints=q_data['hints']
                    )
                    db.session.add(question)
                    total_added += 1

        db.session.commit()
        print(f"\n✅ Successfully seeded {total_added} questions!")

        # Print summary
        print("\nSeeded questions by subject:")
        for subject in SAMPLE_QUESTIONS.keys():
            count = Question.query.filter_by(subject=subject).count()
            print(f"  {subject}: {count} questions")

        # Print difficulty breakdown
        print("\nSeeded questions by difficulty:")
        for difficulty in QuestionDifficulty:
            count = Question.query.filter_by(difficulty=difficulty.value).count()
            print(f"  {difficulty.name}: {count} questions")


if __name__ == '__main__':
    print("=" * 50)
    print("Tutoring System Database Seeding Script")
    print("=" * 50)
    seed_questions()
    print("\nSeeding complete!")
