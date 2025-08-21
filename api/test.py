#!/usr/bin/env python3
"""
Test script to debug the RAG API responses.
Run this while the Flask app is running to see what's being returned.
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    return True

def test_search(query):
    """Test the search endpoint with a query."""
    print(f"🔍 Testing search: '{query}'")
    try:
        payload = {"query": query}
        response = requests.post(f"{API_URL}/api/search", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📊 Response structure:")
            print(f"  Query: {data.get('query', 'N/A')}")
            print(f"  Answer: {data.get('answer', 'N/A')}")
            print(f"  Sources: {data.get('sources', [])}")
            print(f"  Professors found: {len(data.get('professors', []))}")
            print(f"  Total found: {data.get('total_found', 0)}")
            
            # Show first professor details
            professors = data.get('professors', [])
            if professors:
                print("\n👨‍🏫 Top professor:")
                prof = professors[0]
                print(f"  Name: {prof.get('name', 'N/A')}")
                print(f"  Subject: {prof.get('subject', 'N/A')}")
                print(f"  Rating: {prof.get('rating', 'N/A')}")
                print(f"  Final Score: {prof.get('final_score', 'N/A')}")
                print(f"  Preview: {prof.get('chunk_preview', 'N/A')[:100]}...")
            
            print(f"\n📋 Full JSON response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error response: {response.text}")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False
    return True

def test_legacy_endpoint(query):
    """Test the legacy /api/process endpoint."""
    print(f"🔄 Testing legacy endpoint: '{query}'")
    try:
        payload = {"text": query}  # Legacy format
        response = requests.post(f"{API_URL}/api/process", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Legacy response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error response: {response.text}")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Legacy test failed: {e}")

if __name__ == "__main__":
    print("🧪 RAG API Debug Test")
    print("=" * 60)
    
    # Test health first
    if not test_health():
        print("❌ API is not responding. Make sure Flask app is running.")
        exit(1)
    
    # Test various queries
    test_queries = [
        "best professor for calculus",
        "organic chemistry teachers",
        "clear lectures math",
        "computer science programming",
        "psychology introduction"
    ]
    
    for query in test_queries:
        test_search(query)
    
    # Test legacy endpoint
    test_legacy_endpoint("best calculus professor")
    
    print("✅ Debug tests completed!")