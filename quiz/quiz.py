import json
import sys
from typing import List
from quiz.graph import model, calculate_cosine_similarity


def load_questions():
    with open("data/questions.json", "r", encoding="utf-8") as f:
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


def run_quiz(questions):
    user_answers = {}
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
        user_answers[q.get("text", "")] = chosen.get("text", "")
    return {
        "choices": choices_made,
        "user_answers": user_answers,
    }


def embed_user_input(user_answers: dict) -> List[float]:
    combined_text = " ".join(user_answers.values())
    sentences = [combined_text]
    embedding = model.encode(sentences, batch_size=1)['dense_vecs']
    return embedding[0].tolist()


def main():
    questions = load_questions()
    if not questions:
        print("No questions found. Check your questions.json.")
        sys.exit(1)

    result = run_quiz(questions)

    print("\n--- Quiz finished ---")
    print("Choices (question_id, index):", result["choices"])
    print("User answers:")
    for k, v in result["user_answers"].items():
        print(f"  {k}: {v}")

    embedded_answers = embed_user_input(result["user_answers"])
    matches = calculate_cosine_similarity(3, embedded_answers)
    if not matches:
        print("\nNot enough trait data to pick a character match.")
        return

    print("\nYour top Nolan character matches:")
    for idx, (name, score) in enumerate(matches, start=1):
        print(f"  {idx}. {name} — similarity {score:.2f}")


if __name__ == "__main__":
    main()
