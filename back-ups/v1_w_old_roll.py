import PySimpleGUI as sg
import numpy as np
from assets import image_data as imgD
from assets import number_formatter as nf


import threading


#TODO: Player data saving + checking

# * Player data setup
multipliers = [1,1,1]
inventory = [0,1_000_000_000_000,0]
prestige = 0
money = 1000

#1_000_000_000_000


# * Prices setup
multiplier_price_legendary = lambda: round(3.5**(2 * multipliers[0]))
multiplier_price_mythic = lambda: 55**multipliers[1]
multiplier_price_godlike = lambda: 200**multipliers[2]





log_text = []

sg.theme("DarkBlue")

# --- COLUMNS --- # 
inventory_col = [
    [
        
    ],
    [
       sg.Image(data=imgD.legendary_key_img, subsample=20),  
       sg.Text("Legendary:", size=(10, 1)), sg.Text(f"{nf.sizeof_number(inventory[0])}", justification="right", key="-LEGENDARY KEY-")
    ],
    [
        sg.Image(data=imgD.mythic_key_img, subsample=20), 
        sg.Text("Mythic: ", size=(10, 1)), sg.Text(f"{nf.sizeof_number(inventory[1])}", justification="right", key="-MYTHIC KEY-")
    ],
    [
       sg.Image(data=imgD.godlike_key_img, subsample=20),  
       sg.Text("Godlike: ", size=(10, 1)), sg.Text(f"{nf.sizeof_number(inventory[2])}", justification="right", key="-GODLIKE KEY-")
    ]
]


multipliers_col = [
    [
        sg.Text("Legendary:", size=(10, 1)), 
        sg.Text(f"{multipliers[0]}x", size=(5, 1), justification="right", key="-LEGENDARY X VALUE-"), 
        sg.Button("+", key="-LEGENDARY INC-"),

        # Value unset, updated when switched to tab.
        sg.Text("$", key="-LEGENDARY X PRICE-", tooltip="0")
    ],
    [
        sg.Text("Mythic: ", size=(10, 1)), 
        sg.Text(f"{multipliers[1]}x", size=(5, 1), justification="right", key="-MYTHIC X VALUE-"), 
        sg.Button("+", key="-MYTHIC INC-"),

        sg.Text("$", key="-MYTHIC X PRICE-", tooltip="0")
    ],
    [
        sg.Text("Godlike: ", size=(10, 1)), 
        sg.Text(f"{multipliers[2]}x", size=(5, 1), justification="right", key="-GODLIKE X VALUE-"), 
        sg.Button("+", key="-GODLIKE INC-"),

        sg.Text("$", key="-GODLIKE X PRICE-", tooltip="0")
    ]
]

rewards_req = [
    [
        sg.Text("Requirements:", size=(10,1))
    ],
    [
        sg.HSeparator()
    ],
    [
        sg.Text("Anti stuck", size=(10,1))
    ],
    [
        sg.Image(data=imgD.godlike_key_img, subsample=20)
    ]
]


rewards_reward = [
    [
        sg.Text("Rewards:", size=(10,1))
    ],
    [
        sg.HSeparator()
    ],
    [
        sg.Text("$1", size=(10,1)), sg.Button("CLAIM", key="-TIME REWARD-")
    ],
    [
        sg.Text("Prestige", size=(10,1)), sg.Button("CLAIM", disabled=True, button_color="black", key="-PRESTIGE-")
    ]
]


# --- TABS --- # 

inventory_tab = [
    [
        sg.Column(inventory_col)
    ]
]


multiplier_tab = [
    [
        sg.Column(multipliers_col)
    ]
]

upgrades_tab = [
    [
        sg.Text("Coming soon: buy limits, \nMax open at same time ,time/open??")
    ]
]

