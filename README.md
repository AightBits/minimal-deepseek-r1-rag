# Minimal DeepSeek-R1 RAG

A basic Retrieval-Augmented Generation (RAG) implementation using DeepSeek-R1 and DuckDuckGo. The script generates search queries, retrieves relevant web content, and incorporates it into responses.

## Dependencies
- Python 3.8+
- `requests` and `duckduckgo-search` (install with `pip install -r requirements.txt`)
- A running DeepSeek-R1 instance with an OpenAI-compatible API

## Usage
Run the script:

```bash
python r1_rag.py
```

## Configuration
Set the DeepSeek-R1 API endpoint and authentication in `r1_rag.py`.

## File
- `r1_rag.py` – Implements query generation, retrieval, and response synthesis.

## Limitations
- Search results depend on DuckDuckGo’s index.
- Model responses are constrained by retrieved content and API parameters.

## License
Apache 2.0 License.
