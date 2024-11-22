from collections import defaultdict
import re
from typing import List, Dict, Set

def preprocess(text: str) -> Set[str]:
    """Preprocess text by converting to lowercase and extracting unique words."""
    # Remove punctuation and convert to lowercase
    words = re.findall(r'\w+', text.lower())
    return set(words)

def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets of words."""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

def find_similar_documents(data: List[str], threshold: float = 0.2) -> Dict[str, List[str]]:
    """Find similar documents based on Jaccard similarity."""
    # Preprocess documents
    processed_docs = {doc: preprocess(doc) for doc in data}
    
    # Find similar documents
    similar_items = defaultdict(list)
    
    for i, (query, query_words) in enumerate(processed_docs.items()):
        for other_doc, other_words in list(processed_docs.items())[i+1:]:
            if query != other_doc:
                sim = jaccard_similarity(query_words, other_words)
                print(f"Similarity between '{query}' and '{other_doc}': {sim}")  # Diagnostic print
                
                if sim >= threshold:
                    similar_items[query].append(other_doc)
                    similar_items[other_doc].append(query)
    
    return similar_items

# Example dataset
data = [
    "The quick brown fox jumps over the lazy dog.",
    "A fast, dark-colored fox leaps over a sleepy canine.",
    "The dog barked at the fox running away.",
    "An apple a day keeps the doctor away.",
    "Eating fruits and vegetables is essential for good health.",
    "The lazy dog slept all day in the sun.",
    "A quick brown fox is better than a slow white rabbit.",
    "Healthy eating habits can improve overall well-being.",
    "The fox and the hound became unlikely friends.",
    "Dogs are known for their loyalty and companionship."
]

# Find similar items
similar_items = find_similar_documents(data, threshold=0.2)

# Display the similar items
print("\nSimilar items:")
for query, items in similar_items.items():
    if items:  # Only print if there are similar items
        print(f"\tQuery: {query}")
        print(f"\tItems: {items}")