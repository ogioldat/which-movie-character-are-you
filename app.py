from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

from quiz.graph import (
    calculate_cosine_similarity,
    get_character_profile,
    get_character_summaries,
)
from quiz.quiz import embed_user_input, load_questions

st.set_page_config(
    page_title="Nolan Character Resonance Quiz",
    page_icon="🎬",
    layout="wide",
)


# Provide multiple aliases so we can still find an image if Neo4j uses
# different naming for the same character.
CHARACTER_IMAGE_MAP: Dict[str, str] = {
    "alfred borden": "img/alfred-borden.jpg",
    "borden": "img/alfred-borden.jpg",
    "alfred pennyworth": "img/alfred-pennyworth.jpg",
    "alfred": "img/alfred-pennyworth.jpg",
    "bane": "img/bane.webp",
    "bruce wayne": "img/bruce-wayne.jpg",
    "batman": "img/bruce-wayne.jpg",
    "dom cobb": "img/dom-cobb.jpg",
    "dominick cobb": "img/dom-cobb.jpg",
    "joseph cooper": "img/joseph-cooper.jpg",
    "cooper": "img/joseph-cooper.jpg",
    "j. cooper": "img/joseph-cooper.jpg",
    "j cooper": "img/joseph-cooper.jpg",
    "leonard shelby": "img/leonard-shelby.jpg",
    "leonard": "img/leonard-shelby.jpg",
    "the joker": "img/joker.jpg",
    "joker": "img/joker.jpg",
    "arthur fleck": "img/joker.jpg",
    "j. robert oppenheimer": "img/oppenheimer.jpg",
    "oppenheimer": "img/oppenheimer.jpg",
    "robert angier": "img/robert-angier.jpg",
    "selina kyle": "img/catwoman.jpg",
    "selina kyle (catwoman)": "img/catwoman.jpg",
    "catwoman": "img/catwoman.jpg",
    "neil": "img/neil.jpg",
    "harvey dent": "img/harvey-dent.jpg",
    "two face": "img/harvey-dent.jpg",
    "two-face": "img/harvey-dent.jpg",
    "mal cobb": "img/mal-cobb.jpg",
    "mal": "img/mal-cobb.jpg",
    "dr. mann": "img/dr-mann.webp",
    "dr mann": "img/dr-mann.webp",
    "doctor mann": "img/dr-mann.webp",
}


@st.cache_data(show_spinner=False)
def get_questions() -> List[dict]:
    return load_questions()


@st.cache_data(show_spinner=False)
def get_gallery_images() -> List[Tuple[str, Path]]:
    folder = Path("img")
    valid_suffixes = {".png", ".jpg", ".jpeg", ".jpg"}
    entries: List[Tuple[str, Path]] = []
    for path in sorted(folder.glob("*")):
        if path.suffix.lower() not in valid_suffixes:
            continue
        label = path.stem.replace("-", " ").replace("_", " ").title()
        entries.append((label, path))
    return entries


@st.cache_data(show_spinner=False)
def fetch_character_summaries() -> List[dict]:
    try:
        return get_character_summaries()
    except Exception as exc:
        # Provide feedback but keep the UI usable without the database.
        st.warning(
            "Could not load character summaries from Neo4j. "
            "The quiz will still work, but landing page metadata will be limited."
        )
        st.error(exc)
        return []


def find_character_image(name: str) -> Optional[str]:
    normalized = name.strip().lower()
    if normalized in CHARACTER_IMAGE_MAP:
        return CHARACTER_IMAGE_MAP[normalized]
    # Fallback: try to find partial matches.
    for alias, image in CHARACTER_IMAGE_MAP.items():
        if normalized in alias:
            return image
    return None


def initialize_state() -> None:
    if "started" not in st.session_state:
        st.session_state.started = False
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "results" not in st.session_state:
        st.session_state.results = None


