"""Quiz question generators, difficulty logic, and answer checking."""

import random
import pandas as pd

TOTAL_QUESTIONS = 10

# Simple dictionary mapping country names to their main language
COUNTRY_LANGUAGES = {
    "Argentina": "Spanish",
    "Australia": "English",
    "Austria": "German",
    "Belgium": "Dutch",
    "Brazil": "Portuguese",
    "Canada": "English",
    "Chile": "Spanish",
    "China": "Mandarin",
    "Colombia": "Spanish",
    "Croatia": "Croatian",
    "Czechia": "Czech",
    "Denmark": "Danish",
    "Egypt": "Arabic",
    "Finland": "Finnish",
    "France": "French",
    "Germany": "German",
    "Greece": "Greek",
    "Hungary": "Hungarian",
    "India": "Hindi",
    "Indonesia": "Indonesian",
    "Ireland": "English",
    "Italy": "Italian",
    "Japan": "Japanese",
    "Kazakhstan": "Kazakh",
    "Mexico": "Spanish",
    "Morocco": "Arabic",
    "Netherlands": "Dutch",
    "New Zealand": "English",
    "Norway": "Norwegian",
    "Peru": "Spanish",
    "Poland": "Polish",
    "Portugal": "Portuguese",
    "Romania": "Romanian",
    "Saudi Arabia": "Arabic",
    "South Africa": "Zulu",
    "South Korea": "Korean",
    "Spain": "Spanish",
    "Sweden": "Swedish",
    "Switzerland": "German",
    "Thailand": "Thai",
    "Turkiye": "Turkish",
    "Ukraine": "Ukrainian",
    "United Arab Emirates": "Arabic",
    "United Kingdom": "English",
    "United States": "English",
    "Uzbekistan": "Uzbek",
    "Vietnam": "Vietnamese",
}


def _pick_four_options(wrong_candidates: list[str], correct_answer: str) -> list[str]:
    """Pick 3 wrong answers, combine with the right answer, and shuffle all 4."""
    # Remove duplicates and accidental match with the correct answer
    unique_wrong = []
    for item in wrong_candidates:
        if item and item != correct_answer and item not in unique_wrong:
            unique_wrong.append(item)

    # Shuffle wrong options and take 3 of them
    random.shuffle(unique_wrong)
    three_wrong = unique_wrong[:3]

    # Combine 3 wrong answers + 1 correct answer = 4 options total
    options = three_wrong + [correct_answer]
    random.shuffle(options)
    return options


def make_capital_question(df: pd.DataFrame, difficulty: str = "Medium") -> dict:
    """Create a 4-option capital question adjusted by difficulty."""
    # Convert DataFrame into a plain list of row dictionaries
    rows = df.to_dict(orient="records")

    # Keep only rows that have non-empty country and capital
    valid_rows = []
    for row in rows:
        country = row.get("country")
        capital = row.get("capital")
        if isinstance(country, str) and isinstance(capital, str):
            country = country.strip()
            capital = capital.strip()
            if country and capital:
                valid_rows.append({"country": country, "capital": capital})

    # Choose one random country
    target = random.choice(valid_rows)
    country_name = target["country"]
    correct_capital = target["capital"]

    # In Hard mode, prefer capitals with a similar word length to make guessing harder
    candidates = []
    if difficulty == "Hard":
        for row in valid_rows:
            cap = row["capital"]
            if cap != correct_capital and abs(len(cap) - len(correct_capital)) <= 2:
                candidates.append(cap)

    # Fallback to all other capitals if not enough similar-length capitals were found
    if len(candidates) < 3:
        candidates = [row["capital"] for row in valid_rows if row["capital"] != correct_capital]

    options = _pick_four_options(candidates, correct_capital)

    return {
        "type": "capital",
        "difficulty": difficulty,
        "question": f"What is the capital of {country_name}?",
        "options": options,
        "answer": correct_capital,
        "explanation": f"The capital of {country_name} is {correct_capital}.",
    }


