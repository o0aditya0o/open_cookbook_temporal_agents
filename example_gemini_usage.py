#!/usr/bin/env python3
"""
Example usage of the Gemini-based chunker
"""

from gemini_chunker import GeminiChunker

# Set your Gemini API key (use environment variable for security)
import os

# Option 1: Set environment variable
# os.environ["GOOGLE_API_KEY"] = "your-gemini-api-key-here"

# Option 2: Pass directly to the chunker
# api_key = "your-gemini-api-key-here"

def main():
    # Initialize the chunker
    chunker = GeminiChunker()  # Will use GOOGLE_API_KEY environment variable
    # Or: chunker = GeminiChunker(api_key="your-key-here")
    
    # Example dataset (replace with your actual data)
    sample_data = [
        {
            "company": "Apple Inc.",
            "date": "2024-01-15",
            "transcript": "Q1 2024 earnings call transcript. Our revenue increased by 15% year-over-year. We're excited about our new product launches. The market response has been positive."
        },
        {
            "company": "Microsoft Corp.",
            "date": "2024-01-20", 
            "transcript": "Q1 2024 earnings call transcript. Cloud services continue to grow rapidly. We're seeing strong adoption across all segments. Our AI initiatives are progressing well."
        }
    ]
    
    print("Processing transcripts with Gemini chunker...")
    
    try:
        # Generate chunks
        transcripts = chunker.generate_transcripts_and_chunks(
            dataset=sample_data,
            min_sentences=2,
            num_workers=2  # Reduced for demo
        )
        
        print(f"\n✅ Successfully processed {len(transcripts)} transcripts!")
        
        # Display results
        for transcript in transcripts:
            print(f"\nCompany: {transcript.company}")
            print(f"Date: {transcript.date}")
            print(f"Quarter: {transcript.quarter}")
            print(f"Number of chunks: {len(transcript.chunks) if transcript.chunks else 0}")
            
            if transcript.chunks:
                for i, chunk in enumerate(transcript.chunks):
                    print(f"  Chunk {i+1}: {chunk.text[:100]}...")
                    print(f"    Metadata: {chunk.metadata}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set your GOOGLE_API_KEY environment variable")
        print("2. Or passed the api_key parameter to GeminiChunker")
        print("3. Have sufficient Gemini API quota")

if __name__ == "__main__":
    main()
