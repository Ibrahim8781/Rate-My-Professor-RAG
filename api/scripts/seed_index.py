#!/usr/bin/env python3
"""
Seed the local index with professor embeddings.
Run this script after updating professors.json to rebuild the search index.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from embedding_utils import create_embeddings

# File paths
DATA_FILE = Path("data/professors.json")
OUTPUT_FILE = Path("data/local_index.json")

def create_professor_chunks(professor):
    """
    Create searchable text chunks for a professor.
    Each chunk contains different aspects of the professor's information.
    """
    chunks = []
    prof_id = professor["id"]
    
    # Chunk 1: Basic info + bio
    basic_info = f"{professor.get('name', '')} teaches {professor.get('subject', '')} in {professor.get('department', '')}. "
    basic_info += f"Rating: {professor.get('avg_rating', 0)}/5 from {professor.get('num_reviews', 0)} reviews. "
    basic_info += professor.get('bio', '')
    
    if basic_info.strip():
        chunks.append(("basic", basic_info.strip()))
    
    # Chunk 2: Tags and teaching style
    if professor.get('tags'):
        tags_text = f"{professor.get('name', '')} is known for: {', '.join(professor.get('tags', []))}."
        chunks.append(("tags", tags_text))
    
    # Chunk 3: Reviews (combine multiple reviews into meaningful chunks)
    reviews = professor.get('reviews', [])
    if reviews:
        # Combine all review text
        review_texts = [review['text'] for review in reviews if review.get('text')]
        if review_texts:
            combined_reviews = f"Student reviews for {professor.get('name', '')}: " + " ".join(review_texts)
            chunks.append(("reviews", combined_reviews))
    
    return chunks

def main():
    """Main function to create and save the search index."""
    
    # Check if professors data exists
    if not DATA_FILE.exists():
        print(f"❌ Error: {DATA_FILE} not found!")
        print("Please create the professors.json file first.")
        return False
    
    # Load professor data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            professors = json.load(f)
        print(f"📚 Loaded {len(professors)} professors from {DATA_FILE}")
    except Exception as e:
        print(f"❌ Error loading professor data: {e}")
        return False
    
    # Create index entries
    index_entries = []
    total_chunks = 0
    
    print("🔄 Creating embeddings...")
    
    for i, professor in enumerate(professors):
        prof_name = professor.get('name', f'Professor {i+1}')
        print(f"  Processing {prof_name}...")
        
        # Create chunks for this professor
        chunks = create_professor_chunks(professor)
        
        for chunk_type, chunk_text in chunks:
            if not chunk_text.strip():
                continue
                
            try:
                # Create embedding
                embedding = create_embeddings(chunk_text)
                
                # Create index entry
                entry = {
                    "id": f"{professor['id']}_chunk_{chunk_type}_{total_chunks}",
                    "vector": embedding,
                    "metadata": {
                        "professor_id": professor["id"],
                        "name": professor.get("name", ""),
                        "subject": professor.get("subject", ""),
                        "department": professor.get("department", ""),
                        "avg_rating": professor.get("avg_rating", 0),
                        "num_reviews": professor.get("num_reviews", 0),
                        "tags": professor.get("tags", []),
                        "chunk_text": chunk_text,
                        "chunk_type": chunk_type
                    }
                }
                
                index_entries.append(entry)
                total_chunks += 1
                
            except Exception as e:
                print(f"    ⚠️  Warning: Failed to create embedding for {prof_name} ({chunk_type}): {e}")
                continue
    
    # Save index
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(index_entries, f, indent=2)
        
        print(f"✅ Successfully created index with {len(index_entries)} entries")
        print(f"📁 Saved to: {OUTPUT_FILE}")
        print(f"📊 Average {total_chunks/len(professors):.1f} chunks per professor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving index: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RAG Professor Review - Index Builder")
    print("=" * 50)
    
    success = main()
    
    if success:
        print("\n🎉 Index creation completed successfully!")
        print("You can now run the Flask app with: python app.py")
    else:
        print("\n💥 Index creation failed!")
        sys.exit(1)