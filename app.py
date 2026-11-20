"""Streamlit interface for Around the Globe Quiz."""

import streamlit as st

from src.data_loader import load_data
from src.quiz_logic import TOTAL_QUESTIONS, check_answer, get_final_verdict, get_question


def start_new_round(df, mode: str, difficulty: str) -> None:
    """Reset counters and start a fresh 10-question quiz round."""
    # Reset score and answered questions count
    st.session_state.score = 0
    st.session_state.answered_count = 0
    st.session_state.submitted = False
    st.session_state.is_correct = None
    st.session_state.active_mode = mode
    st.session_state.active_difficulty = difficulty
    # Generate the first question right away
    st.session_state.current_question = get_question(df, mode=mode, difficulty=difficulty)


def init_session_state(df, mode: str, difficulty: str) -> None:
    """Initialize session_state variables on first load."""
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "answered_count" not in st.session_state:
        st.session_state.answered_count = 0
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "is_correct" not in st.session_state:
        st.session_state.is_correct = None
    if "active_mode" not in st.session_state:
        st.session_state.active_mode = mode
    if "active_difficulty" not in st.session_state:
        st.session_state.active_difficulty = difficulty
    if "current_question" not in st.session_state:
        st.session_state.current_question = get_question(df, mode=mode, difficulty=difficulty)


def main() -> None:
    """Run the Around the Globe Quiz app."""
    st.set_page_config(page_title="Around the Globe Quiz", page_icon="🌍")

    st.title("🌍 Around the Globe Quiz")
    st.write(f"Answer {TOTAL_QUESTIONS} questions about capitals, regions, and country languages.")

    # Load data from cache or World Bank API
    try:
        df = load_data(use_cache=True)
    except Exception as error:
        st.error(f"Could not load data: {error}")
        return

    # Sidebar settings: question topic, difficulty level, and restart button
    st.sidebar.header("Quiz Settings")
    mode = st.sidebar.selectbox(
        "Topic",
        options=["Mixed", "Capitals", "Regions", "Languages"],
    )
    difficulty = st.sidebar.selectbox(
        "Difficulty",
        options=["Easy", "Medium", "Hard"],
        index=1,
    )

    init_session_state(df, mode, difficulty)

    # If user changed topic or difficulty, start a fresh round with those settings
    if st.session_state.active_mode != mode or st.session_state.active_difficulty != difficulty:
        start_new_round(df, mode, difficulty)
        st.rerun()

    if st.sidebar.button("Restart Quiz"):
        start_new_round(df, mode, difficulty)
        st.rerun()

    # Top progress and score bar
    current_q_number = min(st.session_state.answered_count + 1, TOTAL_QUESTIONS)
    col1, col2, col3 = st.columns(3)
    col1.metric("Question", f"{current_q_number} / {TOTAL_QUESTIONS}")
    col2.metric("Score", st.session_state.score)
    col3.metric("Difficulty", difficulty)

    st.divider()

    # Show final summary once all 10 questions have been answered
    if st.session_state.answered_count >= TOTAL_QUESTIONS:
        title, message = get_final_verdict(st.session_state.score, TOTAL_QUESTIONS)
        st.subheader(title)
        st.write(message)

        if st.button("Play Again"):
            start_new_round(df, mode, difficulty)
            st.rerun()
        return

    question_data = st.session_state.current_question
    st.subheader(question_data["question"])

    # Display 4 answer options using radio buttons
    selected_option = st.radio(
        "Choose one of the 4 options:",
        options=question_data["options"],
        key=f"q_{st.session_state.answered_count}_{question_data['question']}",
        disabled=st.session_state.submitted,
    )

    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            is_correct, new_score = check_answer(
                user_answer=selected_option,
                correct_answer=question_data["answer"],
                score=st.session_state.score,
            )
            st.session_state.score = new_score
            st.session_state.answered_count += 1
            st.session_state.submitted = True
            st.session_state.is_correct = is_correct
            st.rerun()
    else:
        # Show immediate feedback and explanation
        if st.session_state.is_correct:
            st.success("Correct! +1 point")
        else:
            st.error(f"Wrong! Correct answer: {question_data['answer']}")

        st.info(question_data["explanation"])

        # Move to next question or finish round after question 10
        button_label = "See Final Result" if st.session_state.answered_count >= TOTAL_QUESTIONS else "Next Question"
        if st.button(button_label):
            if st.session_state.answered_count < TOTAL_QUESTIONS:
                st.session_state.current_question = get_question(df, mode=mode, difficulty=difficulty)
            st.session_state.submitted = False
            st.session_state.is_correct = None
            st.rerun()


if __name__ == "__main__":
    main()