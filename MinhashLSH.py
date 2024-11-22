# the shingling method will create overlapping fragments of a set
# then a set of random hash functions
from collections import defaultdict

def minhash(data, num_perm):
  minhash_signatures = defaultdict(list)
  
  # create a list of hash functions
  hash_functions = [lambda x, i=i: hash(str(x) + str(i)) for i in range(num_perm)]
  
  for element in data:
    # for each element, compute the min hash value for each hash function
    minhash_signatures[element] = [min(hash_function(word) for word in element.split()) for hash_function in hash_functions]
    
  return minhash_signatures


# function to create an LSH index, assign items to buckets, and perform a similarity search
def lsh(data, num_perm):
  # create a minhash signature for each data point
  minhash_dict = minhash(data, num_perm)
  index = defaultdict(list)
  
  # assign data points to buckets based on their minhash signature
  for point, signature in minhash_dict.items():
    bucket_id = tuple(signature)
    index[bucket_id].append(point)
    
  # perform similarity searcg by finding data points in the same bucket
  similar_items = {}
  for query, query_signature in minhash_dict.items():
    bucket_id = tuple(query_signature)
    candidates = index[bucket_id]
    similar_items[query] = candidates
  
  return similar_items

# example dataset
data = ["cat dog rabbit", "dog lizzard bird", "cat bear crow", "lion lizard panda"]

# adjust the number of permutations as required
num_perm = 16

# find similar items
similar_items = lsh(data, num_perm)

# display the similar items
print("Similar items:")
for query, items in similar_items.items():
  print(f"\tQuery: {query}")
  print(f"\tItems: {items}")