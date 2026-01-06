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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is 5 × 3?',
                'option_a': '8',
                'option_b': '10',
                'option_c': '15',
                'option_d': '20',
                'correct_option': 'C',
                'explanation': 'Multiplication of 5 and 3: 5 × 3 = 15',
                'hints': [
                    'Think of 5 groups of 3',
                    '3 + 3 + 3 + 3 + 3 = 15'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is 12 ÷ 4?',
                'option_a': '2',
                'option_b': '3',
                'option_c': '4',
                'option_d': '6',
                'correct_option': 'B',
                'explanation': 'Division: 12 ÷ 4 = 3. We are dividing 12 into 4 equal groups.',
                'hints': [
                    'Think: 4 times what number equals 12?',
                    '4 × 3 = 12'
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
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Solve: 3x - 5 = 10',
                'option_a': 'x = 3',
                'option_b': 'x = 5',
                'option_c': 'x = 15',
                'option_d': 'x = 10',
                'correct_option': 'B',
                'explanation': '3x - 5 = 10. Add 5 to both sides: 3x = 15. Divide by 3: x = 5',
                'hints': [
                    'Isolate the x term first',
                    'Then divide both sides by 3'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the slope of the line y = 2x + 3?',
                'option_a': '3',
                'option_b': '2',
                'option_c': '-2',
                'option_d': '1/2',
                'correct_option': 'B',
                'explanation': 'In the equation y = mx + b, m is the slope. Here m = 2.',
                'hints': [
                    'The slope is the coefficient of x',
                    'Look at the form y = mx + b'
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
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Solve: x² - 7x + 12 = 0',
                'option_a': 'x = 3 or x = 4',
                'option_b': 'x = 2 or x = 6',
                'option_c': 'x = 1 or x = 12',
                'option_d': 'x = -3 or x = -4',
                'correct_option': 'A',
                'explanation': 'Factor: (x - 3)(x - 4) = 0, so x = 3 or x = 4',
                'hints': [
                    'Find two numbers that multiply to 12 and add to -7',
                    'Those numbers are -3 and -4'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the perimeter of a square with side length 4?',
                'option_a': '8',
                'option_b': '12',
                'option_c': '16',
                'option_d': '20',
                'correct_option': 'C',
                'explanation': 'Perimeter = 4 × side length = 4 × 4 = 16',
                'hints': [
                    'Perimeter is the distance around the square',
                    'A square has 4 equal sides'
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
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the area of a triangle with base 10 and height 6?',
                'option_a': '30',
                'option_b': '60',
                'option_c': '16',
                'option_d': '20',
                'correct_option': 'A',
                'explanation': 'Area of triangle = ½ × base × height = ½ × 10 × 6 = 30',
                'hints': [
                    'The formula is ½ × base × height',
                    'That is half of base times height'
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
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'In a circle with radius 5, what is the circumference?',
                'option_a': '5π',
                'option_b': '10π',
                'option_c': '25π',
                'option_d': '15π',
                'correct_option': 'B',
                'explanation': 'Circumference = 2πr = 2π(5) = 10π',
                'hints': [
                    'The formula is C = 2πr',
                    'Or C = πd where d is diameter'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the SI unit of speed or velocity?',
                'option_a': 'Meter',
                'option_b': 'Meter per second',
                'option_c': 'Kilometer',
                'option_d': 'Kilometer per hour',
                'correct_option': 'B',
                'explanation': 'The SI unit of velocity is meter per second (m/s).',
                'hints': [
                    'It involves distance per unit time',
                    'The SI base unit of length is meter'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What does Newton\'s first law state?',
                'option_a': 'F = ma',
                'option_b': 'An object in motion stays in motion unless acted upon',
                'option_c': 'Action and reaction are equal',
                'option_d': 'Energy cannot be created or destroyed',
                'correct_option': 'B',
                'explanation': 'Newton\'s first law of motion: An object at rest or in motion stays that way unless acted upon by an external force.',
                'hints': [
                    'This is about inertia',
                    'It is also called the law of inertia'
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the formula for potential energy?',
                'option_a': 'PE = mv',
                'option_b': 'PE = ½mv²',
                'option_c': 'PE = mgh',
                'option_d': 'PE = ma',
                'correct_option': 'C',
                'explanation': 'Gravitational potential energy is PE = mgh, where m is mass, g is gravity, and h is height.',
                'hints': [
                    'Potential energy depends on height',
                    'PE = mass × gravity × height'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'If an object has a mass of 5 kg and accelerates at 3 m/s², what is the force?',
                'option_a': '8 N',
                'option_b': '12 N',
                'option_c': '15 N',
                'option_d': '20 N',
                'correct_option': 'C',
                'explanation': 'Using F = ma: F = 5 kg × 3 m/s² = 15 N',
                'hints': [
                    'Use the formula F = ma',
                    'Multiply mass by acceleration'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the chemical formula for water?',
                'option_a': 'H₂O',
                'option_b': 'H₂O₂',
                'option_c': 'CO₂',
                'option_d': 'NaCl',
                'correct_option': 'A',
                'explanation': 'Water is made of 2 hydrogen atoms and 1 oxygen atom, so H₂O.',
                'hints': [
                    'Water has hydrogen and oxygen',
                    'Think of the most common compound'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the chemical symbol for carbon?',
                'option_a': 'Ca',
                'option_b': 'Co',
                'option_c': 'C',
                'option_d': 'Cr',
                'correct_option': 'C',
                'explanation': 'The chemical symbol for carbon is C. It is atomic number 6.',
                'hints': [
                    'It is a single letter',
                    'Carbon is the basis of organic chemistry'
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What does an acid have?',
                'option_a': 'pH less than 7',
                'option_b': 'pH greater than 7',
                'option_c': 'pH equal to 7',
                'option_d': 'No pH value',
                'correct_option': 'A',
                'explanation': 'Acids have a pH less than 7. The lower the pH, the more acidic the solution.',
                'hints': [
                    'Acidic solutions are "sour"',
                    'pH less than 7 is acidic'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'What is the molar mass of CO₂?',
                'option_a': '44 g/mol',
                'option_b': '48 g/mol',
                'option_c': '32 g/mol',
                'option_d': '60 g/mol',
                'correct_option': 'A',
                'explanation': 'CO₂: C = 12, O = 16. Molar mass = 12 + 16 + 16 = 44 g/mol',
                'hints': [
                    'Add up the atomic masses',
                    'C = 12, O = 16'
                ]
            }
        ],
        'Biology': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the powerhouse of the cell?',
                'option_a': 'Nucleus',
                'option_b': 'Mitochondria',
                'option_c': 'Chloroplast',
                'option_d': 'Ribosome',
                'correct_option': 'B',
                'explanation': 'Mitochondria is called the powerhouse of the cell because it produces ATP energy.',
                'hints': [
                    'It produces energy',
                    'It is involved in respiration'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What is the basic unit of life?',
                'option_a': 'Atom',
                'option_b': 'Molecule',
                'option_c': 'Cell',
                'option_d': 'Tissue',
                'correct_option': 'C',
                'explanation': 'The cell is the basic unit of life. All living organisms are made of cells.',
                'hints': [
                    'It is the smallest living unit',
                    'Cells make up all organisms'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is the process by which plants make their food?',
                'option_a': 'Respiration',
                'option_b': 'Photosynthesis',
                'option_c': 'Fermentation',
                'option_d': 'Digestion',
                'correct_option': 'B',
                'explanation': 'Photosynthesis is the process where plants convert light energy into chemical energy (glucose).',
                'hints': [
                    'It requires sunlight',
                    'It happens in the chloroplasts'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Which is the correct plural of "child"?',
                'option_a': 'Childs',
                'option_b': 'Childes',
                'option_c': 'Children',
                'option_d': 'Childrens',
                'correct_option': 'C',
                'explanation': '"Child" is an irregular noun. The plural form is "children".',
                'hints': [
                    'This is an irregular plural',
                    'Think of the word used in sentences'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Choose the correct pronoun: "My friend and ____ went to the movies."',
                'option_a': 'me',
                'option_b': 'I',
                'option_c': 'myself',
                'option_d': 'myself',
                'correct_option': 'B',
                'explanation': 'Use "I" here because it is the subject of the sentence. "Me" is used as an object.',
                'hints': [
                    'Think about whether it is a subject or object',
                    'Try saying just the pronoun with the verb'
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What tense is "The students have completed their assignment"?',
                'option_a': 'Simple past',
                'option_b': 'Present perfect',
                'option_c': 'Past perfect',
                'option_d': 'Present tense',
                'correct_option': 'B',
                'explanation': 'Present perfect is formed with "have/has" + past participle. It shows an action that occurred in the past but is relevant to the present.',
                'hints': [
                    'It uses "have" or "has"',
                    'The action started in the past and continues or just finished'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Choose the correct sentence:',
                'option_a': 'The team are playing well',
                'option_b': 'The team is playing well',
                'option_c': 'Both are correct depending on context',
                'option_d': 'Neither is correct',
                'correct_option': 'C',
                'explanation': 'Both are correct. In American English, "is" (singular) is preferred. In British English, "are" (plural) is also acceptable for collective nouns.',
                'hints': [
                    'Collective nouns can be tricky',
                    'American and British English may differ'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Which word is a synonym for "happy"?',
                'option_a': 'Sad',
                'option_b': 'Joyful',
                'option_c': 'Angry',
                'option_d': 'Confused',
                'correct_option': 'B',
                'explanation': 'Joyful is a synonym for happy. Both words mean experiencing or expressing joy.',
                'hints': [
                    'A synonym means similar meaning',
                    'Think of a positive emotion'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What does "persist" mean?',
                'option_a': 'To give up',
                'option_b': 'To continue firmly or obstinately',
                'option_c': 'To stop',
                'option_d': 'To question',
                'correct_option': 'B',
                'explanation': 'Persist means to continue firmly or obstinately despite difficulty or opposition.',
                'hints': [
                    'It is about continuing despite obstacles',
                    'Think of someone who doesn\'t give up'
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'What is an antonym for "bright"?',
                'option_a': 'Light',
                'option_b': 'Brilliant',
                'option_c': 'Dim',
                'option_d': 'Shiny',
                'correct_option': 'C',
                'explanation': 'Dim is an antonym for bright. Bright means giving out much light, while dim means not bright.',
                'hints': [
                    'Antonym means opposite',
                    'Think of the opposite of something glowing'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'What does "melancholy" mean?',
                'option_a': 'Extremely happy',
                'option_b': 'Very angry',
                'option_c': 'Pensive sadness; thoughtfully sad',
                'option_d': 'Confused',
                'correct_option': 'C',
                'explanation': 'Melancholy is a pensive sadness, often with some beauty or nostalgia to it.',
                'hints': [
                    'It is a form of sadness',
                    'But it has a contemplative quality'
                ]
            }
        ],
        'Reading Comprehension': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Based on the statement: "Sarah enjoys reading books in the park." What does Sarah like to do?',
                'option_a': 'Play sports',
                'option_b': 'Read books',
                'option_c': 'Go hiking',
                'option_d': 'Watch movies',
                'correct_option': 'B',
                'explanation': 'The statement directly says that Sarah enjoys reading books, so reading books is what she likes to do.',
                'hints': [
                    'Look for what Sarah "enjoys"',
                    'Reading is mentioned in the sentence'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Based on: "The old library was closed for renovations, and the community had to use the temporary location for three months." Why did the community use a temporary location?',
                'option_a': 'The permanent library burned down',
                'option_b': 'The permanent library was closed for renovations',
                'option_c': 'The temporary location was better',
                'option_d': 'The community preferred it',
                'correct_option': 'B',
                'explanation': 'The text states the library was closed for renovations, which is why the temporary location was used.',
                'hints': [
                    'Look for cause and effect',
                    'Why would they need a temporary location?'
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
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'Who was the first President of the United States?',
                'option_a': 'Thomas Jefferson',
                'option_b': 'George Washington',
                'option_c': 'Benjamin Franklin',
                'option_d': 'John Adams',
                'correct_option': 'B',
                'explanation': 'George Washington was the first President of the United States, serving from 1789 to 1797.',
                'hints': [
                    'He is on the dollar bill',
                    'He was a military general'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What ancient civilization built the pyramids?',
                'option_a': 'Mesopotamia',
                'option_b': 'Ancient Egypt',
                'option_c': 'Ancient Greece',
                'option_d': 'Ancient Rome',
                'correct_option': 'B',
                'explanation': 'Ancient Egypt built the famous pyramids, particularly during the Old Kingdom period.',
                'hints': [
                    'It is in Africa',
                    'Along the Nile River'
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'Which empire built Hadrian\'s Wall?',
                'option_a': 'Ancient Greece',
                'option_b': 'Ancient Egypt',
                'option_c': 'Roman Empire',
                'option_d': 'Ottoman Empire',
                'correct_option': 'C',
                'explanation': 'Hadrian\'s Wall was built by the Roman Empire in Britain around 122 AD under Emperor Hadrian.',
                'hints': [
                    'It is in Britain',
                    'It divides the country north and south'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Who was the first emperor of Rome?',
                'option_a': 'Julius Caesar',
                'option_b': 'Augustus',
                'option_c': 'Nero',
                'option_d': 'Marcus Aurelius',
                'correct_option': 'B',
                'explanation': 'Augustus (originally Octavian) was the first emperor of Rome, ruling from 27 BC to 14 AD.',
                'hints': [
                    'He came after Julius Caesar',
                    'He was a great-nephew of Caesar'
                ]
            }
        ],
        'Medieval History': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'What was the name of the medieval knight\'s code of conduct?',
                'option_a': 'Chivalry',
                'option_b': 'Feudalism',
                'option_c': 'Knighthood',
                'option_d': 'Nobility',
                'correct_option': 'A',
                'explanation': 'Chivalry was the code of conduct for medieval knights, emphasizing honor, loyalty, and virtuous behavior.',
                'hints': [
                    'It is about noble conduct',
                    'It is associated with knights'
                ]
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'In what year did the Black Death begin in Europe?',
                'option_a': '1347',
                'option_b': '1350',
                'option_c': '1340',
                'option_d': '1360',
                'correct_option': 'A',
                'explanation': 'The Black Death arrived in Europe in 1347, becoming one of the most devastating pandemics in history.',
                'hints': [
                    'It was in the 1300s',
                    'It killed millions of people'
                ]
            }
        ],
        'Modern History': [
            {
                'difficulty': QuestionDifficulty.EASY,
                'question_text': 'In what year did the American Revolution begin?',
                'option_a': '1773',
                'option_b': '1774',
                'option_c': '1775',
                'option_d': '1776',
                'correct_option': 'C',
                'explanation': 'The American Revolution began in 1775 with the Battles of Lexington and Concord.',
                'hints': [
                    'It was before the Declaration of Independence',
                    'Fighting started at Lexington and Concord'
                ]
            },
            {
                'difficulty': QuestionDifficulty.EASY,
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
            },
            {
                'difficulty': QuestionDifficulty.MEDIUM,
                'question_text': 'In what year did the Berlin Wall fall?',
                'option_a': '1987',
                'option_b': '1988',
                'option_c': '1989',
                'option_d': '1990',
                'correct_option': 'C',
                'explanation': 'The Berlin Wall fell on November 9, 1989, symbolizing the end of the Cold War.',
                'hints': [
                    'It was late 1980s',
                    'It happened after the Cold War began to thaw'
                ]
            },
            {
                'difficulty': QuestionDifficulty.HARD,
                'question_text': 'Which country was the first to grant women\'s suffrage at the national level?',
                'option_a': 'United Kingdom',
                'option_b': 'New Zealand',
                'option_c': 'United States',
                'option_d': 'France',
                'correct_option': 'B',
                'explanation': 'New Zealand was the first country to grant women\'s suffrage at the national level in 1893.',
                'hints': [
                    'It is not a European country',
                    'It is in the Southern Hemisphere'
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
