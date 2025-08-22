#!/usr/bin/env python3
"""
Improved seed script - creates ONE embedding per professor to avoid duplicates.
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

def create_professor_text(professor):
    """
    Create a single, comprehensive text representation of a professor.
    This avoids duplicate embeddings and improves search accuracy.
    """
    # Basic info
    name = professor.get('name', 'Unknown')
    subject = professor.get('subject', 'Unknown Subject')
    department = professor.get('department', 'Unknown Department')
    rating = professor.get('avg_rating', 0)
    num_reviews = professor.get('num_reviews', 0)
    
    # Start with core info
    text_parts = [
        f"Professor {name} teaches {subject} in the {department} department.",
        f"Rating: {rating} out of 5 stars from {num_reviews} reviews."
    ]
    
    # Add bio if available
    bio = professor.get('bio', '').strip()
    if bio:
        text_parts.append(bio)
    
    # Add tags (teaching style info)
    tags = professor.get('tags', [])
    if tags:
        text_parts.append(f"Known for: {', '.join(tags)}.")
    
    # Add review excerpts (combine them into one block)
    reviews = professor.get('reviews', [])
    if reviews:
        review_texts = []
        for review in reviews[:3]:  # Limit to first 3 reviews
            text = review.get('text', '').strip()
            if text:
                review_texts.append(text)
        
        if review_texts:
            text_parts.append(f"Student feedback: {' '.join(review_texts)}")
    
    return ' '.join(text_parts)

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
    
    # Create index entries (ONE per professor)
    index_entries = []
    
    print("🔄 Creating embeddings...")
    
    for i, professor in enumerate(professors):
        prof_name = professor.get('name', f'Professor {i+1}')
        prof_id = professor.get('id', f'prof_{i}')
        
        print(f"  Processing {prof_name}...")
        
        try:
            # Create comprehensive text for this professor
            professor_text = create_professor_text(professor)
            
            # Create single embedding
            embedding = create_embeddings(professor_text)
            
            # Create index entry
            entry = {
                "id": prof_id,
                "vector": embedding,
                "metadata": {
                    "professor_id": prof_id,
                    "name": professor.get("name", "Unknown"),
                    "subject": professor.get("subject", "Unknown Subject"),
                    "department": professor.get("department", "Unknown Department"),
                    "avg_rating": professor.get("avg_rating", 0),
                    "num_reviews": professor.get("num_reviews", 0),
                    "tags": professor.get("tags", []),
                    "bio": professor.get("bio", ""),
                    "full_text": professor_text,  # Store for debugging
                    "profile_url": professor.get("profile_url", "")
                }
            }
            
            index_entries.append(entry)
            
        except Exception as e:
            print(f"    ⚠️  Warning: Failed to create embedding for {prof_name}: {e}")
            continue
    
    # Save index
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(index_entries, f, indent=2)
        
        print(f"✅ Successfully created index with {len(index_entries)} professors")
        print(f"📁 Saved to: {OUTPUT_FILE}")
        print(f"📊 One embedding per professor (no duplicates)")
        
        # Show some stats
        subjects = {}
        for entry in index_entries:
            subject = entry['metadata']['subject']
            subjects[subject] = subjects.get(subject, 0) + 1
        
        print(f"📋 Subjects covered: {len(subjects)}")
        for subject, count in sorted(subjects.items()):
            print(f"   - {subject}: {count} professors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving index: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RAG Professor Review - Improved Index Builder")
    print("=" * 50)
    
    success = main()
    
    if success:
        print("\n🎉 Index creation completed successfully!")
        print("You can now run the Flask app with: python app.py")
    else:
        print("\n💥 Index creation failed!")
        sys.exit(1)