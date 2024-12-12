import sys
sys.path.insert(0, './local_modules/')

import numpy as np
import re
import os
import json
from typing import List, Set, Dict
from collections import defaultdict

class DocumentSimilarityLSH:
    def __init__(self, num_hash_functions: int = 100, bands: int = 20):
        if bands <= 0 or num_hash_functions <= 0:
            raise ValueError("Number if hash functions and bands must be positive")
        if num_hash_functions % bands != 0:
            raise ValueError("Number of hash functions must be divisible by number of bands")
        
        self.num_hash_functions = num_hash_functions
        self.bands = bands
        self.rows_per_band = num_hash_functions // bands
        self.documents = {}
        self.hash_tables = [defaultdict(list) for _ in range(bands)]
        
        # generate hash coeff (for reproducibility, we set a static seed)
        np.random.seed(42)
        self.hash_coeff = np.random.randint(1, 2**31-1, size=(num_hash_functions, 2))
        
    def _preprocess_text(self, text: str) -> str:
        """
        Une fonction qui prend en entrée un texte volumineux et retourne une version nettoyée de celui-ci, en supprimant les espaces superflus, la ponctuation et les caractères indésirables
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
            
        # convert to lower case -> remove extra whitespaces -> remove ponctuations -> remove extra whitespaces
        text = text.lower()
        text = re.sub(r'[\n\t]', ' ', text)
        text = re.sub(r'[^\w\s\']', ' ', text)
        text = ' '.join(text.split())
        
        return text
    
    def _create_shingles(self, text: str, k: int = 3) -> Set[str]:
        """
        Cette fonction génère des “shingles” (ou n-grammes) à partir d’un texte donné. Un shingle est une sous-chaîne de longueur `k` extraite du texte. Cette fonction prend en entrée une chaîne de caractères `text` et un entier `k` qui définit la taille des shingles
        """
        if k <= 0:
            raise ValueError("Shingle size must be positive")
        
        text = self._preprocess_text(text)
        if len(text) < k:
            return {text}
        
        return {text[i:i+k] for i in range(len(text) - k + 1)}
    
    def _hash_function(self, value: str, a: int, b: int) -> int:
        """
        Cette fonction calcule une valeur de hachage pour une chaîne de caractères donnée en utilisant une méthode de hachage basée sur des coefficients a et b
        source: https://stackoverflow.com/questions/13305290/is-there-a-pure-python-implementation-of-murmurhash
        on utilise un grand nombre premier pour eviter les collision des entrée differentes, deux intrée differentes de doivent pas generer la meme valeur de hashage
        """
        
        prime = 16777619
        hash_val = 2166136261
        
        for char in value:
            hash_val = hash_val ^ ord(char)
            hash_val = ((hash_val * prime) & 0xFFFFFFFF)
        
        # prevent overflow
        result = (((a & 0xFFFFFFFF) * (hash_val & 0xFFFFFFFF)) & 0xFFFFFFFF)
        result = ((result + (b & 0xFFFFFFFF)) & 0xFFFFFFFF)
        return result
    
    def _minhash_signature(self, shingles: Set[str]) -> np.ndarray:
        """
        Cette fonction génère une signature MinHash à partir d’un ensemble de shingles en appelant _hash_function, elle appelle cette fonction plusieurs fois et a chaque fois compare et prends la valeure minimale. La signature MinHash est utilisée pour estimer la similarité entre des ensembles en réduisant leur dimensionnalité (pour une meilleur performance) tout en préservant les propriétés de similarité
        """
        
        if not shingles:
            raise ValueError("empty shingle set")
        
        signature = np.full(self.num_hash_functions, np.inf)
        
        for shingle in shingles:
            for i in range(self.num_hash_functions):
                a, b = self.hash_coeff[i]
                hash_value = self._hash_function(shingle, a, b)
                signature[i] = min(signature[i], hash_value)
        
        return signature
    
    def add_document(self, doc_id: str, text: str):
        """
        Cette fontion permet d'ajouter un document à l'index LSH, elle prends en entrée l'ID et le contenue
        """
        if not text.strip():
            raise ValueError("empty document text")
        if doc_id in self.documents:
            raise ValueError(f'document ID "{doc_id}" already exists')
        
        shingles = self._create_shingles(text)
        signature = self._minhash_signature(shingles)
        self.documents[doc_id] = signature
        
        # add to lsh bands
        for band in range(self.bands):
            start_idx = band * self.rows_per_band
            end_idx = start_idx + self.rows_per_band
            band_signature = tuple(signature[start_idx:end_idx])
            self.hash_tables[band][band_signature].append(doc_id)
            
    def _jaccard_similarity(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """
        Calcule la similarite Jaccard entre deux signatures minhash, cette similarité est celle qui decide a quelle points deux documents sonts similaire
        """
        if len(sig1) != len(sig2):
            raise ValueError("signatures length do not match")
        matches = np.sum(sig1 == sig2)
        # print(f'jaccard sim: {matches / len(sig1)}')
        
        return matches / len(sig1)
    
    import json
    
    def find_similar_documents(self, doc_id: str, threshold: float = 0.1) -> str:
        """
        Recherche les documents similaires. Elle compare la signature MinHash du document spécifié avec celles des autres documents et retourne ceux qui dépassent un seuil de similarité définie.
        Returns a JSON string of similar documents.
        """
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        if doc_id not in self.documents:
            raise ValueError(f'document {doc_id} not found')
            
        candidate_docs = set()
        query_signature = self.documents[doc_id]
        
        for band in range(self.bands):
            start_idx = band * self.rows_per_band
            end_idx = start_idx + self.rows_per_band
            band_signature = tuple(query_signature[start_idx:end_idx])
            candidates = self.hash_tables[band][band_signature]
            candidate_docs.update(candidates)
            
        candidate_docs.discard(doc_id)
        
        similarities = {}
        for candidate_id in candidate_docs:
            candidate_signature = self.documents[candidate_id]
            similarity = self._jaccard_similarity(query_signature, candidate_signature)
            if similarity >= threshold:
                similarities[candidate_id] = similarity
                
        similar_documents = dict(sorted(similarities.items(), key=lambda x: x[1], reverse=True))
        
        return json.dumps(similar_documents)
    

def run_plagiarism_check(main_file_path, documents_dir=None, threshold=0.1):
    
    # maek sure the main file exists
    if not os.path.exists(main_file_path):
        raise FileNotFoundError(f"main file not found: {main_file_path}")
        
    with open(main_file_path, 'r', encoding='utf-8') as f:
        main_text = f.read()
        
    # create an instance of the class
    lsh = DocumentSimilarityLSH()
    
    # add the main file
    lsh.add_document("main", main_text)
    
    # get all the other documents and add them to find which one is a plagiarism
    if documents_dir:
        if not os.path.isdir(documents_dir):
            raise NotADirectoryError(f"Invalid directory: {documents_dir}")
            
        # sort them to avoid any issues
        text_files = sorted([
            f for f in os.listdir(documents_dir) 
            if os.path.isfile(os.path.join(documents_dir, f)) and f.endswith('.txt')
        ])
        
        
        for idx, filename in enumerate(text_files, 1):
            file_path = os.path.join(documents_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    doc_text = f.read()
                    lsh.add_document(f"doc_{idx}", doc_text)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    
    # call the find_similar_documents function
    similar_docs = lsh.find_similar_documents("main", threshold=threshold)
    
    return similar_docs

def main():
    try:
        main_file = 'main.txt'
        documents_dir = './documents'
        
        result_json = run_plagiarism_check(main_file, documents_dir)
        similar_docs = json.loads(result_json)
        
        
        if similar_docs:
            print("Documents similaires trouvé:")
            return result_json
        else:
            print("\n aucune similarité trouvé.")
            
    except Exception as e:
        print(f"Error during plagiarism check: {e}")
        
if __name__ == "__main__":
    similar_json = main()
    print(similar_json)