import numpy as np


def adjust_weights(options, chances, item_to_increase, increase_factor):
    """
    Dynamically adjust the weights for a specific item.
    """
    # Instead of adding to 100, make them add to 1 for numpy
    chances_as_one = [i/100 for i in(chances)]

    # Create a copy of the original chances to modify
    adjusted_chances = np.copy(chances_as_one)

    # Find the index of the item to increase
    item_index = np.where(options == item_to_increase)[0][0]

    # Increase the weight for the selected item
    adjusted_chances[item_index] *= increase_factor

    # Re-normalize the weights so they still sum to 1
    adjusted_chances /= np.sum(adjusted_chances)

    return adjusted_chances


#chest_options = np.array(["Common", "Uncommon","Rare","Epic","Legendary"])
#chest_chances = [41,30,20,8,1]
# adjust_weights(chest_options,chest_chances,"Legendary", multipliers[0])


chest_options = np.array(["Common", "Uncommon","Rare","Epic","Legendary"])
chest_chances = [41,30,20,8,1]

roll_amount = 10_000_000_000

stuff = adjust_weights(chest_options,chest_chances,"Legendary", 17), roll_amount

chest_rewards = np.array([i for i in range(len(chest_options))])

estimated_counts = {}

chunk_size = 10_000_000

num_chunks = roll_amount//chunk_size

for reward, probability in zip(chest_rewards, stuff[0]):
    # Calculate expected count based on probability over 1 billion rolls
    #expected_count_full =  amount * probability 

    # Set rewards amount to chunks added
    

    result_chunks = np.random.binomial(n=chunk_size, p=probability, size=num_chunks)

    total_sum = np.sum(result_chunks, dtype=np.int64)

    print(total_sum)
    #estimated_counts[reward] = sum(np.random.binomial(n=chunk_size, p=probability, size=num_chunks))

    leftover_trials = roll_amount % chunk_size

    # If more needed, then add those too
    if leftover_trials > 0:
        estimated_counts[reward] += np.random.binomial(n=leftover_trials, p=probability)

    print("got: ", estimated_counts[reward])















# print(adjust_weights(np.array(["Yes","No"]), [99.99999,0.00001], "No", 1))

# amount = 1_000_000_000

# probability = 0.00001
# print(amount * probability/100)

# expected_count_full = round(amount * probability/100,2)

# prob_rounded = round(probability/100, 2)

# eee = adjust_weights(np.array(["Yes","No"]), [99.99999,0.00001], "No", 1)
# # godlike = round(np.random.normal(loc=expected_count_full, scale=np.sqrt(expected_count_full)))
# godlike = np.random.binomial(n=amount, p=eee[1])


# print(f"Expected: {expected_count_full}, got:{godlike}")