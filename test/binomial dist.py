import numpy as np
import time 

# amount = 10 billion (1e10), probability = 0.000001%
amount = 10**9
probability = 0.000001 / 100  # Convert percentage to a fraction

# Break into smaller chunks to avoid overflow
chunk_size = 10**7  # 10 million trials at a time
num_chunks = amount // chunk_size

# Simulate binomial distribution in smaller chunks and sum the results
godlike = sum(np.random.binomial(n=chunk_size, p=probability, size=num_chunks))

# Handle any leftover trials if amount is not a perfect multiple of chunk_size
leftover_trials = amount % chunk_size
if leftover_trials > 0:
    godlike += np.random.binomial(n=leftover_trials, p=probability)

print(godlike)
