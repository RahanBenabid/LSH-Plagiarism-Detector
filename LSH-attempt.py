import re

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
	# this uses the murmurHash algorithm
	return 

if __name__ == "__main__":
	essay = """
	The Impact of Social Media on Modern Society

	Social media has fundamentally transformed how we communicate and interact in the 21st century. 
	These platforms have created unprecedented opportunities for global connectivity, allowing people 
	from different corners of the world to share ideas, experiences, and information instantly.
	"""
	
	cleaned_essay = data_clean(essay)
	print(cleaned_essay)
	
	shingles = shingling(cleaned_essay)
	print(shingles)
	
	test = "Hello world"
	seed = 123456789
	hash = hash_function(test, seed)