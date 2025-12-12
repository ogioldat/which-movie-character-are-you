import dataclasses
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from quiz.graph import Character, load_characters

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def present_question(q, qnum=None):
    header = f"Question {qnum}: " if qnum is not None else "Question: "
    print(f"\n{header}{q['text']}")
    for i, a in enumerate(q.get("answers", []), start=1):
        print(f"  {i}. {a['text']}")
        if a.get("photo"):
            print(f"     (photo: {a['photo']})")


def get_choice(num_options, prompt=None):
    prompt = prompt or f"Choose 1-{num_options}: "
    while True:
        try:
            choice = input(prompt).strip()
            if choice == "":
                print("Please enter a number.")
                continue
            idx = int(choice)
            if 1 <= idx <= num_options:
                return idx - 1
            print(f"Enter a number between 1 and {num_options}.")
        except ValueError:
            print("Invalid input, enter the option number.")


# Aggregation rules for categorical keys (priority used to break ties)
PRIORITY_MAPS = {
    "alignment": {"Good": 3, "Neutral": 2, "Evil": 1},
}

CHARACTER_DATA_PATH = Path("data/characters.json")

# Mapping categorical signals from the quiz to the numeric [-10, 10] space.
CATEGORICAL_TO_NUMERIC = {
    "alignment": {"Good": 10.0, "Neutral": 0.0, "Evil": -10.0},
    "motivation": {"Justice": 10.0, "Ambition": 4.0, "Power": -8.0},
}


def aggregate_properties(props_acc):
    result = {}
    for key, values in props_acc.items():
        # Filter out None
        vals = [v for v in values if v is not None]
        if not vals:
            continue
        # If all numeric -> mean
        if all(isinstance(v, (int, float)) for v in vals):
            result[key] = statistics.mean(vals)
            continue
        # Otherwise treat as categorical (no mixed numeric+categorical per user's note)
        counter = Counter(vals)
        most_common = counter.most_common()
        top_count = most_common[0][1]
        candidates = [val for val, cnt in most_common if cnt == top_count]
        if len(candidates) == 1:
            result[key] = candidates[0]
        else:
            # tie-break by priority map if available
            priority = PRIORITY_MAPS.get(key)
            if priority:
                best = max(candidates, key=lambda x: priority.get(x, 0))
                result[key] = best
            else:
                # fallback: pick the first candidate encountered (stable)
                result[key] = candidates[0]
    return result


def _normalize_numeric_value(value: float) -> float:
    """Map quiz inputs (typically 0-10) onto the -10..10 trait space."""
    if 0 <= value <= 10:
        return (value - 5) * 2
    return float(value)


def normalize_user_traits(aggregated: Dict[str, float]) -> Dict[str, float]:
    normalized = {}
    for key, value in aggregated.items():
        numeric_value = None
        if isinstance(value, (int, float)):
            numeric_value = _normalize_numeric_value(value)
        elif isinstance(value, str):
            mapping = CATEGORICAL_TO_NUMERIC.get(key, {})
            numeric_value = mapping.get(value)
        if numeric_value is not None:
            normalized[key] = numeric_value
    return normalized


def cosine_similarity(user_vector: Dict[str, float], trait_vector: Dict[str, float]) -> float:
    overlap = [k for k in user_vector.keys() if k in trait_vector]
    if not overlap:
        return 0.0
    dot = sum(user_vector[k] * trait_vector[k] for k in overlap)
    user_norm = math.sqrt(sum(user_vector[k] ** 2 for k in overlap))
    trait_norm = math.sqrt(sum(trait_vector[k] ** 2 for k in overlap))
    if user_norm == 0 or trait_norm == 0:
        return 0.0
    return dot / (user_norm * trait_norm)


def rank_characters(
    user_vector: Dict[str, float], characters: Sequence[Character], top_k: int = 3
) -> List[Tuple[Character, float]]:
    if not user_vector:
        return []

    scored = []
    for char in characters:
        traits = dataclasses.asdict(char.traits)
        score = cosine_similarity(user_vector, traits)
        scored.append((char, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


def load_character_profiles(path: Path = CHARACTER_DATA_PATH) -> List[Character]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return load_characters(data)


def run_quiz(questions):
    props_acc = defaultdict(list)
    choices_made = []
    for qi, q in enumerate(questions, start=1):
        present_question(q, qnum=qi)
        answers = q.get("answers", [])
        if not answers:
            print("No answers for this question, skipping.")
            continue
        idx = get_choice(len(answers))
        choices_made.append((q["id"], idx))
        chosen = answers[idx]
        props = chosen.get("properties", {})
        for k, v in props.items():
            props_acc[k].append(v)
    aggregated = aggregate_properties(props_acc)
    return {
        "choices": choices_made,
        "aggregated_properties": aggregated,
    }


def parse_auto_choices(s):
    if not s:
        return None
    parts = s.split(",")
    out = []
    for p in parts:
        p = p.strip()
        if p == "":
            continue
        try:
            n = int(p)
            out.append(n - 1)  # convert to 0-based
        except ValueError:
            print(f"Invalid auto choice '{p}', ignoring.")
    return out


def main():
    questions = load_questions()
    if not questions:
        print("No questions found. Check your questions.json.")
        sys.exit(1)

    result = run_quiz(questions)

    print("\n--- Quiz finished ---")
    print("Choices (question_id, index):", result["choices"])
    print("Aggregated properties:")
    for k, v in result["aggregated_properties"].items():
        print(f"  {k}: {v}")

    characters = load_character_profiles()
    user_vector = normalize_user_traits(result["aggregated_properties"])
    matches = rank_characters(user_vector, characters, top_k=3)
    if not matches:
        print("\nNot enough trait data to pick a character match.")
        return

    print("\nYour top Nolan character matches:")
    for idx, (char, score) in enumerate(matches, start=1):
        print(f"  {idx}. {char.character_name} ({char.movie}) — similarity {score:.2f}")


if __name__ == "__main__":
    main()
