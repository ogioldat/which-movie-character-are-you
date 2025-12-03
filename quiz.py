import json
import statistics
import sys
from collections import Counter, defaultdict

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


if __name__ == "__main__":
    main()
