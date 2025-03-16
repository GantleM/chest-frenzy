import numpy as np
import uuid


def roll(chest, options, chances, amount, item_bonus):

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

    if(amount > max_Real_ROLLS):

        if (amount > 100_000_000_000):
            chunk_size = 10**8  # 100 million trials at a time
        else:
            chunk_size = 10**7 # 10 million trials at a time
        num_chunks = amount // chunk_size


        estimated_counts = {}
        # Loop through each reward and calculate estimated counts
        for reward, probability in zip(chest_rewards, chances):

    
            # Get a list of results/chunk
            result_chunks = np.random.binomial(n=chunk_size, p=probability, size=num_chunks)

            # ! MAKE SURE INT64 TO AVOID OVERFLOW!!
            total_sum = np.sum(result_chunks, dtype=np.int64)

            estimated_counts[reward] = total_sum

            leftover_trials = amount % chunk_size

            # If more needed, then add those too
            if leftover_trials > 0:
                estimated_counts[reward] += np.random.binomial(n=leftover_trials, p=probability)

        # Put it into correct format
        reward_count = dict(zip(options, estimated_counts.values()))

    else:
        
        # Do rolls
        results = np.random.choice(chest_rewards, size=amount, p=chances)

        # Count occurrences of each reward
        unique, counts = np.unique(results, return_counts=True)

        # Convert back to labels if needed (only for final output)
        #reward_count = dict(zip(options, counts))
        reward_count = {options[unique[i]]: counts[i] for i in range(len(unique))}
        

    print(reward_count)
    # print(type(roll_results))
    # print(type(reward_count))
    
    if (chest == "STARTER"):
        
        roll_results[-1] += int(reward_count.get("Common",0)) * 10
        roll_results[-1] += int(reward_count.get("Uncommon",0)) * 10
        roll_results[-1] += int(reward_count.get("Rare",0)) * 15
        roll_results[-1] += int(reward_count.get("Epic",0)) * 25
        roll_results[-1] += int(reward_count.get("Legendary",0)) * 50
        
        # Set amount of keys earned.
        roll_results[0] += reward_count.get("Legendary",0)

        if item_bonus[0] == "key":
            roll_results[0] = int(roll_results[0]*item_bonus[1])

        elif item_bonus[0] == "money":
            roll_results[-1] = int(roll_results[-1]*item_bonus[1])
           
        


        # Doesn't look like you're getting anything cause you spend X and this includes what you spent
        log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {roll_results[0]:,} Legendary keys", "light gray"])
    

    if (chest == "LEGENDARY"):

        # ["Common", "Rare", "Epic", "Mythic", "Void", "Secret"]
        roll_results[-1] += int(reward_count.get("Common",0)) * 10
        roll_results[-1] += int(reward_count.get("Rare",0))* 15
        roll_results[-1] += int(reward_count.get("Epic",0)) * 25
        roll_results[-1] += int(reward_count.get("Secret",0)) * 1_000_000
        
        
        # adds how many times you got "void" -> 0.5x your money
        roll_results[-2][0] = reward_count.get("Void",0)
        roll_results[1] += reward_count.get("Mythic",0)

        if item_bonus[0] == "key":
            roll_results[1] = int(roll_results[1]*item_bonus[1])

        elif item_bonus[0] == "money":
            roll_results[-1] = int(roll_results[-1]*item_bonus[1])


        if (roll_results[-2][0] > 0):
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {roll_results[1]:,} Mythic keys \n**YOU GOT UNLUCKY {reward_count.get("Void",0):,}x times!**", "light gray"]) 
        else:
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {roll_results[1]:,} Mythic keys", "light gray"])


        
        

    if (chest == "MYTHIC"):

        # ["Common", "Rare", "Epic", "Godlike", "Secret"]
        roll_results[-1] += int(reward_count.get("Common",0)) * 1000
        roll_results[-1] += int(reward_count.get("Rare",0)) * 1500
        roll_results[-1] += int(reward_count.get("Epic",0)) * 3000
        roll_results[-1] += int(reward_count.get("Secret",0)) * 1_000_000_000_000
        
    
        if item_bonus[0] == "money":
            print(roll_results[-1], "and", item_bonus[1])
            roll_results[-1] = int(roll_results[-1]*item_bonus[1])


        # If you get godlike, it changes message colour. 
        if (reward_count.get("Godlike",0) > 0):
            roll_results[2] += reward_count.get("Godlike",0)
            
            #! Need to be different as key is checked only if you got some
            if item_bonus[0] == "key":
                roll_results[2] = int(roll_results[2]*item_bonus[1])


            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {roll_results[2]:,} Godlike keys", "yellow"])

        else:
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,} and {roll_results[2]:,} Godlike keys", "light gray"])

    if (chest == "ASCENSION"):
        # ["Common", "Rare", "Very rare", "Epic", "JACKPOT"]
        roll_results[-1] += int(reward_count.get("Common",0)) * 10000
        roll_results[-1] += int(reward_count.get("Rare",0)) * 15000
        roll_results[-1] += int(reward_count.get("Very rare",0)) * 25000
        roll_results[-1] += int(reward_count.get("Epic",0)) * 100000
        roll_results[-1] += int(reward_count.get("JACKPOT",0)) * 1_000_000
        

        # If you get godlike, it changes message colour. 
        if (reward_count.get("JACKPOT", 0) > 0):
            log_to_add.append([f"YOU GOT A JACKPOT! ${roll_results[-1]:,}", "red"])

        else:
            log_to_add.append([f"You've rolled: ${roll_results[-1]:,}", "pink"])


    # Add log text to position -3.
    roll_results.insert(-2,log_to_add[0])
    return roll_results


def item_chest_roll(float_chances, item_chances, rarity_chances):
    item_float_category = np.random.choice([0.8,0.75,0.4,0], p=float_chances)
                                  
    if item_float_category == 0.8:
        floatNum = np.random.uniform(0.8, 1.0000001)
        
    elif item_float_category == 0.75:
        floatNum = np.random.uniform(0.75, 0.8000001)

    elif item_float_category == 0.4:
        floatNum = np.random.uniform(0.4, 0.7500001)

    elif item_float_category == 0:
        floatNum = np.random.uniform(0, 0.4000001)
       
    name = np.random.choice(["Fortune Cookie","Metal Detector", "X-Ray Goggles"],p=item_chances )

    rarity = np.random.choice(["Paper", "Metal", "Emerald", "Ruby" , "Golden", "Diamond"], p=rarity_chances)


    #print(round(floatNum,3))
    #{"id": "iwx334212", "rarity":"Golden", "name":"Fortune Cookie", "float":0.234, "display": "Golden ⭐ Fortune Cookie [0.834]"},

    floatNum = round(floatNum,3)
    
    if floatNum == 1:
        display = f"{rarity} ⭐ {name} [{floatNum}]"
        log = [f"You've rolled: {display}", "yellow"]
    else:
        display = f"{rarity} {name} [{floatNum}]"
        log = [f"You've rolled: {display}", "light gray"]

    generated_item = {
        "id": str(uuid.uuid4()),
        "rarity": rarity,
        "name": name,
        "float": floatNum,
        "display": display
        
    }

    result = [generated_item,log]
    return(result)
    # print(generated_item)
    