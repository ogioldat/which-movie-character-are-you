from neo4j import GraphDatabase
from quiz.CharacterEmbedding import CharacterEmbedding
from FlagEmbedding import BGEM3FlagModel

URI = "neo4j+s://f6e7bfa3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "RUjFALUooPTwVOpGqyOcMzS-wwnV2y8Uq3wR6VdezM8"

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

GET_CHARACTERS_QUERY = """MATCH (c:Character)-[:APPEARS_IN]->(m:Movie)
    OPTIONAL MATCH (c)-[:EXPERIENCES]->(n:NarrativeEvent)
    OPTIONAL MATCH (c)-[:EXPRESSES]->(p:PsychologicalStatement)
    OPTIONAL MATCH (c)-[:SAYS]->(d:DialogueLine)
    RETURN
      c.name AS name,
      m.title AS movie,
      collect(DISTINCT n.description) AS narrative,
      collect(DISTINCT p.text) AS psychology,
      collect(DISTINCT d.text) AS dialogue
"""


def load_characters_for_embedding():
    with driver.session() as session:
        result = session.run(GET_CHARACTERS_QUERY)  # type: ignore[arg-type]
        docs = []

        for r in result:
            doc = CharacterEmbedding(
                name=r["name"],
                movie=r["movie"],
                narrative=r["narrative"],
                psychology=r["psychology"],
                dialogue=r["dialogue"],
            )
            docs.append(doc)
    return docs


def add_characters_embeddings(embeddings: dict[str, list[float]]):
    query = """
    UNWIND $embeddings AS item
    MATCH (c:Character {name: item.name})
    SET c.embedding = item.embedding

    """
    items = [{"name": name, "embedding": vector} for name, vector in embeddings.items()]
    with driver.session() as session:
        session.run(query, embeddings=items)  # type: ignore[arg-type]
    print(f"Added embeddings for {len(embeddings)} characters.")


def create_character_embedding_index():
    query = """
        CREATE VECTOR INDEX character_embedding_index
        FOR (c:Character)
        ON (c.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 1024,
            `vector.similarity_function`: 'cosine'
          }
        };
    """
    with driver.session() as session:
        result = session.run(query)  # type: ignore[arg-type]
        print(result)


def calculate_cosine_similarity(num_best: int, user_embedding: list[float]):
    query = """
    CALL db.index.vector.queryNodes("character_embedding_index", $num_best, $user_embedding)
    YIELD node, score
    RETURN node, score;
    """
    best = []
    with driver.session() as session:
        result = session.run(query, num_best=num_best, user_embedding=user_embedding)  # type: ignore[arg-type]
        for record in result:
            best.append((record["node"]["name"], record["score"]))  # access name via node
    return best


