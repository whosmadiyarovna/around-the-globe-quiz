# Around the Globe Quiz

An interactive geography quiz built with Python and Streamlit using real country data.

## Features
- **10-question rounds** with a final score summary and knowledge rating at the end.
- **Three question topics**: country capitals, regions, and main languages (`Mixed` mode also available).
- **Difficulty levels (`Easy`, `Medium`, `Hard`)** that adjust how distractors (wrong options) are selected:
  - *Capitals*: `Hard` prefers capitals with a similar name length.
  - *Languages*: `Hard` picks languages from the same region; `Easy` picks from other regions.
- **Four answer options** per question with one correct answer and an explanation after submitting.

## Data Sources
- **World Bank API** — country metadata (`src/data_loader.py`) with local CSV caching.
- **REST Countries API** — country languages and regions (`src/quiz_logic.py`) with local JSON caching and a fallback dictionary.

## Project Structure
```text
.
├── app.py              # Streamlit user interface and session state flow
├── src/
│   ├── data_loader.py  # Fetches, cleans, and caches World Bank country data
│   └── quiz_logic.py   # Generates 4-option questions, checks answers, and scores rounds
├── requirements.txt    # Python dependencies
└── README.md
```

## Installation and Run
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```