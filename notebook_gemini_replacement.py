# Replace the problematic OpenAI-based chunker with Gemini
# Copy this code into a new cell in your notebook

# First, install the required package
# Run this in a separate cell: %pip install google-generativeai

# Import the new Gemini chunker
from gemini_chunker import GeminiChunker

# Set your Gemini API key (replace with your actual key)
import os
os.environ["GOOGLE_API_KEY"] = "your-gemini-api-key-here"

# Initialize the new chunker
chunker = GeminiChunker()

# Process your data (same interface as before)
transcripts = chunker.generate_transcripts_and_chunks(raw_data)

print(f"Successfully processed {len(transcripts)} transcripts with Gemini!")
