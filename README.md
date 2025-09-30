# Hype Coach

Hype Coach generates personalized pep talks by finding your most relevant achievements and connecting them to whatever challenge you're facing. It's like having a motivational coach who actually knows your track record.

## Quick Start

```bash
pip install -r requirements.txt
```

## Prerequisites

Start Ollama server:

```bash
ollama serve
ollama pull llama3.1:8b
```

## Usage

```bash
python -m src.cli --scenario "your challenge here" --energy [1-3]
```

Energy levels:
- **1**: Calm, reassuring encouragement
- **2**: Confident, upbeat motivation  
- **3**: High-energy, enthusiastic hype

## Design Notes

**Architecture**: Plan-act pattern with tool integration. The agent first decides whether to retrieve achievements, then generates personalized motivation.

**Retrieval Tool**: TF-IDF selector finds relevant achievements based on scenario keywords. Confidence scoring reflects retrieval quality using cosine similarity.

**Evidence Grounding**: All motivational content references specific achievements with inline citations. Only generic advice without applicable achievements

**TF-IDF vs Embeddings**: Chose TF-IDF for simplicity and interpretability. Embeddings would be a natural day-two enhancement for better semantic matching.

## Development

Run tests:
```bash
python -m pytest -q
```

Environment variables:
```bash
LLM_PLAN_MODE=live    # or 'stub' for testing
LLM_FINAL_MODE=live   # or 'stub' for testing
```

## Project Structure

```
src/
├── agent.py      # Main agent with plan-act flow
├── tools.py      # Achievement retrieval with TF-IDF
├── selectors.py  # TF-IDF implementation
├── models.py     # Pydantic data models
├── prompts.py    # LLM instructions
└── cli.py        # Command-line interface

data/
└── achievements.json  # Personal achievement database

tests/
├── test_agent.py      # Agent behavior tests
├── test_tools.py      # Retrieval tool tests
├── test_selectors.py  # TF-IDF selector tests
└── test_end_to_end.py # Integration smoke test