def render_landing_page() -> None:
    st.title("Which Nolan character mirrors your instincts?")
    st.write(
        "Dive into a short, cinematic personality quiz inspired by characters from "
        "Christopher Nolan's films. When you are ready, tap **Begin** to start."
    )

    summaries = fetch_character_summaries()
    if summaries:
        with st.expander("Who's in the graph right now?", expanded=False):
            for entry in summaries:
                st.write(f"- {entry['name']} — *{entry['movie']}*")

    st.write("### Cast Sneak Peek")
    gallery = get_gallery_images()
    cols = st.columns(3)
    for idx, (label, path) in enumerate(gallery):
        with cols[idx % 3]:
            st.image(str(path), caption=label)

    if st.button("🎬 Begin the Quiz", use_container_width=True):
        st.session_state.started = True


def collect_answers(questions: List[dict]) -> Dict[int, int]:
    answers: Dict[int, int] = {}
    for question in questions:
        qid = question["id"]
        options = [answer["text"] for answer in question.get("answers", [])]
        selected = st.selectbox(
            question["text"],
            options,
            key=f"question_{qid}",
            placeholder="Pick the option that feels right",
        )
        if selected is None:
            continue
        answers[qid] = options.index(selected)
    return answers


def generate_results(
    questions: List[dict], answers: Dict[int, int]
) -> Dict[str, object]:
    user_answers: Dict[str, str] = {}
    for question in questions:
        qid = question["id"]
        if qid not in answers:
            continue
        answer_idx = answers[qid]
        user_answers[question["text"]] = question["answers"][answer_idx]["text"]

    if not user_answers:
        raise ValueError("No answers were provided.")

    embedded = embed_user_input(user_answers)
    matches = calculate_cosine_similarity(3, embedded)
    top_match_name = matches[0][0] if matches else None
    profile = (
        get_character_profile(top_match_name) if top_match_name else None
    )
    return {"answers": user_answers, "matches": matches, "profile": profile}


def render_quiz_body() -> None:
    questions = get_questions()
    if not questions:
        st.error("No questions available. Please check data/questions.json.")
        return

    st.header("Answer instinctively")
    st.caption("Trust your gut. There are no right or wrong answers here.")

    answers = collect_answers(questions)
    total_answered = len(answers)
    st.progress(total_answered / len(questions))
    st.write(f"Answered {total_answered} of {len(questions)} questions.")

    all_answered = total_answered == len(questions)
    if all_answered:
        if st.button("Show my cinematic alter ego", type="primary"):
            try:
                st.session_state.results = generate_results(questions, answers)
                st.session_state.submitted = True
            except Exception as exc:
                st.error(
                    "We could not connect to the database or embedding service. "
                    "Please try again."
                )
                st.exception(exc)
    else:
        st.info("Answer every question to reveal your match.")

    if st.session_state.submitted and st.session_state.results:
        render_results(st.session_state.results)


def render_results(results: Dict[str, object]) -> None:
    st.divider()
    st.header("Your Nolan counterpart")

    matches: List[Tuple[str, float]] = results.get("matches", [])
    profile = results.get("profile")

    if not matches:
        st.warning("We could not find a close enough match in the graph.")
        return

    primary_name, primary_score = matches[0]
    st.subheader(f"{primary_name} — similarity {primary_score:.2f}")

    image_path = find_character_image(primary_name)
    cols = st.columns([1, 2])
    with cols[0]:
        if image_path:
            st.image(image_path, caption=primary_name)
        else:
            st.write("No promo image available for this character.")
    with cols[1]:
        if profile:
            st.write(f"**Film:** {profile.get('movie', 'Unknown')}")
            render_profile_section("Defining events", profile.get("narrative"))
            render_profile_section("Psychological notes", profile.get("psychology"))
            render_profile_section("Notable lines", profile.get("dialogue"))
        else:
            st.info(
                "Could not load additional details for this character from Neo4j."
            )

    if len(matches) > 1:
        st.write("### Other close matches")
        for name, score in matches[1:]:
            st.write(f"- {name} ({score:.2f})")


def render_profile_section(title: str, entries: Optional[List[str]]) -> None:
    valid_entries = [entry for entry in entries or [] if entry]
    if not valid_entries:
        return
    st.write(f"**{title}:**")
    for entry in valid_entries:
        st.write(f"• {entry}")


def main() -> None:
    initialize_state()
    if not st.session_state.started:
        render_landing_page()
    else:
        render_quiz_body()


if __name__ == "__main__":
    main()
