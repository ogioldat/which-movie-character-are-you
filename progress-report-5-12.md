# Progress Report – 5.12

- Tomasz Ogiołda
- Paulina Pojda

## Highlights from Recent Work

### Quiz Authoring & CLI Tooling

- A full narrative-driven item bank (`questions.json`) was added, providing multi-answer questions with categorical and numeric trait signals that align with the modeling documents.
- `quiz.py` offers a terminal flow that renders each question, records choices, aggregates numeric traits via means and categorical traits via priority-aware tie-breaking, and surfaces the resulting feature vector ready for downstream similarity matching.

### Knowledge Graph Assets

- `data/characters.json` now curates detailed Nolan character profiles, combining quantitative trait weights with narrative, dialogue, and psychological notes suitable for both graph construction and UX copy.
- `quiz/graph.py` plus the generated `character_graph.html`/`graph.html` outputs bootstrap a NetworkX-based view of the character–trait space, establishing the foundation for interactive inspection and future embedding experiments.

## Suggested Next Steps

1. **Connect quiz output to embeddings.** Use the aggregated quiz vector to perform cosine similarity lookups against the golden embeddings.
2. **Enrich the graph builder.** Finish wiring weighted edges between characters and traits in `quiz/graph.py` and regenerate the HTML exports so the visualization reflects the current dataset instead of isolated nodes.
3. **Productize the experience.** Wrap `quiz.py` in a simple web or CLI interface that can persist the resulting vectors, re-run recommendations, and surface the generated explanations from the narrative descriptors in the dataset.
