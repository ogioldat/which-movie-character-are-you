class CharacterEmbedding:
    def __init__(self, name, movie, narrative, psychology, dialogue):
        self.name = name
        self.movie = movie
        self.narrative = narrative
        self.psychology = psychology
        self.dialogue = dialogue

    def to_text(self) -> str:
        return f"""
            Character: {self.name}
            Movie: {self.movie}
            
            Narrative:
            {'. '.join(self.narrative)}
            
            Psychology:
            {'. '.join(self.psychology)}
            
            Dialogue:
            {'. '.join(self.dialogue)}
        """.strip()

    def calculate_embedding(self, model, batch_size=12):
        sentences = [self.to_text()]
        embedding = model.encode(sentences, batch_size=batch_size)['dense_vecs']
        return embedding[0].tolist()
