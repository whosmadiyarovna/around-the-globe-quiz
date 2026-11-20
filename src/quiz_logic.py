"""Quiz question generators and answer checking for Around the Globe Quiz."""

import random
import pandas as pd


def make_capital_question(df: pd.DataFrame) -> dict:
    """Create a multiple-choice question asking for a country's capital."""
    # Convert the pandas DataFrame into a regular list of dictionaries
    rows = df.to_dict(orient="records")

    # Keep only entries where both country and capital are non-empty strings
    valid_rows = []
    for row in rows:
        country = row.get("country")
        capital = row.get("capital")
        if isinstance(country, str) and isinstance(capital, str):
            country = country.strip()
            capital = capital.strip()
            if country and capital:
                valid_rows.append({"country": country, "capital": capital})

    # Pick one random country for the question
    target = random.choice(valid_rows)
    country_name = target["country"]
    correct_capital = target["capital"]

    # Collect unique capitals from other countries to use as wrong answers
    wrong_capitals = []
    for row in valid_rows:
        cap = row["capital"]
        if cap != correct_capital and cap not in wrong_capitals:
            wrong_capitals.append(cap)

    # Shuffle wrong capitals and take up to 3 distractors
    random.shuffle(wrong_capitals)
    wrong_options = wrong_capitals[: min(3, len(wrong_capitals))]

    # Combine wrong options with the right answer and shuffle the final list
    options = wrong_options + [correct_capital]
    random.shuffle(options)

    return {
        "question": f"What is the capital of {country_name}?",
        "options": options,
        "answer": correct_capital,
        "explanation": f"The capital of {country_name} is {correct_capital}.",
    }


def make_region_question(df: pd.DataFrame) -> dict:
    """Create a multiple-choice question asking which region a country is in."""
    # Convert DataFrame to a plain list of row dictionaries
    rows = df.to_dict(orient="records")

    # Keep only rows that have both a country name and a region name
    valid_rows = []
    for row in rows:
        country = row.get("country")
        region = row.get("region")
        if isinstance(country, str) and isinstance(region, str):
            country = country.strip()
            region = region.strip()
            if country and region:
                valid_rows.append({"country": country, "region": region})

    # Choose one random country as the question target
    target = random.choice(valid_rows)
    country_name = target["country"]
    correct_region = target["region"]

    # Gather other unique regions as wrong choices
    wrong_regions = []
    for row in valid_rows:
        reg = row["region"]
        if reg != correct_region and reg not in wrong_regions:
            wrong_regions.append(reg)

    # Shuffle and pick up to 3 wrong regions
    random.shuffle(wrong_regions)
    wrong_options = wrong_regions[: min(3, len(wrong_regions))]

    # Add the correct region and shuffle all answer options
    options = wrong_options + [correct_region]
    random.shuffle(options)

    return {
        "question": f"In which region is {country_name} located?",
        "options": options,
        "answer": correct_region,
        "explanation": f"{country_name} is located in {correct_region}.",
    }


def make_equator_question(df: pd.DataFrame) -> dict:
    """Create a question asking which of two countries is closer to the equator."""
    # Convert DataFrame to a plain list of dictionaries
    rows = df.to_dict(orient="records")

    # Keep countries with valid numeric latitude and compute distance from 0° equator
    valid_rows = []
    for row in rows:
        country = row.get("country")
        lat = row.get("latitude")
        if isinstance(country, str) and country.strip() and lat is not None:
            try:
                lat_num = float(lat)
            except (ValueError, TypeError):
                # Skip rows where latitude cannot be converted to a number
                continue

            # Distance to the equator is the absolute value of latitude
            valid_rows.append(
                {
                    "country": country.strip(),
                    "distance": abs(lat_num),
                }
            )

    # Pick two distinct countries at random
    first, second = random.sample(valid_rows, 2)

    # Smaller distance means closer to the equator
    if first["distance"] <= second["distance"]:
        closer = first
    else:
        closer = second

    # Put both countries in options and shuffle their order
    options = [first["country"], second["country"]]
    random.shuffle(options)

    return {
        "question": "Which country is closer to the equator?",
        "options": options,
        "answer": closer["country"],
        "explanation": (
            f"{first['country']}: {round(first['distance'], 1)}° from equator | "
            f"{second['country']}: {round(second['distance'], 1)}° from equator."
        ),
    }


def get_question(df: pd.DataFrame, mode: str = "Mixed") -> dict:
    """Generate one quiz question for the chosen mode."""
    # Return a specific question type if requested
    if mode == "Capitals":
        return make_capital_question(df)
    if mode == "Regions":
        return make_region_question(df)
    if mode == "Equator":
        return make_equator_question(df)

    # In Mixed mode, pick one of the three question types randomly
    question_type = random.choice(["capital", "region", "equator"])
    if question_type == "capital":
        return make_capital_question(df)
    if question_type == "region":
        return make_region_question(df)
    return make_equator_question(df)


def check_answer(user_answer: str, correct_answer: str, score: int) -> tuple[bool, int]:
    """Compare the user's answer with the correct one and update the score."""
    # Award 1 point if the answer matches, otherwise keep the current score
    if user_answer == correct_answer:
        return True, score + 1
    return False, score