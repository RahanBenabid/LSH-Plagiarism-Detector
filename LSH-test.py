# this code generates a sample datapoint, defines the number of random projections & data dimentionality, generates a random projection matrix, hashes the datapoint, prints the hash values in 1s and 0s

import numpy as np

def hash_function(datapoint, random_vector):
  """
  Hashes a datapoint using a random projection vector.
  
  Args:
    datapoint: A numpy array representing the datapoint
    random_vector: A numpy array representing the random projection vector

  Returns:
    a single bit hash value (0-1)
  """
  projection = np.dot(datapoint, random_vector)
  return 1 if projection >= 0 else 0

def generate_random_matrix(num_projections, data_dim):
  """
  Generates a random projection matrix with specified dimentions

  Args:
    num_projections: number of random projection vectors to generate
    data_dim: Dimentionality of the datapoints

  Returns:
    Numpy array representing the random projection matrix
  """
  
  return np.random.randn(num_projections, data_dim)

def lsh_hash(datapoint, random_matrix):
  """
  Hashes a datapoint using multiple random projections

  Args:
    datapoint: a Numpy array reprenting the datapoint
    random_matrix: a Numpy array representing the random projection matrix

  Returns:
    a list of hash values (ine for each random projection vector)
  """
  
  hash_values = []
  for random_vector in random_matrix:
    hash_values.append(hash_function(datapoint, random_vector))
  return hash_values

# datapint sample
datapoint = np.array([1, 2, 3])

# number of random projections
num_projections = 2

# dimentionality of datapoints
data_dim = len(datapoint)

# generate a random projection matrix
random_matrix = generate_random_matrix(num_projections, data_dim)

# hash the datapoint
hash_values = lsh_hash(datapoint, random_matrix)

# print the hash values
print("LSH Hash:", hash_values)