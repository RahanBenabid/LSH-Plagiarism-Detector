import re
import random

def data_clean(essay):
	essay = essay.lower()
	essay = re.sub(r'[^\w\s]', '', essay)
	essay = re.sub(r'\s+', ' ', essay).strip()
	return essay

def shingling(essay, k: int = 4):
	shingles = []
	for i in range(len(essay) - k + 1):
		shingle = essay[i:i+k]
		shingles.append(shingle)
		
	return shingles

def hash_function(essay, seed):
	# This uses the murmurHash algorithm
	# source https://www.keiruaprod.fr/blog/2023/04/02/the-murmur-hashing-algorithm.html
	C1 = 0xcc9e2d51
	C2 = 0x1b873593
	R1 = 15
	R2 = 13
	M = 5
	N = 0xe6546b64
	
	hash_value = seed ^ len(essay)
	i = 0
	
	# Process the input in chunks of 4 bytes
	while i + 4 <= len(essay):
		k = int.from_bytes(essay[i:i + 4], byteorder='little')
		k = (k * C1) & 0xFFFFFFFF
		k = ((k << R1) | (k >> (32 - R1))) & 0xFFFFFFFF
		k = (k * C2) & 0xFFFFFFFF
		
		hash_value ^= k
		hash_value = ((hash_value << R2) | (hash_value >> (32 - R2))) & 0xFFFFFFFF
		hash_value = (hash_value * M + N) & 0xFFFFFFFF
		
		i += 4
		
	# Handle remaining bytes if any
	# not real necassary tho since the shingles are made of 4
	if i < len(essay):
		k = 0
		j = 0
		
		while i < len(essay):
			k ^= essay[i] << j
			i += 1
			j += 8
			
		k = (k * C1) & 0xFFFFFFFF
		k = ((k << R1) | (k >> (32 - R1))) & 0xFFFFFFFF
		k = (k * C2) & 0xFFFFFFFF
		
		hash_value ^= k
		
	# Finalize the hash value
	hash_value ^= len(essay)
	hash_value ^= hash_value >> 16
	hash_value = (hash_value * 0x85ebca6b) & 0xFFFFFFFF
	hash_value ^= hash_value >> 13
	hash_value = (hash_value * 0xc2b2ae35) & 0xFFFFFFFF
	hash_value ^= hash_value >> 16
	
	return hash_value

def minhash(shingles, num_hashes=100, seed=123456):
	import random
	random.seed(seed)
	# Ensure the range for randint is all integers
	seeds = [random.randint(1, int(1e9)) for _ in range(num_hashes)]
	
	minhashes = []
	for seed in seeds:
		min_hash = min(hash_function(shingle.encode('utf-8'), seed) for shingle in shingles)
		minhashes.append(min_hash)
	return minhashes

if __name__ == "__main__":
	essay = """
	The Impact of Social Media on Modern Society

	Social media has fundamentally transformed how we communicate and interact in the 21st century. 
	These platforms have created unprecedented opportunities for global connectivity, allowing people 
	from different corners of the world to share ideas, experkiences, and information instantly.
	"""
	
	cleaned_essay = data_clean(essay)
	print(cleaned_essay)
	
	shingles = shingling(cleaned_essay)
	print(shingles)
	
	seed = 123456789
	hashes = []
	for shingle in shingles:
		hashed_shingle = hash_function(shingle.encode('utf-8'), seed)
		hashes.append(hashed_shingle)
	
	print(hashes)
	
	minhashes = minhash(shingles)
	
	print(minhashes)
	