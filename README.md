# Around the Globe Quiz

Around the Globe Quiz lets you test your world geography knowledge across 10-question rounds with adjustable difficulty and instant feedback in a web app.

built with Streamlit · Python 3.11+

## What the app does

| Mode / Feature | What you can do |
| :--- | :--- |
| **Capitals** (`src/quiz_logic.py`) | Answer 4-option questions about country capitals; `Hard` mode favors capitals with a similar name length. |
| **Regions** (`src/quiz_logic.py`) | Identify which region a country belongs to from 4 answer choices. |
| **Languages** (`src/quiz_logic.py`) | Guess a main language spoken in a country; `Hard` mode picks distractors from the same region, while `Easy` mode draws from other regions. |
| **Mixed & 10-Question Round** (`app.py`) | Play a 10-question round with live score tracking, explanations after each answer, a final knowledge verdict at the end, and a restart option. |

## How scoring and difficulty work

Each round consists of **10 questions** with **4 answer options** and **1 correct answer** per question. Selecting the right option adds `+1` point to the round score.

Distractor selection scales with the selected difficulty:

| Difficulty | How options are generated |
| :--- | :--- |
| **Easy** | Picks more distinct options (for example, languages from other regions when available). |
| **Medium** | Uses standard randomized distractors alongside the correct answer. |
| **Hard** | Picks trickier distractors (such as capitals with similar name length or languages from the same region). |

At the end of all 10 questions, `get_final_verdict()` returns a summary message based on the final score (from a top score of `9+` down to `< 2` when extra geography study is recommended).

## Data sources

- **World Bank API**: used in `src/data_loader.py` to fetch and clean country metadata (country names, regions, capitals).
- **REST Countries API**: used in `src/quiz_logic.py` to fetch country languages and regions, with a local fallback dictionary if the API is unreachable.
- **Local cache (`data/`)**: caches fetched country and language data locally so repeated runs are fast and reliable without hitting external APIs every time.

## Libraries

| Library | Used for |
| :--- | :--- |
| `requests` | calling the World Bank and REST Countries APIs |
| `pandas` | storing and iterating over country records |
| `streamlit` | building the interactive web quiz and `session_state` round flow |

Exact versions are listed in `requirements.txt`.

## Setup

1. Clone the repository and enter the folder:

   ```bash
   git clone [https://github.com/](https://github.com/)<your-user>/around-the-globe-quiz.git
   cd around-the-globe-quiz

## Project Structure
```text
.
around-the-globe-quiz/
├── app.py              # Streamlit entry point, session state, 10-question flow, and final summary
├── src/
│   ├── __init__.py
│   ├── data_loader.py  # Fetches, cleans, and caches World Bank country data
│   └── quiz_logic.py   # Generates 4-option questions by difficulty, checks answers, and scores rounds
├── data/               # Local cached data files (ignored in git)
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