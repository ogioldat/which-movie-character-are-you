# Implementation Plan: “Which Nolan Movie Character Are You?”

Embeddings-based Psycho Quiz (real cosine similarity, not just point counting)

## Phase 1: Domain Modeling & Golden Embeddings (one-time setup)

1. Select 12 final characters (as listed before)  

   Cooper, Leonard Shelby, Dom Cobb, Bruce Wayne/Batman, Robert Angier, Alfred Borden, Neil, J. Robert Oppenheimer, The Joker, Adult Murph, Mal Cobb

2. Create the 8-dimensional trait space (exact axes we already defined):
   - Moral: Lawful (−1) … Chaotic (+1)
   - Motivation: Love/Hope (−1) … Obsession/Power (+1)  
   - Time: Linear (−1) … Manipulates/Trapped (+1)  
   - Self-sacrifice: High (−1) … Low (+1)  
   - Guilt: High (−1) … None (+1)  
   - View of Humanity: Worth saving (−1) … One bad day (+1)  
   - Logic vs Emotion: Logic (−1) … Emotion (+1)  
   - Reality-bending willingness: Grounded (−1) … Would break physics (+1)

3. Hand-craft golden 8-dimensional vectors for each of the 12 characters  
   (done once by you or a Nolan expert; takes ~1-2 hours). Example:

| Character          | Moral | Motiv | Time | Sacri | Guilt | Humanity | Logic | Reality |
|--------------------|-------|-------|------|-------|-------|----------|-------|---------|
| Cooper             | -0.8  | -0.9  | -0.2 | -1.0  | -0.6  | -1.0     | -0.4  | +0.8    |
| The Joker          | +1.0  | +0.8  | +0.6 | +1.0  | +1.0  | +1.0     | +0.7  | +0.3    |
| Dom Cobb           | -0.3  | +0.4  | +0.9 | -0.5  | -0.9  | -0.4     | +0.2  | +1.0    |

4. Save these 12 golden vectors in a JSON or CSV file (gold_embeddings.json)

### Phase 2: Questionnaire → User Vector

15 questions (exactly the ones already written).

Mapping each question → which dimension(s) it loads on (you only need this once):

| Question | Primary dimension(s)                          | Loading strength |
|---------|-----------------------------------------------|------------------|
| 1       | Self-sacrifice, Love/Hope, Reality-bending    | very high        |
| 2       | View of Humanity, Chaos                       | very high        |
| 3       | Time (trapped), Guilt                         | high             |
| ...     | ...                                           | ...              |

Each answer A–E is converted to a score from −1.0 to +1.0  
A = −1.0, B = −0.5, C = 0, D = +0.5, E = +1.0

For each dimension, average the scores of all questions that load on it (weighted if you want extra precision).

→ You now have one 8-dimensional user vector, normalized to unit length.