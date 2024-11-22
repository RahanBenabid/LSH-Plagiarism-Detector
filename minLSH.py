from collections import defaultdict

def minhash(data, num_perm):
	minhash_signature = defaultdict(list)
	
	# create a list of hash functions
	hash_functions = [lambda x, i=i: hash(str(x) + str(i)) for i in range(num_perm)]
	
	# print(hash_functions)
	
	for element in data:
		# for each element, compute the min hash value for each hash function
		for hash_function in hash_functions:
			minhash_signature[element].append(min(hash_function(x) for x in element.split()))
		
		return minhash_signature
	
# this one creates an LSH index, assign items to buckets, and perofrms a similarity search
def lsh(data, num_perm):
	# create a minhash signature for each data point
	minhash_dict = minhash(data, num_perm)
	index = defaultdict(list)
	
	# assign data points to buckets based on their minhash signature
	for point, signature in minhash_dict.items():
		bucket_id = tuple(signature)
		index[bucket_id].append(point)
		
	# perform similarity search by finding data points in the same bucket
	similar_items = {}
	for query, query_signature in minhash_dict.items():
		bucket_id = tuple(query_signature)
		candidates = index[bucket_id]
		similar_items[query] = candidates
	
	return similar_items

data = ["cat dog rabbit", "dog lizard bird", "cat bear crow", "lion lizard panda"]

num_perm = 16

similar_items = lsh(data, num_perm)

print("Similar items:")
for query, items in similar_items.items():
	print(f"\tQuery: {query}")
	print(f"\tItems: {items}")
	