### Phase A: Modeling the Domain (The Characters)

To create a meaningful embedding space, you need a diverse set of "Target Nodes" (Characters) that occupy different areas of Nolan’s thematic spectrum.

**Option Set 1: The "Obsessive Visionaries"**

* **Robert Angier (The Prestige):** Defined by sacrifice, showmanship, and fatal obsession.
* **Dom Cobb (Inception):** Defined by guilt, distinct reality warping, and motivation by family.
* **J. Robert Oppenheimer (Oppenheimer):** Defined by genius, moral ambiguity, and the weight of consequences.

**Option Set 2: The "Moral Anchors" vs. "Agents of Entropy"**

* **Bruce Wayne / Batman (Dark Knight Trilogy):** Order, rules, enduring pain for the greater good.
* **The Joker (The Dark Knight):** Pure chaos, absence of rules, testing human nature.
* **Cooper (Interstellar):** Exploration, love as a quantifiable force, distinct "explorer" archetype.

**Option Set 3: The "Time Warpers"**

* **The Protagonist (Tenet):** Professionalism, operating in reverse entropy, suppression of ego.
* **Leonard Shelby (Memento):** Unreliable narrator, living in the immediate present, constructed reality.

#### The Attributes (Features)

To model the domain, you must assign attributes (relations) to these characters. In a graph setting, these would be edge connections.

| Character | Dominant Trait | Relationship to Time | Moral Alignment | Motivation |
| :--- | :--- | :--- | :--- | :--- |
| **Cobb** | Guilt | Dream Time (Slowed) | Chaotic Good | Redemption |
| **Joker** | Chaos | Irrelevant | Chaotic Evil | Disruption |
| **Cooper** | Love | Relativity (Dilated) | Neutral Good | Survival |
| **Leonard**| Confusion | Fragmented | True Neutral | Revenge |
| **Batman** | Discipline | Linear | Lawful Good | Justice |

---

### Phase B: Designing the Questionnaire

Your questions must extract user preferences that map to the *attributes* of the domain, not the characters directly. This allows the embedding algorithm to infer the connection.

**Sample Questions (and what they measure):**

1. **The "Time" Vector:**
    * *Question:* "If you could perceive time differently, how would you choose to experience it?"
    * *Options:* A flat circle (Interstellar/Tenet), A puzzle to be solved (Memento), A resource to be managed (Dunkirk/Inception).

2. **The "Sacrifice" Vector:**
    * *Question:* "To achieve your life's greatest work, what are you willing to lose?"
    * *Options:* My physical self (Prestige), My reputation (Dark Knight), My connection to family (Interstellar).

3. **The "Reality" Vector:**
    * *Question:* "How do you define truth?"
    * *Options:* It is objective and factual (Oppenheimer), It is whatever I choose to remember (Memento), It is malleable (Inception).

---

### Phase C: Embedding Strategy & Algorithms

This is the technical core of your assignment. Since you need to "learn embeddings," you generally have two strong approaches:

#### Approach 1: Knowledge Graph Embeddings

You build a **Heterogeneous Graph**.

* **Nodes:** Users, Characters, Traits (e.g., "Chaos", "Science", "Revenge").
* **Edges:**
  * Character $\rightarrow$ *Has_Trait* $\rightarrow$ Trait
  * User $\rightarrow$ *Selected_Answer* $\rightarrow$ Trait

**Algorithm:** Use **node2vec** or **Metapath2vec**.

1. Perform random walks on the graph to generate sequences of nodes.
2. Feed these sequences into a Skip-Gram model (like Word2Vec).
3. This learns a vector representation for every node. Characters with similar traits will be close in vector space. The User will be pulled toward the traits they selected.

#### Approach 2: Personality Axes (the “embedding space” – 8 dimensions Nolan loves)

1. Moral Compass: Lawful → Chaotic
1. Motivation: Love/Family/Hope → Obsession/Revenge/Power
1. Relationship with Time: Accepts linear time → Manipulates or trapped by time
1. Self-Sacrifice: High (would die for others) → Low (everything for personal goal)
1. Guilt Level: Crippling guilt → Zero remorse
1. View of Humanity: Fundamentally good, worth saving → One bad day from madness
1. Intellect vs Emotion: Cold logic / genius → Driven by emotion
1. Willingness to Break Reality: Would literally bend physics → Stays grounded

---

### Phase D: Discovery (Finding the Match)

Once you have trained the model, the User and the Characters are vectors in the same $d$-dimensional space.

To find the match, you simply calculate the **Cosine Similarity** between the User vector ($U$) and every Character vector ($C$):

$$Similarity(U, C) = \frac{U \cdot C}{\|U\| \|C\|}$$

The Character node with the highest similarity score is the result.

### Summary of the Workflow

1. **Define 5-8 Characters** (Target Nodes).
2. **Define 10-15 Traits** (Concept Nodes).
3. **Link Characters to Traits** (e.g., Batman connects to "Order" and "Justice").
4. **User answers questions**, creating links between **User Node** and **Trait Nodes**.
5. **Run Node2Vec** on the total graph.
6. **Compute Cosine Similarity** to find the nearest Character node to the User node.