def make_region_question(df: pd.DataFrame, difficulty: str = "Medium") -> dict:
    """Create a 4-option region question."""
    # Convert DataFrame into a plain list of row dictionaries
    rows = df.to_dict(orient="records")

    # Keep rows with valid country and region
    valid_rows = []
    for row in rows:
        country = row.get("country")
        region = row.get("region")
        if isinstance(country, str) and isinstance(region, str):
            country = country.strip()
            region = region.strip()
            if country and region:
                valid_rows.append({"country": country, "region": region})

    target = random.choice(valid_rows)
    country_name = target["country"]
    correct_region = target["region"]

    # Collect all other regions as distractors
    other_regions = [row["region"] for row in valid_rows if row["region"] != correct_region]
    options = _pick_four_options(other_regions, correct_region)

    return {
        "type": "region",
        "difficulty": difficulty,
        "question": f"In which region is {country_name} located?",
        "options": options,
        "answer": correct_region,
        "explanation": f"{country_name} is located in {correct_region}.",
    }


def make_language_question(df: pd.DataFrame, difficulty: str = "Medium") -> dict:
    """Create a 4-option language question adjusted by difficulty."""
    # Convert DataFrame into a plain list of row dictionaries
    rows = df.to_dict(orient="records")

    # Match countries from our dataset with COUNTRY_LANGUAGES
    entries = []
    for row in rows:
        country = row.get("country")
        region = row.get("region")
        if isinstance(country, str):
            country_clean = country.strip()
            if country_clean in COUNTRY_LANGUAGES:
                entries.append(
                    {
                        "country": country_clean,
                        "region": str(region).strip() if region else "",
                        "language": COUNTRY_LANGUAGES[country_clean],
                    }
                )

    # Pick one country for the question
    target = random.choice(entries)
    country_name = target["country"]
    target_region = target["region"]
    correct_language = target["language"]

    # Hard mode: pick wrong languages from countries in the SAME region (more tricky)
    # Easy mode: pick wrong languages from OTHER regions (more distinct)
    candidates = []
    if difficulty == "Hard":
        for item in entries:
            if item["region"] == target_region and item["language"] != correct_language:
                candidates.append(item["language"])
    elif difficulty == "Easy":
        for item in entries:
            if item["region"] != target_region and item["language"] != correct_language:
                candidates.append(item["language"])

    # If Hard/Easy list has fewer than 3 unique languages, fill from all languages
    if len(set(c for c in candidates if c != correct_language)) < 3:
        candidates = [item["language"] for item in entries if item["language"] != correct_language]

    options = _pick_four_options(candidates, correct_language)

    return {
        "type": "language",
        "difficulty": difficulty,
        "question": f"What is a main language spoken in {country_name}?",
        "options": options,
        "answer": correct_language,
        "explanation": f"A main language in {country_name} is {correct_language}.",
    }


def get_question(
    df: pd.DataFrame,
    mode: str = "Mixed",
    difficulty: str = "Medium",
) -> dict:
    """Generate one question based on mode ('Mixed', 'Capitals', 'Regions', 'Languages')."""
    if mode == "Capitals":
        return make_capital_question(df, difficulty=difficulty)
    if mode == "Regions":
        return make_region_question(df, difficulty=difficulty)
    if mode == "Languages":
        return make_language_question(df, difficulty=difficulty)

    # Mixed mode picks randomly among the 3 question types
    q_type = random.choice(["capital", "region", "language"])
    if q_type == "capital":
        return make_capital_question(df, difficulty=difficulty)
    if q_type == "region":
        return make_region_question(df, difficulty=difficulty)
    return make_language_question(df, difficulty=difficulty)


def check_answer(user_answer: str, correct_answer: str, score: int) -> tuple[bool, int]:
    """Check if user_answer is correct and return (is_correct, updated_score)."""
    # Add 1 point if the selected answer matches the correct answer
    if user_answer == correct_answer:
        return True, score + 1
    return False, score


def get_final_verdict(score: int, total_questions: int = TOTAL_QUESTIONS) -> tuple[str, str]:
    """Return a title and message at the end of a 10-question quiz."""
    # High score verdict
    if score >= 9:
        return (
            "🏆 Geography Superstar!",
            f"You scored {score} out of {total_questions}! Awesome job — you really know your way around the globe.",
        )
    # Good score verdict
    if score >= 6:
        return (
            "🌍 Great Job!",
            f"You scored {score} out of {total_questions}! Solid geography knowledge with just a few details left.",
        )
    # Average score verdict
    if score >= 2:
        return (
            "🧭 Nice Try!",
            f"You scored {score} out of {total_questions}. A good start — a bit more practice and you will ace it!",
        )
    # Very low score verdict (< 2)
    return (
        "📚 Time to Study Geography!",
        f"You scored {score} out of {total_questions}. No worries — looks like it's time to explore the map and study geography!",
    )