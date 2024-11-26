import re
import random

class DocumentSimilarityLSH:
    def __init__(self, num_hash_functions: int = 100, bands: int = 20):
        if bands <= 0 or num_hash_functions <= 0:
            raise ValueError("Number of hash functions and bands must be positive")
        if num_hash_functions % bands != 0:
            raise ValueError("Number of hash functions must be divisible by number of bands")
            
        self.num_hash_functions = num_hash_functions
        self.bands = bands
        self.rows_per_band = num_hash_functions // bands
        self.documents = {}
        self.hash_tables = [{} for _ in range(bands)]
        
        # Generate hash coefficients
        random.seed(42)  # For reproducibility
        self.hash_coeff = [
            (random.randint(1, 2**31-1), random.randint(1, 2**31-1)) 
            for _ in range(num_hash_functions)
        ]
        
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text to handle common variations"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
            
        # Convert to lowercase
        text = text.lower()
        # Replace newlines and tabs with spaces
        text = re.sub(r'[\n\t]', ' ', text)
        # Remove punctuation except apostrophes
        text = re.sub(r'[^\w\s\']', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _create_shingles(self, text: str, k: int = 3) -> set:
        """Create character-based shingles"""
        text = self._preprocess_text(text)
        if len(text) < k:
            return {text}  # Return full text as single shingle for very short texts
        
        # Create character-level shingles
        return {text[i:i+k] for i in range(len(text) - k + 1)}
    
    def _hash_function(self, value: str, a: int, b: int) -> int:
        """MurmurHash-inspired string hashing function with overflow protection"""
        prime = 16777619
        hash_val = 2166136261
        
        for char in value:
            hash_val = hash_val ^ ord(char)
            hash_val = ((hash_val * prime) & 0xFFFFFFFF)
            
        # Use modular arithmetic to prevent overflow
        result = (((a & 0xFFFFFFFF) * (hash_val & 0xFFFFFFFF)) & 0xFFFFFFFF)
        result = ((result + (b & 0xFFFFFFFF)) & 0xFFFFFFFF)
        return result
    
    def _minhash_signature(self, shingles: set) -> list:
        """Generate MinHash signature for a set of shingles"""
        if not shingles:
            raise ValueError("Empty shingle set")
            
        signature = [float('inf')] * self.num_hash_functions
        
        for shingle in shingles:
            for i in range(self.num_hash_functions):
                a, b = self.hash_coeff[i]
                hash_value = self._hash_function(shingle, a, b)
                signature[i] = min(signature[i], hash_value)
                
        return signature
    
    def add_document(self, doc_id: str, text: str):
        """Add a document to the LSH index"""
        if not text.strip():
            raise ValueError("Empty document text")
        if doc_id in self.documents:
            raise ValueError(f"Document ID '{doc_id}' already exists")
            
        shingles = self._create_shingles(text)
        signature = self._minhash_signature(shingles)
        self.documents[doc_id] = signature
        
        # Add to LSH bands
        for band in range(self.bands):
            start_idx = band * self.rows_per_band
            end_idx = start_idx + self.rows_per_band
            band_signature = tuple(signature[start_idx:end_idx])
            
            # Use defaultdict-like behavior
            if band_signature not in self.hash_tables[band]:
                self.hash_tables[band][band_signature] = []
            self.hash_tables[band][band_signature].append(doc_id)
            
    def _jaccard_similarity(self, sig1: list, sig2: list) -> float:
        """Calculate Jaccard similarity between two signatures"""
        if len(sig1) != len(sig2):
            raise ValueError("Signature lengths do not match")
        
        # Count matching hash values
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)
    
    def find_similar_documents(self, doc_id: str, threshold: float = 0.3) -> dict:
        """Find similar documents above the given threshold"""
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        if doc_id not in self.documents:
            raise ValueError(f"Document '{doc_id}' not found")
            
        candidate_docs = set()
        query_signature = self.documents[doc_id]
        
        # Collect candidates from all matching bands
        for band in range(self.bands):
            start_idx = band * self.rows_per_band
            end_idx = start_idx + self.rows_per_band
            band_signature = tuple(query_signature[start_idx:end_idx])
            
            candidates = self.hash_tables[band].get(band_signature, [])
            candidate_docs.update(candidates)
            
        candidate_docs.discard(doc_id)
        
        # Calculate actual similarities for candidates
        similarities = {}
        for candidate_id in candidate_docs:
            candidate_signature = self.documents[candidate_id]
            similarity = self._jaccard_similarity(query_signature, candidate_signature)
            if similarity >= threshold:
                similarities[candidate_id] = similarity
                
        return dict(sorted(similarities.items(), key=lambda x: x[1], reverse=True))

def run_plagiarism_check():
    # Original essay
    essay1 = """
    The Impact of Social Media on Modern Society

    Social media has fundamentally transformed how we communicate and interact in the 21st century. 
    These platforms have created unprecedented opportunities for global connectivity, allowing people 
    from different corners of the world to share ideas, experiences, and information instantly.
    """

    # Similar essay
    essay2 = """
    The Effects of Social Media in Today's World

    Social media has fundamentally changed how people communicate and interact in the modern era. 
    These digital platforms have created new ways for worldwide connectivity, enabling individuals 
    from different parts of the globe to exchange ideas, experiences, and information instantaneously.
    """

    # Completely different essay
    essay3 = """
    The Future of Renewable Energy
    
    Renewable energy technologies are rapidly advancing and becoming increasingly important in our 
    fight against climate change. Solar and wind power have seen dramatic improvements in efficiency 
    and cost-effectiveness over the past decade.
    """

    # Initialize LSH system
    lsh = DocumentSimilarityLSH()

    # Add documents
    print("\nAdding documents...")
    lsh.add_document("essay1", essay1)
    lsh.add_document("essay2", essay2)
    lsh.add_document("essay3", essay3)

    # Compare original essay with others
    print("\nChecking similarities with Essay 1...")
    similar_docs = lsh.find_similar_documents("essay1", threshold=0.5)
    
    if similar_docs:
        print("\nSimilar documents found:")
        for doc_id, similarity in similar_docs.items():
            print(f"{doc_id}: {similarity:.2%} similarity")
    else:
        print("\nNo significant similarities found.")

if __name__ == "__main__":
    run_plagiarism_check()