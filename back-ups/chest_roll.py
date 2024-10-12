
#!!!! OLD VERSION !!!! USES NORMAL FOR SMALL PROBABOLOTY (NOT ACCURATE + SLOW!!!)

import numpy as np
from collections import Counter


def roll(chest, options, chances, amount, money):

    #TODO: If amount > 1m or 10m: Roll 100k random, then multiply results instead of actully that much??

    # Description
    roll_results = [
        0, # 0-Legendary key
        0, # 1-Mythic key
        0, # 2-Godlike key
        0, # 3- Ascention token key
          # -3 LOG TO ADD - Will be a tuple here
        [0], # -2-money to void 
        0] # -1-Money to add
    log_to_add = []

    # Get a list of numbers, use less memory to randomize than strings
    chest_rewards = np.array([i for i in range(len(options))])

    #* If more than 1M rolls, then simulate. Otherwise, do actual rolls.
    max_Real_ROLLS = 1_000_000

    if(amount > 1_000_000_000):
        '''
        chunk_size = 10**7  # 10 million trials at a time
        num_chunks = amount // chunk_size


        estimated_counts = {}
        # Loop through each reward and calculate estimated counts
        for reward, probability in zip(chest_rewards, chances):
            # Calculate expected count based on probability over 1 billion rolls
            expected_count_full =  amount * probability 
            print(expected_count_full)


            # Set rewards amount to chunks added
            estimated_counts[reward] = sum(np.random.binomial(n=chunk_size, p=probability, size=num_chunks))

            leftover_trials = amount % chunk_size

            # If more needed, then add those too
            if leftover_trials > 0:
                estimated_counts[reward] += np.random.binomial(n=leftover_trials, p=probability)

            print("got: ", estimated_counts[reward])
        '''

        
        results = np.random.choice(chest_rewards, size=5_000_000, p=chances)

        # Count occurrences of each reward in the smaller sample
        result_counts = Counter(results)

        # Scale factor for estimating results, rounded to 2 decimal places
        scale_factor = round(amount / 5_000_000, 2)
        
        # Create a dictionary to store the final estimates
        estimated_counts = {}
        # Loop through each reward and calculate estimated counts
        for reward, probability in zip(chest_rewards, chances):
            # Calculate expected count based on probability over 1 billion rolls
            expected_count_full =  amount * probability/100 #! TURN IT INTO A PERCENTAGE!!!!
            print(expected_count_full)

            if reward in result_counts:
                # If the reward appeared in the small sample, use the Poisson distribution
                actual_count = result_counts[reward] * scale_factor

                # estimated_counts[reward] = np.random.poisson(lam=actual_count)

                estimated_counts[reward] = round(np.random.normal(loc=actual_count, scale=np.sqrt(actual_count)))
                
                # estimated_counts[reward] = actual_count
            else:
                # If the reward didn't appear, use its expected count directly with Poisson
                # estimated_counts[reward] = np.random.poisson(lam=expected_count_full)

                estimated_counts[reward] = round(np.random.normal(loc=expected_count_full, scale=np.sqrt(expected_count_full)))
        
        # Put it into correct format
        reward_count = dict(zip(options, estimated_counts.values()))

    elif(amount > max_Real_ROLLS):
        results = np.random.choice(chest_rewards, size=max_Real_ROLLS, p=chances)

        # Count occurrences of each reward in the smaller sample
        result_counts = Counter(results)

        # Scale factor for estimating results, rounded to 2 decimal places
        scale_factor = round(amount / max_Real_ROLLS, 2)
        
        # Create a dictionary to store the final estimates
        estimated_counts = {}
        # Loop through each reward and calculate estimated counts
        for reward, probability in zip(chest_rewards, chances):
            # Calculate expected count based on probability over 1 billion rolls
            expected_count_full = probability * amount
            print(expected_count_full)

            if reward in result_counts:
                # If the reward appeared in the small sample, use the Poisson distribution
                actual_count = result_counts[reward] * scale_factor

                estimated_counts[reward] = np.random.poisson(lam=actual_count)
                
                # estimated_counts[reward] = actual_count
            else:
                # If the reward didn't appear, use its expected count directly with Poisson
                estimated_counts[reward] = np.random.poisson(lam=expected_count_full)

        # Put it into correct format
        reward_count = dict(zip(options, estimated_counts.values()))

    else:
        # Do rolls
        results = np.random.choice(chest_rewards, size=amount, p=chances)

        # Count occurrences of each reward
        unique, counts = np.unique(results, return_counts=True)

        # Convert back to labels if needed (only for final output)
        reward_count = dict(zip(options, counts))

    print(reward_count)
    
    if (chest == "STARTER"):
        
        roll_results[-1] += reward_count.get("Common",0) * 10
        roll_results[-1] += reward_count.get("Uncommon",0) * 10
        roll_results[-1] += reward_count.get("Rare",0) * 15
        roll_results[-1] += reward_count.get("Epic",0) * 25
        roll_results[-1] += reward_count.get("Legendary",0) * 50
        
        # Set amount of keys earned.
        roll_results[0] += reward_count.get("Legendary",0)

        # Doesn't look like you're getting anything cause you spend X and this includes what you spent
        log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {reward_count.get("Legendary",0):,} Legendary keys", "light gray"])
    

    if (chest == "LEGENDARY"):

        # ["Common", "Rare", "Epic", "Mythic", "Void", "Secret"]
        roll_results[-1] += reward_count.get("Common",0) * 10
        roll_results[-1] += reward_count.get("Rare",0) * 15
        roll_results[-1] += reward_count.get("Epic",0) * 25
        roll_results[-1] += reward_count.get("Secret",0) * 1_000_000
        
        
        # adds how many times you got "void" -> 0.5x your money
        roll_results[-2][0] = reward_count.get("Void",0)

        if (roll_results[-2][0] > 0):
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {reward_count.get("Mythic",0):,} Mythic keys \n**YOU GOT UNLUCKY {reward_count.get("Void",0):,}x times!**", "light gray"]) 
        else:
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {reward_count.get("Mythic",0):,} Mythic keys", "light gray"])


        
        roll_results[1] += reward_count.get("Mythic",0)

    if (chest == "MYTHIC"):

        # ["Common", "Rare", "Epic", "Godlike", "Secret"]
        roll_results[-1] += reward_count.get("Common",0) * 1000
        roll_results[-1] += reward_count.get("Rare",0) * 1500
        roll_results[-1] += reward_count.get("Epic",0) * 3000
        roll_results[-1] += reward_count.get("Secret",0) * 1_000_000_000_000
        

        # If you get godlike, it changes message colour. 
        if (reward_count.get("Godlike",0) > 0):
            roll_results[2] += reward_count.get("Godlike",0)
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {reward_count.get("Godlike",0):,} Godlike keys", "yellow"])

        else:
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {reward_count.get("Godlike",0):,} Godlike keys", "light gray"])

    # Add log text to position -3.
    roll_results.insert(-2,log_to_add[0])
    return roll_results