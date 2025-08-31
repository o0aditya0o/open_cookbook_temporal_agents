# Open Cookbook Temporal Agents

This repository contains a Jupyter notebook for analyzing earnings call transcripts and a custom SQLite database interface.

## Database Interface

The `db_interface.py` file provides a clean SQLite database interface with the following features:

### Functions

- `make_connection(memory=False, refresh=False, db_path="cookbook.db")` - Create SQLite database connection
- `create_tables(conn)` - Create database tables for companies, transcripts, and stock prices
- `insert_company(conn, name, ticker=None, sector=None)` - Add a new company
- `insert_transcript(conn, company_id, date, transcript_text, sentiment_score=None)` - Add a transcript
- `get_companies(conn)` - Retrieve all companies
- `get_transcripts(conn, company_id=None)` - Retrieve transcripts (optionally filtered by company)

### Usage

```python
from db_interface import make_connection, create_tables

# Create database connection (same as in notebook)
sqlite_conn = make_connection(memory=False, refresh=True)

# Create tables
create_tables(sqlite_conn)

# Use the connection for database operations...
```

## Gemini-Based Chunker

The `gemini_chunker.py` file provides a replacement for the OpenAI-based `chonkie` library, using Google's Gemini API instead.

### Features

- **GeminiEmbeddings**: Custom embeddings class for Gemini API
- **SimpleSemanticChunker**: Simplified chunking based on sentence boundaries
- **GeminiChunker**: Main chunker class with the same interface as the original

### Setup

1. **Get a Gemini API key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Set your API key**:
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key-here"
   ```
   Or pass it directly:
   ```python
   chunker = GeminiChunker(api_key="your-key-here")
   ```

### Usage

```python
from gemini_chunker import GeminiChunker

# Initialize chunker
chunker = GeminiChunker()

# Process your dataset
transcripts = chunker.generate_transcripts_and_chunks(
    dataset=raw_data,
    min_sentences=3,
    num_workers=10
)
```

### Example

Run the example script to test:
```bash
python3 example_gemini_usage.py
```

## Notebook

The `playbook.ipynb` notebook demonstrates:
- Loading earnings call transcript datasets from Hugging Face
- Analyzing company and transcript data
- Using the custom database interface to store and query data

## Requirements

- Python 3.10+
- Required packages: `datasets`, `sqlite3` (built-in), `google-generativeai`
- Optional packages: `chonkie`, `datetime`, `ipykernel`, `jinja2`, `matplotlib`, `networkx`, `numpy`, `openai`

## Migration from OpenAI to Gemini

If you're switching from the original OpenAI-based implementation:

1. **Replace imports**:
   ```python
   # Old (OpenAI)
   from chonkie import OpenAIEmbeddings, SemanticChunker
   
   # New (Gemini)
   from gemini_chunker import GeminiChunker
   ```

2. **Update chunker initialization**:
   ```python
   # Old
   chunker = Chunker()
   
   # New
   chunker = GeminiChunker()
   ```

3. **Set Gemini API key** instead of OpenAI key

## Note

The original PyPI `db_interface` package had dependency issues and was designed for MySQL. This local implementation provides a clean SQLite interface that matches the expected API.

The Gemini implementation provides a cost-effective alternative to OpenAI for text chunking and analysis.
