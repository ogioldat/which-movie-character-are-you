import json
from pathlib import Path
from typing import List
from neo4j import GraphDatabase
from quiz.CharacterEmbedding import CharacterEmbedding
from quiz.graph import model, load_characters_for_embedding, add_characters_embeddings, create_character_embedding_index

URI = "neo4j+ssc://f6e7bfa3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "RUjFALUooPTwVOpGqyOcMzS-wwnV2y8Uq3wR6VdezM8"
CHARACTER_DATA_PATH = Path("data/characters.json")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def load_data(text, json_path):
    with open(json_path, "r", encoding="utf-8") as fh:
        characters = json.load(fh)
    with driver.session() as session:
        session.run(text, characters=characters)
    print(f"Loaded {len(characters)} characters into the database.")


def check_data_loaded():
    with driver.session() as session:
        result = session.run("MATCH (n:Character) RETURN count(n) AS count")
        count = result.single()["count"]
        return count > 0


def embed_characters(characters: List[CharacterEmbedding]) -> dict[str, List[float]]:
    embeddings = {}
    for character in characters:
        vector = character.calculate_embedding(model)
        embeddings[character.name] = vector
    return embeddings


def main():
    query = """
    UNWIND $characters AS c

    // Movies
    MERGE (m:Movie {title: c.movie})

    // Character
    MERGE (ch:Character {name: c.character_name})
    MERGE (ch)-[:APPEARS_IN]->(m)

    // Narrative Events
    FOREACH (event IN c.narrative_description |
      MERGE (e:NarrativeEvent {description: event})
      MERGE (ch)-[:EXPERIENCES]->(e)
    )

    // Dialogue Lines
    FOREACH (line IN c.dialogue_lines |
      MERGE (d:DialogueLine {text: line})
      MERGE (ch)-[:SAYS]->(d)
    )

    // Psychological Statements
    FOREACH (psy IN c.psychological_description |
      MERGE (p:PsychologicalStatement {text: psy})
      MERGE (ch)-[:EXPRESSES]->(p)
    )
    """

    if not check_data_loaded():
        print("Loading character data into the database...")
        load_data(query, CHARACTER_DATA_PATH)
        characters = load_characters_for_embedding()
        embeddings = embed_characters(characters)
        add_characters_embeddings(embeddings)
        create_character_embedding_index()
    else:
        print("Character data already loaded and embedded.")

    driver.close()


if __name__ == "__main__":
    main()
