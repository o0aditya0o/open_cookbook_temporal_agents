import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from tqdm import tqdm

# Install and import Google Generative AI
try:
    import google.generativeai as genai
except ImportError:
    print("Installing google-generativeai...")
    import subprocess
    subprocess.check_call(["pip", "install", "google-generativeai"])
    import google.generativeai as genai

class GeminiEmbeddings:
    """Custom embeddings class to work with Gemini API"""
    def __init__(self, api_key: str = None, model: str = "models/embedding-001"):
        if api_key:
            genai.configure(api_key=api_key)
        elif os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        else:
            raise ValueError("Please provide GOOGLE_API_KEY environment variable or pass api_key parameter")
        
        self.model = model
        self.embedding_model = genai.GenerativeModel(model)
    
    def embed_query(self, text: str) -> list[float]:
        """Generate embeddings for a text query"""
        try:
            result = self.embedding_model.embed_content(text)
            return result.embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return a default embedding vector (you might want to handle this differently)
            return [0.0] * 768  # Default dimension

class SimpleSemanticChunker:
    """Simplified semantic chunker that works with Gemini embeddings"""
    def __init__(self, embedding_model, threshold: float = 0.7, min_sentences: int = 3):
        self.embedding_model = embedding_model
        self.threshold = threshold
        self.min_sentences = min_sentences
    
    def chunk(self, text: str) -> list:
        """Simple chunking based on sentence boundaries and length"""
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            current_length += len(sentence)
            
            # Create chunk if we have enough sentences or reach a natural break
            if (len(current_chunk) >= self.min_sentences and 
                (current_length > 500 or i == len(sentences) - 1)):
                
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "start_index": len(' '.join(sentences[:i-len(current_chunk)+1])),
                        "end_index": len(' '.join(sentences[:i+1])),
                        "sentence_count": len(current_chunk)
                    }
                })
                
                current_chunk = []
                current_length = 0
        
        # Handle any remaining text
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "start_index": len(' '.join(sentences[:-len(current_chunk)])),
                    "end_index": len(' '.join(sentences)),
                    "sentence_count": len(current_chunk)
                }
            })
        
        return chunks

class GeminiChunker:
    def __init__(self, api_key: str = None, model: str = "models/embedding-001"):
        self.api_key = api_key
        self.model = model
    
    def find_quarter(self, text: str) -> str | None:
        search_results = re.findall(r"[Q]\d\s\d{4}", text)

        if search_results:
            quarter = str(search_results[0])
            return quarter
        
        return None
    
    def generate_transcripts_and_chunks(
        self,
        dataset: Any,
        company: list[str] | None = None,
        text_key: str = "transcript",
        company_key: str = "company",
        date_key: str = "date",
        threshold_value: float = 0.7,
        min_sentences: int = 3,
        num_workers: int = 50,
    ) -> list:
        # Import Transcript class here to avoid circular imports
        from datetime import datetime
        import uuid
        from pydantic import BaseModel, Field
        
        class Chunk(BaseModel):
            """Chunk class that's compatible with Pydantic"""
            text: str
            metadata: dict[str, Any]
        
        class Transcript(BaseModel):
            id: uuid.UUID = Field(default_factory=uuid.uuid4)
            text: str
            company: str
            date: datetime
            quarter: str | None = None
            chunks: list[Chunk] | None = None
        
        transcripts = [
            Transcript(
                text=d[text_key],
                company=d[company_key],
                date=d[date_key],
                quarter=self.find_quarter(d[text_key]),
            )
            for d in dataset
        ]

        if company:
            transcripts = [t for t in transcripts if t.company in company]

        def _process(t) -> Transcript:
            if not hasattr(_process, "chunker"):
                embed_model = GeminiEmbeddings(api_key=self.api_key, model=self.model)
                _process.chunker = SimpleSemanticChunker(
                    embedding_model=embed_model,
                    threshold=threshold_value,
                    min_sentences=max(min_sentences, 1),
                )
            semantic_chunks = _process.chunker.chunk(t.text)
            t.chunks = [
                Chunk(
                    text=c["text"],
                    metadata=c["metadata"]
                )
                for c in semantic_chunks
            ]

            return t
        
        with ThreadPoolExecutor(max_workers=num_workers) as pool:
            futures = [pool.submit(_process, t) for t in transcripts]
            transcripts = [
                f.result()
                for f in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc="Generating Semantic Chunks with Gemini"
                )
            ]

        return transcripts

# Example usage:
# chunker = GeminiChunker(api_key="your-gemini-api-key")
# transcripts = chunker.generate_transcripts_and_chunks(raw_data)
