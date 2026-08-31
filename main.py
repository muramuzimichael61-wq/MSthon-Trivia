#!/usr/bin/env python3
"""
MSthon Trivia - A "Who Wants to Be a Millionaire" style quiz application
"""

import random
from typing import List, Dict, Tuple

class Question:
    """Represents a trivia question"""
    def __init__(self, question: str, options: List[str], correct_answer: int, prize: int):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer  # Index of correct option (0-3)
        self.prize = prize

class MSthonTrivia:
    """Main trivia game class"""
    
    PRIZE_LEVELS = [
        100, 500, 1000, 5000, 10000, 25000, 50000, 100000, 500000, 1000000
    ]
    
    def __init__(self):
        self.questions = self.load_questions()
        self.current_question_index = 0
        self.current_prize = 0
        self.lifelines_used = {
            '50-50': False,
            'phone-a-friend': False,
            'ask-audience': False
        }
        self.game_over = False
        self.won = False
        
    def load_questions(self) -> List[Question]:
        """Load trivia questions"""
        questions = [
            Question(
                "What is the capital of France?",
                ["London", "Berlin", "Paris", "Madrid"],
                2,
                100
            ),
            Question(
                "Which planet is known as the Red Planet?",
                ["Venus", "Mars", "Jupiter", "Saturn"],
                1,
                500
            ),
            Question(
                "Who wrote 'Romeo and Juliet'?",
                ["Jane Austen", "Charles Dickens", "William Shakespeare", "Mark Twain"],
                2,
                1000
            ),
            Question(
                "What is the largest ocean on Earth?",
                ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
                3,
                5000
            ),
            Question(
                "In what year did the Titanic sink?",
                ["1912", "1898", "1920", "1905"],
                0,
                10000
            ),
            Question(
                "What is the chemical symbol for Gold?",
                ["Go", "Gd", "Au", "Ag"],
                2,
                25000
            ),
            Question(
                "Which country is home to the Great Wall?",
                ["Japan", "Korea", "China", "Vietnam"],
                2,
                50000
            ),
            Question(
                "How many strings does a violin have?",
                ["3", "4", "5", "6"],
                1,
                100000
            ),
            Question(
                "What is the smallest prime number?",
                ["0", "1", "2", "3"],
                2,
                500000
            ),
            Question(
                "Who painted the Mona Lisa?",
                ["Michelangelo", "Leonardo da Vinci", "Raphael", "Donatello"],
                1,
                1000000
            ),
        ]
        random.shuffle(questions)
        return questions
    
    def get_current_question(self) -> Question:
        """Get the current question"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print(" " * 15 + "WELCOME TO MSTHON TRIVIA")
        print("="*60)
        print("\nRules:")
        print("  • Answer 10 questions correctly to win $1,000,000!")
        print("  • You have 3 lifelines:")
        print("    1. 50-50 (removes 2 wrong answers)")
        print("    2. Phone-a-Friend (get a hint)")
        print("    3. Ask the Audience (audience votes)")
        print("  • One wrong answer and the game is over!")
        print("="*60 + "\n")
    
    def display_question(self, question: Question):
        """Display current question and options"""
        print(f"\nQuestion {self.current_question_index + 1} of {len(self.questions)}")
        print(f"Prize Level: ${self.PRIZE_LEVELS[self.current_question_index]:,}")
        print("-" * 60)
        print(f"\n{question.question}\n")
        
        for i, option in enumerate(question.options, 1):
            print(f"  {chr(64+i)}: {option}")
        
        print()
    
    def display_lifelines(self):
        """Display available lifelines"""
        print("\nAvailable Lifelines:")
        if not self.lifelines_used['50-50']:
            print("  [1] 50-50")
        if not self.lifelines_used['phone-a-friend']:
            print("  [2] Phone-a-Friend")
        if not self.lifelines_used['ask-audience']:
            print("  [3] Ask the Audience")
        print("  [0] Skip lifelines")
        print()
    
    def use_50_50(self, question: Question) -> List[int]:
        """Remove 2 wrong answers"""
        wrong_indices = [i for i in range(4) if i != question.correct_answer]
        removed = random.sample(wrong_indices, 2)
        self.lifelines_used['50-50'] = True
        
        print("\n🎯 50-50 Lifeline Used!")
        print("Two wrong answers have been removed:\n")
        
        for i, option in enumerate(question.options, 1):
            if i - 1 not in removed:
                print(f"  {chr(64+i)}: {option}")
        
        return removed
    
    def use_phone_a_friend(self, question: Question):
        """Get a hint from a friend"""
        self.lifelines_used['phone-a-friend'] = True
        confidence = random.randint(60, 95)
        correct_letter = chr(65 + question.correct_answer)
        
        print(f"\n📞 Phone-a-Friend Lifeline Used!")
        print(f"Your friend thinks the answer is '{correct_letter}'")
        print(f"Confidence level: {confidence}%\n")
    
    def use_ask_audience(self, question: Question):
        """Get audience vote"""
        self.lifelines_used['ask-audience'] = True
        
        print("\n👥 Ask the Audience Lifeline Used!")
        print("Audience voting results:\n")
        
        votes = [0, 0, 0, 0]
        votes[question.correct_answer] = random.randint(45, 65)
        remaining = 100 - votes[question.correct_answer]
        
        for i in range(4):
            if i != question.correct_answer:
                votes[i] = random.randint(5, remaining // 3)
        
        # Normalize to 100
        votes[question.correct_answer] = 100 - sum(votes)
        
        for i, vote in enumerate(votes, 1):
            print(f"  {chr(64+i)}: {vote}%")
        print()
    
    def check_answer(self, user_choice: int, question: Question) -> bool:
        """Check if the answer is correct"""
        if user_choice == question.correct_answer:
            print("\n✅ CORRECT ANSWER!")
            self.current_prize = self.PRIZE_LEVELS[self.current_question_index]
            print(f"You've won: ${self.current_prize:,}")
            
            if self.current_question_index == len(self.questions) - 1:
                self.won = True
                self.game_over = True
            else:
                self.current_question_index += 1
            
            return True
        else:
            print(f"\n❌ WRONG ANSWER!")
            print(f"The correct answer was: {chr(65 + question.correct_answer)}: {question.options[question.correct_answer]}")
            print(f"\nYou won: ${self.current_prize:,}")
            self.game_over = True
            return False
    
    def play(self):
        """Main game loop"""
        self.display_welcome()
        input("Press Enter to start the game...\n")
        
        while not self.game_over:
            question = self.get_current_question()
            
            if question is None:
                break
            
            self.display_question(question)
            self.display_lifelines()
            
            while True:
                try:
                    choice = input("Enter your choice (A/B/C/D) or lifeline number (0-3): ").upper().strip()
                    
                    if choice == '0':
                        break
                    elif choice in ['1', '2', '3']:
                        lifeline_num = int(choice)
                        if lifeline_num == 1 and not self.lifelines_used['50-50']:
                            self.use_50_50(question)
                        elif lifeline_num == 2 and not self.lifelines_used['phone-a-friend']:
                            self.use_phone_a_friend(question)
                        elif lifeline_num == 3 and not self.lifelines_used['ask-audience']:
                            self.use_ask_audience(question)
                        else:
                            print("This lifeline has already been used!\n")
                        continue
                    elif choice in ['A', 'B', 'C', 'D']:
                        answer_index = ord(choice) - 65
                        self.check_answer(answer_index, question)
                        break
                    else:
                        print("Invalid input! Please enter A, B, C, D, or a lifeline number (0-3).\n")
                except Exception as e:
                    print(f"Error: {e}. Please try again.\n")
        
        self.display_game_over()
    
    def display_game_over(self):
        """Display game over message"""
        print("\n" + "="*60)
        if self.won:
            print(" " * 20 + "🎉 CONGRATULATIONS! 🎉")
            print(" " * 15 + "YOU'VE WON $1,000,000!")
        else:
            print(" " * 25 + "GAME OVER")
            print(f" " * 20 + f"Final Prize: ${self.current_prize:,}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    game = MSthonTrivia()
    game.play()
    
    # Ask to play again
    while True:
        play_again = input("Would you like to play again? (yes/no): ").lower().strip()
        if play_again in ['yes', 'y']:
            game = MSthonTrivia()
            game.play()
        elif play_again in ['no', 'n']:
            print("\nThanks for playing MSthon Trivia! Goodbye! 👋\n")
            break
        else:
            print("Please enter 'yes' or 'no'.")


if __name__ == "__main__":
    main()
