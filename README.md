# MSthon Trivia 🎮

A "Who Wants to Be a Millionaire" style multiple-choice trivia quiz application built with Python.

## Features

✨ **Game Features:**
- **10 Progressive Difficulty Questions** - Answer all correctly to win $1,000,000!
- **Prize Levels** - Win increasing amounts of money as you progress
- **3 Lifelines:**
  - 🎯 **50-50** - Removes 2 incorrect answers
  - 📞 **Phone-a-Friend** - Get a hint from a friend with confidence level
  - 👥 **Ask the Audience** - See audience voting percentages
- **One Strike Rule** - One wrong answer ends the game
- **Play Again** - Continue playing multiple rounds

## Installation

### Prerequisites
- Python 3.6 or higher

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/muramuzimichael61-wq/MSthon-Trivia.git
cd MSthon-Trivia
```

2. **No additional dependencies needed!** This application uses only Python's standard library.

## How to Run

```bash
python main.py
```

Or with Python 3:
```bash
python3 main.py
```

## Gameplay Instructions

1. **Start the Game** - Press Enter when prompted to begin
2. **Read the Question** - Each question has 4 multiple-choice options (A, B, C, D)
3. **Choose Your Answer:**
   - Enter the letter of your choice (A/B/C/D)
   - Or use a lifeline by entering (1/2/3)
   - Or skip lifelines by entering 0
4. **Use Lifelines Wisely** - Each lifeline can only be used once
5. **Win or Lose:**
   - Answer correctly to advance to the next question and win the prize
   - Answer incorrectly and the game ends
   - Answer all 10 correctly to win $1,000,000!

## Prize Breakdown

| Question | Prize |
|----------|-------|
| 1 | $100 |
| 2 | $500 |
| 3 | $1,000 |
| 4 | $5,000 |
| 5 | $10,000 |
| 6 | $25,000 |
| 7 | $50,000 |
| 8 | $100,000 |
| 9 | $500,000 |
| 10 | $1,000,000 |

## Example Gameplay

```
============================================================
               WELCOME TO MSTHON TRIVIA
============================================================

Rules:
  • Answer 10 questions correctly to win $1,000,000!
  • You have 3 lifelines:
    1. 50-50 (removes 2 wrong answers)
    2. Phone-a-Friend (get a hint)
    3. Ask the Audience (audience votes)
  • One wrong answer and the game is over!
============================================================


Question 1 of 10
Prize Level: $100
------------------------------------------------------------

What is the capital of France?

  A: London
  B: Berlin
  C: Paris
  D: Madrid

Available Lifelines:
  [1] 50-50
  [2] Phone-a-Friend
  [3] Ask the Audience
  [0] Skip lifelines

Enter your choice (A/B/C/D) or lifeline number (0-3): C

✅ CORRECT ANSWER!
You've won: $100
```

## Customization

You can easily customize the questions by editing the `load_questions()` method in `main.py`:

```python
def load_questions(self) -> List[Question]:
    """Load trivia questions"""
    questions = [
        Question(
            "Your question here?",
            ["Option A", "Option B", "Option C", "Option D"],
            2,  # Index of correct answer (0-3)
            100  # Prize amount
        ),
        # Add more questions...
    ]
```

## Project Structure

```
MSthon-Trivia/
├── main.py           # Main application file
├── README.md         # This file
└── .gitignore        # Git ignore file
```

## Future Enhancements

- 🌐 Add different categories (Science, History, Sports, etc.)
- 📊 Implement a scoring/leaderboard system
- 🎵 Add sound effects
- 🎨 Create a GUI version using tkinter or PyQt
- 💾 Save game progress and statistics
- 🌍 Add difficulty levels
- 🗂️ Load questions from a database or API

## Contributing

Feel free to fork this project and submit pull requests with improvements!

## License

This project is open source and available for personal use and learning.

## Author

Created by muramuzimichael61-wq

---

**Enjoy the game and good luck winning that $1,000,000!** 🎉
