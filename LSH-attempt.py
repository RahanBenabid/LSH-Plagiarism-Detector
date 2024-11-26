import re
import random
import numpy as np

def data_clean(text):
	"""a function that cleans all the unnecesary characters and whitespaces in the document"""
	text = text.lower()
	text = re.sub(r'[^\w\s]', '', text)
	text = re.sub(r'\s+', ' ', text).strip()
	return text

def shingling(text, k: int = 3):
	"""creates shingles out of the cleaned text"""
		
	return {text[i:i+k] for i in range(len(text) - k + 1)}

def hash_function(value: str, a: int, b: int):
	prime = 16777619
	hash_val = 2166136261
	
	for char in value:
		hash_val = hash_val ^ ord(char)
		hash_val = ((hash_val * prime) & 0xFFFFFFFF)
		
	result = (((a & 0xFFFFFFFF) * (hash_val & 0xFFFFFFFF)) & 0xFFFFFFFF)
	result = ((result + (b & 0xFFFFFFFF)) & 0xFFFFFFFF)
	return result



def minhash(shingles, num_hashes=100, seed=123456):
	"""uses the hash functions and finds the minhash for each shingle"""
	import random
	random.seed(seed)
	seeds = [(random.randint(1, int(1e9)), random.randint(1, int(1e9))) for _ in range(num_hashes)]
	
	minhashes = []
	for a, b in seeds:
		min_hash = min(hash_function(shingle, a, b) for shingle in shingles)
		minhashes.append(min_hash)
		
	return minhashes

def jaccard_similarity(list1, list2):
	"""this will compare the similarities between two documents"""
	# source: https://www.geeksforgeeks.org/how-to-calculate-jaccard-similarity-in-python/
	
	
	set1 = set(list1)
	set2 = set(list2)
	
	intersection = len(set1.intersection(set2))
	union =  len(set1.union(set2))
	
	return intersection / union


if __name__ == "__main__":
	essay1 = """
	The Impact of Social Media on Modern Society

	Social media has fundamentally transformed how we communicate and interact in the 21st century. 
	These platforms have created unprecedented opportunities for global connectivity, allowing people 
	from different corners of the world to share ideas, experiences, and information instantly.
	"""
	
	# Plagiarized version with some modifications
	essay2 = """
	The Future of Renewable Energy
	
	Renewable energy technologies are rapidly advancing and becoming increasingly important in our 
	fight against climate change. Solar and wind power have seen dramatic improvements in efficiency 
	and cost-effectiveness over the past decade.
	"""
	
	cleaned_essay1 = data_clean(essay1)
	cleaned_essay2 = data_clean(essay2)
	
	# print(cleaned_essay)
	
	shingles1 = shingling(cleaned_essay1)
	shingles2 = shingling(cleaned_essay2)
	
	# print(shingles)
	
	minhashes1 = minhash(shingles1)
	minhashes2 = minhash(shingles2)
	
	print(minhashes1)
	
	print(jaccard_similarity(minhashes1, minhashes2))
	