#!/usr/bin/env python3
"""
Add more questions to expand the question bank.
Run from backend directory: python scripts/add_more_questions.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, db
from app.models.question import Question

ADDITIONAL_QUESTIONS = {
    'Mathematics': [
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What is 5 × 6?',
            'option_a': '25',
            'option_b': '30',
            'option_c': '35',
            'option_d': '40',
            'correct_option': 'B',
            'explanation': '5 × 6 = 30. Multiplication combines groups of equal size.',
            'hints': ['Count by 5s six times', '5 + 5 + 5 + 5 + 5 + 5 = 30']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What is 15 ÷ 3?',
            'option_a': '3',
            'option_b': '4',
            'option_c': '5',
            'option_d': '6',
            'correct_option': 'C',
            'explanation': 'Division splits groups. 15 ÷ 3 means 15 split into 3 groups = 5 per group.',
            'hints': ['How many 3s fit into 15?', '3 × 5 = 15']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What is 10 - 6?',
            'option_a': '4',
            'option_b': '5',
            'option_c': '6',
            'option_d': '7',
            'correct_option': 'A',
            'explanation': '10 - 6 = 4. Subtraction is the reverse of addition.',
            'hints': ['Count backwards from 10', '6 + 4 = 10']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is 25% of 100?',
            'option_a': '10',
            'option_b': '20',
            'option_c': '25',
            'option_d': '50',
            'correct_option': 'C',
            'explanation': '25% means 25/100. 25% of 100 = 0.25 × 100 = 25.',
            'hints': ['Percent means per hundred', 'One quarter of 100 is 25']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'Solve: 2x + 4 = 12',
            'option_a': 'x = 2',
            'option_b': 'x = 4',
            'option_c': 'x = 6',
            'option_d': 'x = 8',
            'correct_option': 'B',
            'explanation': '2x + 4 = 12 → 2x = 8 → x = 4. Subtract 4 from both sides, then divide by 2.',
            'hints': ['Subtract 4 first', 'Then divide both sides by 2']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is the area of a rectangle with length 5m and width 3m?',
            'option_a': '8 m²',
            'option_b': '15 m²',
            'option_c': '16 m²',
            'option_d': '20 m²',
            'correct_option': 'B',
            'explanation': 'Area = length × width = 5 × 3 = 15 m².',
            'hints': ['Multiply length by width', '5 × 3 = 15']
        },
        {
            'difficulty': 0.8,  # HARD
            'question_text': 'Solve: x² + 5x + 6 = 0',
            'option_a': 'x = -2 or x = -3',
            'option_b': 'x = 2 or x = 3',
            'option_c': 'x = -2 or x = 3',
            'option_d': 'x = 2 or x = -3',
            'correct_option': 'A',
            'explanation': 'x² + 5x + 6 = (x+2)(x+3) = 0. So x = -2 or x = -3.',
            'hints': ['Factor the quadratic', 'Find two numbers that multiply to 6 and add to 5']
        },
        {
            'difficulty': 0.8,  # HARD
            'question_text': 'What is the derivative of f(x) = 3x²?',
            'option_a': 'f\'(x) = 3x',
            'option_b': 'f\'(x) = 6x',
            'option_c': 'f\'(x) = 3x³',
            'option_d': 'f\'(x) = 6',
            'correct_option': 'B',
            'explanation': 'Using power rule: d/dx(3x²) = 3 × 2x^(2-1) = 6x.',
            'hints': ['Use the power rule', 'Bring down the exponent and reduce it by 1']
        },
    ],
    'Science': [
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What do plants need to grow?',
            'option_a': 'Only water',
            'option_b': 'Water, sunlight, and soil nutrients',
            'option_c': 'Only sunlight',
            'option_d': 'Only soil',
            'correct_option': 'B',
            'explanation': 'Plants need water for hydration, sunlight for photosynthesis, and soil nutrients for growth.',
            'hints': ['Think about photosynthesis', 'Plants take from soil, water, and air']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'Which planet is closest to the Sun?',
            'option_a': 'Venus',
            'option_b': 'Mercury',
            'option_c': 'Earth',
            'option_d': 'Mars',
            'correct_option': 'B',
            'explanation': 'Mercury is the closest planet to the Sun in our solar system.',
            'hints': ['It starts with M', 'It is very hot']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What is the chemical formula for water?',
            'option_a': 'CO₂',
            'option_b': 'O₂',
            'option_c': 'H₂O',
            'option_d': 'H₂',
            'correct_option': 'C',
            'explanation': 'Water is composed of 2 hydrogen atoms and 1 oxygen atom: H₂O.',
            'hints': ['It contains hydrogen and oxygen', 'Two hydrogens, one oxygen']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is photosynthesis?',
            'option_a': 'The process of breaking down glucose',
            'option_b': 'The process of turning light into chemical energy',
            'option_c': 'The process of respiration',
            'option_d': 'The process of reproduction',
            'correct_option': 'B',
            'explanation': 'Photosynthesis is the process by which plants convert light energy into chemical energy stored in glucose.',
            'hints': ['It involves light and plants', 'It creates glucose']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is the SI unit of force?',
            'option_a': 'Joule',
            'option_b': 'Newton',
            'option_c': 'Watt',
            'option_d': 'Pascal',
            'correct_option': 'B',
            'explanation': 'The Newton (N) is the SI unit of force. 1 N = 1 kg⋅m/s².',
            'hints': ['Named after Isaac Newton', 'F = ma']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is the pH value of neutral water?',
            'option_a': '5',
            'option_b': '7',
            'option_c': '9',
            'option_d': '0',
            'correct_option': 'B',
            'explanation': 'Neutral water has a pH of 7. Values below 7 are acidic, values above 7 are basic.',
            'hints': ['Neutral is in the middle', 'pH scale goes from 0 to 14']
        },
        {
            'difficulty': 0.8,  # HARD
            'question_text': 'What is the speed of light in vacuum?',
            'option_a': '100,000 km/s',
            'option_b': '200,000 km/s',
            'option_c': '300,000 km/s',
            'option_d': '400,000 km/s',
            'correct_option': 'C',
            'explanation': 'The speed of light is approximately 299,792 km/s, often rounded to 300,000 km/s.',
            'hints': ['Einstein\'s constant', 'About 3 × 10⁸ m/s']
        },
    ],
    'English': [
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'Which of these is a noun?',
            'option_a': 'Run',
            'option_b': 'Happy',
            'option_c': 'Book',
            'option_d': 'Quickly',
            'correct_option': 'C',
            'explanation': 'A noun is a person, place, or thing. "Book" is a thing (noun). Run is a verb, Happy is an adjective, Quickly is an adverb.',
            'hints': ['Nouns are things', 'You can see or touch a book']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'What is the opposite of "hot"?',
            'option_a': 'Warm',
            'option_b': 'Cold',
            'option_c': 'Cool',
            'option_d': 'Mild',
            'correct_option': 'B',
            'explanation': '"Cold" is the opposite of "hot". Cold means very low in temperature.',
            'hints': ['Think about temperature', 'Ice is cold']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'Which sentence is correct?',
            'option_a': 'She go to school',
            'option_b': 'She goes to school',
            'option_c': 'She going to school',
            'option_d': 'She gone to school',
            'correct_option': 'B',
            'explanation': 'In present tense with third person singular (she), we use "goes". The verb must agree with the subject.',
            'hints': ['Subject-verb agreement', 'She is singular third person']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is a metaphor?',
            'option_a': 'A comparison using "like" or "as"',
            'option_b': 'A direct comparison between two things',
            'option_c': 'A statement that is obviously not true',
            'option_d': 'A repeated word or sound',
            'correct_option': 'B',
            'explanation': 'A metaphor is a figure of speech that compares two different things without using "like" or "as". Example: "Time is money".',
            'hints': ['Unlike simile, it doesn\'t use "like"', 'It is a direct comparison']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'Which word is a synonym for "happy"?',
            'option_a': 'Sad',
            'option_b': 'Angry',
            'option_c': 'Joyful',
            'option_d': 'Tired',
            'correct_option': 'C',
            'explanation': '"Joyful" is a synonym for "happy" - both words mean experiencing pleasure or contentment.',
            'hints': ['Synonyms have similar meanings', 'Think of a positive emotion']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What is the main idea of a paragraph?',
            'option_a': 'The first sentence',
            'option_b': 'The most important point the paragraph conveys',
            'option_c': 'The last sentence',
            'option_d': 'The longest sentence',
            'correct_option': 'B',
            'explanation': 'The main idea is the central point or primary message. It can appear anywhere but is often near the beginning.',
            'hints': ['Usually stated in a topic sentence', 'All details support this idea']
        },
        {
            'difficulty': 0.8,  # HARD
            'question_text': 'What literary device is used in "Her voice was music to his ears"?',
            'option_a': 'Alliteration',
            'option_b': 'Metaphor',
            'option_c': 'Onomatopoeia',
            'option_d': 'Irony',
            'correct_option': 'B',
            'explanation': '"Her voice was music to his ears" is a metaphor comparing her voice directly to music without using "like" or "as".',
            'hints': ['It compares two different things', 'No "like" or "as" used']
        },
    ],
    'History': [
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'In what year did World War II end?',
            'option_a': '1943',
            'option_b': '1944',
            'option_c': '1945',
            'option_d': '1946',
            'correct_option': 'C',
            'explanation': 'World War II ended in 1945, with Germany surrendering in May and Japan in September.',
            'hints': ['It was after 1943', 'Japan surrendered in September']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'Who was the first President of the United States?',
            'option_a': 'Thomas Jefferson',
            'option_b': 'George Washington',
            'option_c': 'Abraham Lincoln',
            'option_d': 'Benjamin Franklin',
            'correct_option': 'B',
            'explanation': 'George Washington was the first President of the United States, serving from 1789 to 1797.',
            'hints': ['He is on the dollar bill', 'First president']
        },
        {
            'difficulty': 0.2,  # EASY
            'question_text': 'Which continent is Egypt located on?',
            'option_a': 'Asia',
            'option_b': 'Europe',
            'option_c': 'Africa',
            'option_d': 'Australia',
            'correct_option': 'C',
            'explanation': 'Egypt is located in North Africa, along the Nile River.',
            'hints': ['Home of the pyramids', 'North Africa']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'In what year did the Titanic sink?',
            'option_a': '1910',
            'option_b': '1912',
            'option_c': '1920',
            'option_d': '1925',
            'correct_option': 'B',
            'explanation': 'The Titanic sank on April 15, 1912, after hitting an iceberg in the Atlantic Ocean.',
            'hints': ['Early 1900s', 'It hit an iceberg']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'Which empire built the Great Wall of China?',
            'option_a': 'Han Empire',
            'option_b': 'Ming Empire',
            'option_c': 'Qin Empire',
            'option_d': 'All of the above',
            'correct_option': 'D',
            'explanation': 'Multiple Chinese empires built or rebuilt the Great Wall over centuries. The Qin, Han, and Ming dynasties all contributed.',
            'hints': ['Multiple empires worked on it', 'It was built over a long time']
        },
        {
            'difficulty': 0.5,  # MEDIUM
            'question_text': 'What year did the Declaration of Independence get signed?',
            'option_a': '1774',
            'option_b': '1776',
            'option_c': '1778',
            'option_d': '1783',
            'correct_option': 'B',
            'explanation': 'The Declaration of Independence was signed on July 4, 1776 in Philadelphia.',
            'hints': ['July 4th celebration', 'American independence']
        },
        {
            'difficulty': 0.8,  # HARD
            'question_text': 'Who was the primary architect of the Treaty of Versailles?',
            'option_a': 'Woodrow Wilson',
            'option_b': 'Georges Clemenceau',
            'option_c': 'David Lloyd George',
            'option_d': 'All of the above',
            'correct_option': 'D',
            'explanation': 'The Treaty of Versailles was negotiated by the "Big Three": Wilson (USA), Clemenceau (France), and Lloyd George (Britain).',
            'hints': ['It involved multiple countries', 'After World War I']
        },
    ]
}

def add_questions():
    """Add questions to the database"""
    with app.app_context():
        questions_added = 0
        
        for subject, questions_list in ADDITIONAL_QUESTIONS.items():
            for question_data in questions_list:
                # Check if this question already exists (by text)
                existing = Question.query.filter_by(
                    question_text=question_data['question_text']
                ).first()
                
                if not existing:
                    question = Question(
                        subject=subject,
                        topic='General',  # Add default topic
                        difficulty=question_data['difficulty'],
                        question_text=question_data['question_text'],
                        option_a=question_data['option_a'],
                        option_b=question_data['option_b'],
                        option_c=question_data['option_c'],
                        option_d=question_data['option_d'],
                        correct_option=question_data['correct_option'],
                        explanation=question_data['explanation'],
                        hints=question_data['hints']
                    )
                    db.session.add(question)
                    questions_added += 1
                    print(f"✓ Added: {subject} - {question_data['question_text'][:50]}...")
        
        db.session.commit()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Added {questions_added} new questions!")
        
        total = Question.query.count()
        print(f"\nTotal questions in database: {total}")
        
        by_subject = {}
        for q in Question.query.all():
            subject = q.subject
            by_subject[subject] = by_subject.get(subject, 0) + 1
        
        print("\nQuestions by subject:")
        for subject, count in sorted(by_subject.items()):
            print(f"  {subject}: {count}")

if __name__ == '__main__':
    print("=" * 60)
    print("Adding More Questions")
    print("=" * 60)
    add_questions()
    print("\nDone!")