rewards_tab = [
    # [
    #     sg.Text("3m"), sg.Text("$100"), sg.Button("Claim")
    # ],
    # [
    #    sg.Image(data=imgD.godlike_key_img, subsample=20), sg.Text("+1 Prestige!"), sg.Button("Claim")
    # ]
    [
        sg.Column(rewards_req),
        sg.VSeparator(),
        sg.Column(rewards_reward)
    ]
    
]

# - PRESTIGE - #
prestige0_tab = [
    [   
        sg.Button("?", tooltip="Information", button_color="white on blue" ,key="-STARTER CHEST INFO-"),

        sg.Text("Starter chest", size=(15,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-STARTER CHEST AMOUNT-"), 
        sg.Button("Buy", key="-STARTER CHEST ROLL-"), sg.Text("$10")
    ],
    [
        sg.Button("?", tooltip="Information", button_color="white on blue", key="-LEGENDARY CHEST INFO-"),

        sg.Text("Legendary chest", size=(15,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-LEGENDARY CHEST AMOUNT-"), 
        sg.Button("Buy", key="-LEGENDARY CHEST ROLL-"), 
        sg.Image(data=imgD.legendary_key_img, subsample=20) 
    ],
    [
        sg.Button("?", tooltip="Information", button_color="white on blue" , key="-MYTHIC CHEST INFO-"),

        sg.Text("Mythic chest", size=(15,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-MYTHIC CHEST AMOUNT-"), 
        sg.Button("Buy", key="-MYTHIC CHEST ROLL-"), 
        sg.Image(data=imgD.mythic_key_img, subsample=20)
    ]
]

prestige1_tab = [
    []
]

prestige2_tab = [
    []
]

# Dynamically make a list of tabs, updates
def get_prestige_tabs(current_prestige):

    prestige_tabs_info = {
        "P0": [prestige0_tab, current_prestige < 0],
        "P1": [prestige1_tab, current_prestige < 1],
        "P2": [prestige2_tab, current_prestige < 2],
    }
    prestige_tabs = []
    counter = 0
    for key in prestige_tabs_info:
        prestige_tabs.append(sg.Tab(f"{key}",prestige_tabs_info[key][0], key=f"-P TAB-{counter}-", disabled=prestige_tabs_info[key][1]))
        counter += 1

    return prestige_tabs

# Change the state of any button, shorter script
def update_button(key,state):
    if state == "on":
        window[key].update(button_color="white",disabled=False)
    elif state == "off":
        window[key].update(button_color="black",disabled=True)


#########################################################
# ! Anytime inventory is touched, run this to update GUI
#########################################################
def update_inventory():
    window["-MONEY-"].update(f"Total money: {nf.sizeof_number(money,"$")}")
    window["-MONEY-"].set_tooltip(f"${money:,}")


    window["-LEGENDARY KEY-"].update(f"{nf.sizeof_number(inventory[0])}")
    window["-MYTHIC KEY-"].update(f"{nf.sizeof_number(inventory[1])}")
    window["-GODLIKE KEY-"].update(f"{nf.sizeof_number(inventory[2])}")

def update_multipliers():


    #? Fix display?
    # Need to take away 1 from the displayed value since it's used when rolling even at lvl 1 -
    # Eg.: with 9x it would get you 8/100 l keys since it's only 8x in reality. 
    # Keep the -1 for accurate display!

    window["-LEGENDARY X VALUE-"].update(f"{multipliers[0]-1}x")
    window["-LEGENDARY X PRICE-"].update(f"{nf.sizeof_number(multiplier_price_legendary(),"$")}")
    window["-LEGENDARY X PRICE-"].set_tooltip(f"${multiplier_price_legendary():,}")

    window["-MYTHIC X VALUE-"].update(f"{multipliers[1]-1}x")
    window["-MYTHIC X PRICE-"].update(f"{nf.sizeof_number(multiplier_price_mythic(),"$")}")
    window["-MYTHIC X PRICE-"].set_tooltip(f"${multiplier_price_mythic():,}")

    window["-GODLIKE X VALUE-"].update(f"{multipliers[2]-1}x")
    window["-GODLIKE X PRICE-"].update(f"{nf.sizeof_number(multiplier_price_godlike(),"$")}")
    window["-GODLIKE X PRICE-"].set_tooltip(f"${multiplier_price_godlike():,}")



# - Chance calculations - #
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



# - CHEST ROLLING TECH -
def roll_chest(chest, options, chances, amount):
    global money
    global inventory
    global log_text

    # Total money earned in rolls
    roll_results = 0

    # Get a list of numbers, use less memory to randomize than strings
    chest_rewards = np.array([i for i in range(len(options))])

    results = np.random.choice(chest_rewards, size=amount, p=chances)

    # Count occurrences of each reward
    unique, counts = np.unique(results, return_counts=True)

    # Convert back to labels if needed (only for final output)
    reward_count = dict(zip(options, counts))


    if (chest == "STARTER"):
        
        roll_results += reward_count.get("Common",0) * 10
        roll_results += reward_count.get("Uncommon",0) * 10
        roll_results += reward_count.get("Rare",0) * 15
        roll_results += reward_count.get("Epic",0) * 25
        roll_results += reward_count.get("Legendary",0) * 50
        
        money += roll_results
        inventory[0] += reward_count.get("Legendary",0)

        # Doesn't look like you're getting anything cause you spend X and this includes what you spent
        log_text.append([f"You've rolled: ${roll_results:,} and {reward_count.get("Legendary",0):,} Legendary keys", "white"])
    

    if (chest == "LEGENDARY"):

        # ["Common", "Rare", "Epic", "Mythic", "Void", "Secret"]
        roll_results += reward_count.get("Common",0) * 10
        roll_results += reward_count.get("Rare",0) * 15
        roll_results += reward_count.get("Epic",0) * 25
        roll_results += reward_count.get("Secret",0) * 1_000_000
        
        
        # NEED to set log first, since it halves money. You don't want reward money to also half!!!

        if (reward_count.get("Void",0) > 0):
            for i in range(reward_count.get("Void",0)):  
                money *= 0.5
                money = round(money)
            log_text.append([f"You've rolled: ${roll_results:,} and {reward_count.get("Mythic",0):,} Mythic keys \n**YOU GOT UNLUCKY {reward_count.get("Void",0):,}x times!**", "white"]) 
        else:
        # Doesn't look like you're getting anything cause you spend X and this includes what you spent
            log_text.append([f"You've rolled: ${roll_results:,} and {reward_count.get("Mythic",0):,} Mythic keys", "white"])


        money += roll_results
        inventory[1] += reward_count.get("Mythic",0)

    if (chest == "MYTHIC"):

        # ["Common", "Rare", "Epic", "Godlike", "Secret"]
        roll_results += reward_count.get("Common",0) * 1000
        roll_results += reward_count.get("Rare",0) * 1500
        roll_results += reward_count.get("Epic",0) * 3000
        roll_results += reward_count.get("Secret",0) * 1_000_000_000_000
        
        

        # Doesn't look like you're getting anything cause you spend X and this includes what you spent
        money += roll_results

        if (reward_count.get("Godlike",0) > 0):
            inventory[2] += reward_count.get("Godlike",0)
            log_text.append([f"You've rolled: ${roll_results:,} and {reward_count.get("Godlike",0):,} Godlike keys", "yellow"])

        else:
            log_text.append([f"You've rolled: ${roll_results:,} and {reward_count.get("Godlike",0):,} Godlike keys", "white"])

        
    # After rolling, reduce log size so it isn't too big, then update the GUI
    # Saves last 25 | if over 30 it will reset  

    
    window["-LOG-"].update(f"\n{log_text[-1][0]}", append=True, text_color_for_value=log_text[-1][1])

    if(len(log_text) > 35):
        log_text = log_text[-25:]
        window['-LOG-'].update('')  # Clear the existing text

        for i in range(len(log_text)):
            line = log_text[i][0]
            color = log_text[i][1]

            window['-LOG-'].update(f"\n{line}", append=True, text_color_for_value=color)


    #TODO: Add saving here
    update_inventory()
            

# --- LAYOUT COLUMNS --- #

left_column = [
    [
        sg.TabGroup([[sg.Tab("Inventory", inventory_tab ), sg.Tab("Multipliers", multiplier_tab),  sg.Tab("Upgrades", upgrades_tab), sg.Tab("Rewards", rewards_tab)]],enable_events=True,key="-MENU TABS-")
    ]
]

right_column = [
    [
        # Def returns a list of active tabs
        sg.TabGroup([get_prestige_tabs(prestige)], key="-PRESTIGE TABS-")
    ]
]



# --- WINDOW --- # 

layout = [
    [
        sg.Text(f"Total money: {nf.sizeof_number(money,"$")}", tooltip=f"{money:,}", key="-MONEY-")
    ],
    [
        sg.Column(left_column),
        sg.Column(right_column)
    ],
    [
        sg.Multiline(size=(90,10), autoscroll=True ,key="-LOG-")
    ]
]

window = sg.Window("Chest Frenzy", layout, finalize=True)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        #TODO: Add saving here
        break


    # -- TAB UPDATES -- #

    if values["-MENU TABS-"] == "Inventory":
        update_inventory()

    if values["-MENU TABS-"] == "Multipliers":
        update_multipliers()


    if values["-MENU TABS-"] == "Rewards":
        
        # -- Time played updates

        # -- Prestige updates
        if inventory[2] >= 1:
            update_button("-PRESTIGE-","on")
        else:
            update_button("-PRESTIGE-","off")
        

    # -- MULTIPLIER BUTTONS

    if event == "-LEGENDARY INC-":

        # Value with out the $, then in the second line take out the "," and turn it into intiger value.
        # price_value = window['-LEGENDARY X PRICE-'].get()[1:]
        # price_of_upgrade = int(price_value.replace(',', ''))  

        price_of_upgrade = multiplier_price_legendary()


        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[0] += 1
            update_multipliers()
            update_inventory()


    if event == "-MYTHIC INC-":

        price_of_upgrade = multiplier_price_mythic()


        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[1] += 1
            update_multipliers()
            update_inventory()
        
        
        
    if event == "-GODLIKE INC-":
          
        price_of_upgrade = multiplier_price_godlike()

        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[2] += 1
            update_multipliers()
            update_inventory()

        
        


    # -- CHEST BUTTONS

    if event == "-STARTER CHEST ROLL-":
        # Handle if it's a letter not int. No need for anything as second test will not roll if it's 0.
        try:
            roll_amount = int(values["-STARTER CHEST AMOUNT-"])
        except:
            window["-STARTER CHEST AMOUNT-"].update(0)

        if (roll_amount > 0 and money >= roll_amount*10):
            
            chest_options = np.array(["Common", "Uncommon","Rare","Epic","Legendary"])
            chest_chances = [41,30,20,8,1]
        
            money -= roll_amount*10

            #roll_chest("STARTER",chest_options,chest_chances,roll_amount)
            threading.Thread(target=roll_chest, args=("STARTER",chest_options, adjust_weights(chest_options,chest_chances,"Legendary", multipliers[0]), roll_amount), daemon=True).start()

            update_inventory()
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")



    if event == "-LEGENDARY CHEST ROLL-":
        # Same STR test here. ^^
        try:
            roll_amount = int(values["-LEGENDARY CHEST AMOUNT-"])
        except:
            window["-LEGENDARY CHEST AMOUNT-"].update(0)


        if (roll_amount > 0 and inventory[0] >= roll_amount):

            chest_options = np.array(["Common", "Rare", "Epic", "Mythic", "Secret", "Void"])
            chest_chances = [88.99989, 10, 1, 0.001, 0.0001, 0.00001]
            # 0.0001 = 1/1M
            # 0.00001 = 1/10M
            # 0.000001 = 1/100M
            inventory[0] -= roll_amount

            #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
            
            threading.Thread(target=roll_chest, args=("LEGENDARY",chest_options, adjust_weights(chest_options,chest_chances,"Mythic", multipliers[1]), roll_amount), daemon=True).start()

            update_inventory()
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")

    if event == "-MYTHIC CHEST ROLL-":
        # Same STR test here. ^^
        try:
            roll_amount = int(values["-MYTHIC CHEST AMOUNT-"])
        except:
            window["-MYTHIC CHEST AMOUNT-"].update(0)


        if (roll_amount > 0 and inventory[1] >= roll_amount):

            chest_options = np.array(["Common", "Rare", "Epic", "Secret", "Godlike"])
            chest_chances = [89.89989, 10, 0.1, 0.0001, 0.00001]
            # 0.0001 = 1/1M
            # 0.00001 = 1/10M
            # 0.000001 = 1/100M
            inventory[1] -= roll_amount

            #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
            
            threading.Thread(target=roll_chest, args=("MYTHIC",chest_options, adjust_weights(chest_options,chest_chances,"Godlike", multipliers[2]), roll_amount), daemon=True).start()

            update_inventory()
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")

    # - INFO

    if event == "-STARTER CHEST INFO-":
        info = '''
        Starter Chest: (No multipliers) 
        -------------------------------
        Common:\t\t\t40% = $10
        Uncommon:\t\t\t30% = $10
        Rare:\t\t\t20% = $15
        Epic:\t\t\t 8% = $25
        Legendary:\t\t\t 1% = $50, 1x Legendary key
        '''

        sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(50,10))


    if event == "-LEGENDARY CHEST INFO-":
        info = '''
        Legendary Chest: (No multipliers) 
        -------------------------------
        Common:\t\t\t88% = $10
        Rare:\t\t\t10% = $20
        Epic:\t\t\t 1% = 1x Legendary key
        Mythic:\t\t\t0.001% = 1x Mythic key
        VOID:\t\t\t 0.00001% = Half all your money (1/10M)
        \n\n\n\n
        *SECRET*:\t\t\t 0.0001% = $10M (1/1M)
        '''

        sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

    if event == "-MYTHIC CHEST INFO-":
        info = '''
        Mythic Chest: (No multipliers) 
        -------------------------------
        Common:\t\t\t90% = $1K
        Rare:\t\t\t10% = $1.5K
        Epic:\t\t\t 1% = $3K
        Godlike:\t\t\t 0.00001% = 1x Godlike key (1/10M)
        \n\n\n\n
        *SECRET*:\t\t\t 0.0001% = $1T (1/1M)
        '''

        sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))


    # -- REWARD BUTTONS

    if event == "-TIME REWARD-":
        money += 1
        update_inventory()

    if event == "-PRESTIGE-" and inventory[2] >= 1:

        #Confirmations
        confirmation =  sg.popup_yes_no("*WARNING*\nA prestige will reset everything!",  title="Prestige")
        
        if (confirmation == "Yes"):

            # Increase prestige variable, check if prestige tab exists
            prestige +=1
    
            inventory = [0,0,0]
            money = 1000

            sg.popup(f"You've prestiged!\nPrestige: {prestige} ")
            
            temp_prestige_tab = f"-P TAB-{prestige}-" 

            if (temp_prestige_tab in window.AllKeysDict):
                window[temp_prestige_tab].update(disabled=False)
            else:
                print("You're above max prestige!")
            
            # Bring back to show inventory - Hides the rewards tab updating, prevents multi prestige?
            window["-MENU TABS-"].Widget.select(0)
       
window.close()