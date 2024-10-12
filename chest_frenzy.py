import PySimpleGUI as sg
import numpy as np
import threading
import os
import time
import roman

#* Custom modules
from assets import image_data as imgD
from assets import number_formatter as nf
from assets import chest_roll as roll
from assets import save_data as save_game
from assets import popup_windows as popups



def do_autosave():
    save_game.write_save(total_chest_opened,multipliers,inventory,prestige,money,upgrades)


# * IMORTANT VARIABLES
version = 3.8
currently_opening = 0


sg.theme("DarkBlue")


if(os.path.isfile("saves/save1.json")):
    saved_data = save_game.read_save()

    total_chest_opened = saved_data["total_chest_opened"]
    multipliers = saved_data["multipliers"]
    inventory = saved_data["inventory"]
    prestige = saved_data["prestige"]
    money = saved_data["money"]
    upgrades = saved_data["upgrades"]



else:

    popups.tutorial(version)

    # * Player data setup
    total_chest_opened = 0
    multipliers = [1,1,1]
    inventory = [0,0,0,0]
    prestige = 0
    money = 1000
    upgrades = {
        "max_buy_limit_level": 1,
        "max_buy_limit_cap_increase" : 0,
        "max_par_rolls": 1,
        "upgrade_discount": 0,
        "multiplier_discount": 0,
        "extra_AT": 0
    }

    do_autosave()

#1_000_000_000_000

# * Prices setup
# multiplier_price_legendary      = lambda: round(3.5**(2 * multipliers[0]))

def multiplier_price(rarity):

    match rarity:
        case "legendary":
            base_price = round(3.5**(2 * multipliers[0]))
        
        case "mythic":
            base_price = 55**multipliers[1]
        
        case "godlike":
            base_price = 200**multipliers[2]

    discount_percent = upgrades["multiplier_discount"] / 100

    discount = round(base_price * discount_percent)

    return base_price-discount



# multiplier_price_mythic         = lambda: 55**multipliers[1]
# multiplier_price_godlike        = lambda: 200**multipliers[2]

def upgrade_price(name):
    match name:
        case "max_buy_limit":
            
            # After 10B buy limit, we increase price eg.: instead of 1qu -> 10qu
            if (upgrades["max_buy_limit_level"] > 11):
                price_num = 10000
            else:
                price_num = 1000

            base_price = price_num*(10**upgrades["max_buy_limit_level"])

        case "max_par_rolls":
            base_price = 100**upgrades["max_par_rolls"]
        
    discount_percent = upgrades["upgrade_discount"] / 100
    discount = round(base_price * discount_percent)

    return base_price-discount

 
#upgrade_price_buylimit          = lambda: 1000*(10**upgrades["max_buy_limit_level"])
upgrade_value_buylimit          = lambda: 10**upgrades["max_buy_limit_level"]

#upgrade_price_par_roll          = lambda: 100**upgrades["max_par_rolls"]



log_text = []



# --- COLUMNS --- # 
info_col = [
    [
        sg.Text(f"Total money: {nf.sizeof_number(money,"$")}", tooltip=f"{money:,}", key="-MONEY-")
    ],
    [
        sg.Text(f"Prestige: {roman.toRoman(prestige)}", key="-PRESTIGE DISPLAY-")
    ]
]

max_open_col = [
    [
        sg.Text(f"{currently_opening}/{upgrades["max_par_rolls"]} chests opening", key= "-CURRENTLY ROLLING-")
    ]
]

inventory_col = [
    [
        
    ],
    [
       sg.Image(data=imgD.legendary_key_img, subsample=20),  
       sg.Text("Legendary:", size=(15, 1)), 
       sg.Text(f"{nf.sizeof_number(inventory[0])}", justification="right", key="-LEGENDARY KEY-")
    ],
    [
        sg.Image(data=imgD.mythic_key_img, subsample=20), 
        sg.Text("Mythic: ", size=(15, 1)), 
        sg.Text(f"{nf.sizeof_number(inventory[1])}", justification="right", key="-MYTHIC KEY-")
    ],
    [
       sg.Image(data=imgD.godlike_key_img, subsample=20),  
       sg.Text("Godlike: ", size=(15, 1)), 
       sg.Text(f"{nf.sizeof_number(inventory[2])}", justification="right", key="-GODLIKE KEY-")
    ],
    [
       sg.Image(data=imgD.ascension_toke_img, subsample=20, visible=prestige>0, key="-ASCENSION TOKEN IMG-"),  
       sg.Text("Ascension Token: ", size=(15, 1), visible=prestige>0, key="-ASCENSION TOKEN TEXT-"), 
       sg.Text(f"{nf.sizeof_number(inventory[3])}", justification="right", visible=prestige>0 ,key="-ASCENSION TOKEN-")
    ]
]


multipliers_col = [
    [
        sg.Text("Legendary:", size=(10, 1)), 
        sg.Text(f"{multipliers[0]}x", size=(5, 1), justification="right", key="-LEGENDARY X VALUE-"), 
        sg.Button("+", key="-LEGENDARY INC-"),

        # Value unset, updated when switched to tab.
        sg.Text("$", size=(9,1), key="-LEGENDARY X PRICE-", tooltip="0")
    ],
    [
        sg.Text("Mythic: ", size=(10, 1)), 
        sg.Text(f"{multipliers[1]}x", size=(5, 1), justification="right", key="-MYTHIC X VALUE-"), 
        sg.Button("+", key="-MYTHIC INC-"),

        sg.Text("$", size=(9,1) ,key="-MYTHIC X PRICE-", tooltip="0")
    ],
    [
        sg.Text("Godlike: ", size=(10, 1)), 
        sg.Text(f"{multipliers[2]}x", size=(5, 1), justification="right", key="-GODLIKE X VALUE-"), 
        sg.Button("+", key="-GODLIKE INC-"),

        sg.Text("$", size=(9,1), key="-GODLIKE X PRICE-", tooltip="0")
    ]
]

prestige_col = [
    [
        sg.Text("Requirements:", size=(10,1))
    ],
    [
        sg.Image(data=imgD.godlike_key_img, subsample=20),
        sg.Text("Godlike:", size=(13,1)),
        sg.Text("1x", justification="right", key="-PRESTIGE KEY REQUIREMENT-") 
    ],
    [
        sg.Image(data=imgD.chest_img, subsample=20),
        sg.Text("Chests opened:", size=(13,1)),
        sg.Text(f"{0}", justification="right", key="-TOTAL OPENED-")
    ],
    [
        sg.ProgressBar(100, orientation='h', size=(20, 10), key='-PROGRESS BAR-')
    ],
    [
        sg.Button("Prestige", disabled=True, button_color="black", key="-PRESTIGE-")
    ]
]


upgrades_col = [
    [
        sg.Text("Max buy limit:", size=(15, 1)), 
        sg.Text(f"{nf.sizeof_number(upgrade_value_buylimit())}", size=(6, 1), justification="right", key="-MAX BUY LIMIT VALUE-"), 
        sg.Button("+", key="-MAX BUY LIMIT INC-"),

        # Value unset, updated when switched to tab.
        sg.Text("$", size=(9,1), key="-MAX BUY LIMIT PRICE-", tooltip="0")
    ],
    [
        sg.Text("Max parallel open:", size=(15, 1)), 
        sg.Text(f"{upgrades["max_par_rolls"]}", size=(6, 1), justification="right", key="-MAX PAR ROLLS VALUE-"), 
        sg.Button("+", key="-MAX PAR ROLLS INC-"),

        sg.Text("$", size=(9,1) ,key="-MAX PAR ROLLS PRICE-", tooltip="0")
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
        sg.Column(upgrades_col)
    ]
]

prestige_progression_tab = [
    [
        sg.Column(prestige_col)
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
    # sg.Text("Upgrades:\n-Multi Prestige\n-Discount\n-Auto-opener robot\n-More AT/prestige")#
    [
        sg.Text("These are permanent upgrades!\n")
    ],
    [
        sg.Text("Extra Token/Prestige: ", size=(16, 1)), 
        sg.Text(f"{upgrades["extra_AT"]}", size=(4, 1), justification="right", key="-EXTRA TOKEN VALUE-"), 
        sg.Button("+", tooltip="+1", key="-EXTRA TOKEN INC-"),

        sg.Text("10x", size=(3,1), pad=((16, 0), 6), key="-EXTRA TOKEN PRICE-"),
        sg.Image(data=imgD.ascension_toke_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Multiplier discount: ", size=(16, 1)), 
        sg.Text(f"{upgrades["multiplier_discount"]}%", size=(4, 1), justification="right", key="-MULTIPLIER DISCOUNT VALUE-"), 
        sg.Button("+", tooltip="+1%", key="-MULTIPLIER DISCOUNT INC-"),

        sg.Text("5x", size=(3,1), pad=((15, 0), 6), key="-MULTIPLIER DISCOUNT PRICE-"),
        sg.Image(data=imgD.ascension_toke_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Upgrade discount: ", size=(16, 1)), 
        sg.Text(f"{upgrades["upgrade_discount"]}%", size=(4, 1), justification="right", key="-UPGRADE DISCOUNT VALUE-"), 
        sg.Button("+", tooltip="+1%", key="-UPGRADE DISCOUNT INC-"),

        sg.Text("10x", size=(3,1), pad=((15, 0), 6), key="-UPGRADE DISCOUNT PRICE-"),
        sg.Image(data=imgD.ascension_toke_img, subsample=20, pad=(0, 0))
    ],
    # [
    #     sg.Text("Multi-Prestige: ", size=(16, 1)), 
    #     sg.Text(f"N/A", size=(4, 1), justification="right", key="-VALUE-"), 
    #     sg.Button("+", key="-INC-"),

    #     sg.Text("???", size=(3,1), pad=((15, 0), 6), key="-PRICE-"),
    #     sg.Image(data=imgD.ascension_toke_img, subsample=20, pad=(0, 0))
    # ]
]

prestige2_tab = [
    [
        sg.Text("Exchange key / money")
    ]
]

prestige3_tab = [
    [
        sg.Text("Buy themes")
    ]
]

prestige6_tab = [
    [
        sg.Text("ASCENSION Token Chest")
    ]
]

prestige10_tab = [
    [
        sg.Text("10B max buy limit\n10 Max par open limit")
    ]
]

# Dynamically make a list of tabs, updates
def get_prestige_tabs(current_prestige):


    #! REVISE NUMBERS EITHER P1,P2,P3 or P 0,P I etc.
    
    prestige_tabs_info = {
        0: ["Prestige 0", prestige0_tab, current_prestige < 0],
        1: ["I", prestige1_tab, current_prestige < 1],
        2: ["II", prestige2_tab, current_prestige < 2],
        3: ["III", prestige3_tab, current_prestige < 3],
        6: ["VI", prestige6_tab, current_prestige < 6],
        10: ["X", prestige10_tab, current_prestige < 10]
    }
    prestige_tabs = []
    counter = 0
    for key in prestige_tabs_info:
        if (prestige_tabs_info[key][2]):
            prestige_tabs.append(sg.Tab(f"🔒",prestige_tabs_info[key][1], key=f"-P TAB-{key}-", disabled=True))
        else:
            prestige_tabs.append(sg.Tab(f"{prestige_tabs_info[key][0]}",prestige_tabs_info[key][1], key=f"-P TAB-{key}-", disabled=False))

       

    return prestige_tabs

# Change the state of any button, shorter script
def update_button(key, is_enabled):
    if is_enabled:
        window[key].update(button_color="white", disabled=False)
    else:
        window[key].update(button_color="black", disabled=True)


#########################################################
# ! Anytime inventory is touched, run this to update GUI
#########################################################
def update_inventory():
    window["-MONEY-"].update(f"Total money: {nf.sizeof_number(money,"$")}")
    window["-MONEY-"].set_tooltip(f"${money:,}")
    window["-PRESTIGE DISPLAY-"].update(f"Prestige: {roman.toRoman(prestige)}")


    window["-LEGENDARY KEY-"].update(f"{nf.sizeof_number(inventory[0])}")
    window["-MYTHIC KEY-"].update(f"{nf.sizeof_number(inventory[1])}")
    window["-GODLIKE KEY-"].update(f"{nf.sizeof_number(inventory[2])}")



    window["-ASCENSION TOKEN IMG-"].update(visible=prestige>0)
    window["-ASCENSION TOKEN TEXT-"].update(visible=prestige>0)
    window["-ASCENSION TOKEN-"].update(visible=prestige>0)
    window["-ASCENSION TOKEN-"].update(nf.sizeof_number(inventory[3]))


def update_multipliers():


    #? Fix display?
    # Need to take away 1 from the displayed value since it's used when rolling even at lvl 1 -
    # Eg.: with 9x it would get you 8/100 l keys since it's only 8x in reality. 
    # Keep the -1 for accurate display!

    window["-LEGENDARY X VALUE-"].update(f"{multipliers[0]-1}x")
    window["-LEGENDARY X PRICE-"].update(f"{nf.sizeof_number(multiplier_price("legendary"),"$")}")
    window["-LEGENDARY X PRICE-"].set_tooltip(f"${multiplier_price("legendary"):,}")

    window["-MYTHIC X VALUE-"].update(f"{multipliers[1]-1}x")
    window["-MYTHIC X PRICE-"].update(f"{nf.sizeof_number(multiplier_price("mythic"),"$")}")
    window["-MYTHIC X PRICE-"].set_tooltip(f"${multiplier_price("mythic"):,}")

    window["-GODLIKE X VALUE-"].update(f"{multipliers[2]-1}x")
    window["-GODLIKE X PRICE-"].update(f"{nf.sizeof_number(multiplier_price("godlike"),"$")}")
    window["-GODLIKE X PRICE-"].set_tooltip(f"${multiplier_price("godlike"):,}")


def update_upgrades():
    
    window["-MAX BUY LIMIT VALUE-"].update(f"{nf.sizeof_number(upgrade_value_buylimit())}")
    window["-MAX PAR ROLLS VALUE-"].update(f"{upgrades["max_par_rolls"]}")


    # Default max buy is 1 B, but can be increased to 10 B with ASCENSION token upgrades!
    if (upgrades["max_buy_limit_level"] >= 9 + upgrades["max_buy_limit_cap_increase"]):
        window["-MAX BUY LIMIT PRICE-"].update("MAX")
        window["-MAX BUY LIMIT PRICE-"].set_tooltip("MAX")
        update_button("-MAX BUY LIMIT INC-", False)
    else:
        window["-MAX BUY LIMIT PRICE-"].update(f"{nf.sizeof_number(upgrade_price("max_buy_limit"),"$")}")
        window["-MAX BUY LIMIT PRICE-"].set_tooltip(f"${upgrade_price("max_buy_limit"):,}")
        update_button("-MAX BUY LIMIT INC-", True)


    if (upgrades["max_par_rolls"] >= 5):

        window["-MAX PAR ROLLS PRICE-"].update("MAX")
        window["-MAX PAR ROLLS PRICE-"].set_tooltip("MAX")
        update_button("-MAX PAR ROLLS INC-", False)

    else:
        window["-MAX PAR ROLLS PRICE-"].update(f"{nf.sizeof_number(upgrade_price("max_par_rolls"),"$")}")
        window["-MAX PAR ROLLS PRICE-"].set_tooltip(f"${upgrade_price("max_par_rolls")}")
        update_button("-MAX PAR ROLLS INC-", True)

def update_prestige():

    # Each prestige +5% is needed to prestige
    # After prestige 10, it all increases to %15
    # BIG JUMP -> previously 9x5% but jumps to 10x15% added!!
    if (prestige < 10): 
        prestige_difficulty = 100 + (5*prestige)
    else:
        prestige_difficulty = 100 + (15*prestige)

    # Set up key requirements
    if (prestige < 10):
        key_requirement = 1*prestige
    elif (prestige < 25):
        key_requirement = 10*prestige
    else:
        key_requirement = 100*prestige

    current_open_goal = (1_000_000_000_000/100) * prestige_difficulty

    window["-TOTAL OPENED-"].update(f"{nf.sizeof_number(total_chest_opened)}/{nf.sizeof_number(current_open_goal)}")
    window["-PROGRESS BAR-"].update((total_chest_opened/current_open_goal)*100)

    window["-PRESTIGE KEY REQUIREMENT-"].update(f"{nf.sizeof_number(key_requirement)}x")

    # If has godlike key AND met requirements

    met_Requirement = inventory[2] >= key_requirement and total_chest_opened >= current_open_goal
    update_button("-PRESTIGE-", met_Requirement)
    

def update_prestige_tab(tab_name):
    match tab_name:
        case "I":

            # IF max level, disable.
        
            window["-EXTRA TOKEN VALUE-"].update(upgrades["extra_AT"])
            update_button("-EXTRA TOKEN INC-", upgrades["extra_AT"] < 10)
            
            
            window["-MULTIPLIER DISCOUNT VALUE-"].update(f"{upgrades["multiplier_discount"]}%")
            update_button("-MULTIPLIER DISCOUNT INC-", upgrades["multiplier_discount"] < 50)

            window["-UPGRADE DISCOUNT VALUE-"].update(f"{upgrades["upgrade_discount"]}%")
            update_button("-UPGRADE DISCOUNT INC-", upgrades["upgrade_discount"] < 50)
        

def update_roll_counter(change_by = 0):
    global currently_opening
    currently_opening += change_by

    window["-CURRENTLY ROLLING-"].update(f"{currently_opening}/{upgrades["max_par_rolls"]} chests opening")

        
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

    # Run the roll function from chest_roll.py  
    ''' 
    returns:
    0,       0-Legendary key
    0,       1-Mythic key
    0,       2-Godlike key
    [text]  -3 LOG TO ADD
    [0],    -2-money to void 
    0       -1-Money to add
    
    '''   
    roll_result = roll.roll(chest, options, chances, amount)  

    time.sleep(0.3)
    # Checks if legendary chest VOID was rolled, then applies it.
    if (roll_result[-2][0] > 0):
        for i in range(roll_result[-2][0]):
            money *= 0.99
            money = round(money)

    # Adds total money earned and the log message
    # * MONEY NEEDS TO BE IN PYTHON INT!!! roll_result = numpy int.
    previous_money = money
    money = previous_money + int(roll_result[-1])
    log_text.append(roll_result[-3])

    # Adds keys to inventory
    inventory = [inventory[i] + roll_result[i] for i in range(len(roll_result)-3)]

    # Update LOG GUI with message.
    window["-LOG-"].update(f"\n{log_text[-1][0]}", append=True, text_color_for_value=log_text[-1][1])


    # After rolling, reduce log size so it isn't too big, then update the GUI
    # Saves last 25 | if over 30 it will reset
    if(len(log_text) > 35):
        log_text = log_text[-25:]
        window['-LOG-'].update('')  # Clear the existing text

        for i in range(len(log_text)):
            line = log_text[i][0]
            color = log_text[i][1]

            window['-LOG-'].update(f"\n{line}", append=True, text_color_for_value=color)

    update_roll_counter(-1)
    do_autosave()
    update_inventory()
            

# --- LAYOUT COLUMNS --- #

top_column = [
    [
        sg.Column(info_col),
        sg.Push(),
        sg.Column(max_open_col)
    ]
]

left_column = [
    [
        sg.TabGroup([[sg.Tab("Inventory", inventory_tab ), sg.Tab("Multipliers", multiplier_tab),  sg.Tab("Upgrades", upgrades_tab), sg.Tab("Prestige", prestige_progression_tab)]], enable_events=True,key="-MENU TABS-")
    ]
]

right_column = [
    [
        # Def returns a list of active tabs
        sg.TabGroup([get_prestige_tabs(prestige)], enable_events=True, key="-PRESTIGE TABS-")
    ]
]



# --- WINDOW --- # 

#TODO: Add load save.
menu_def = [
    ["Settings", ["Save::-MANUAL SAVE-", "Load (coming soon)"]],
    ["Performance", ["Coming soon...", "Coming soon...."] ],
    ["Help",["Basic::-BASIC HELP-", "Prestige info::-PRESTIGE HELP-"]]
]

 #bar_background_color=sg.theme_background_color()
layout = [
    [
        sg.MenubarCustom(menu_def, pad=(0,0), bar_background_color=sg.theme_input_background_color())
    ],
    [
        top_column
    ],
    [
        sg.Column(left_column),
        sg.Column(right_column)
    ],
    [
        # * size=(w,h) w is set to 1, but expand_x is set to true, so only setting h in reality
        sg.Multiline(size=(1,10), autoscroll=True, expand_x=True ,key="-LOG-")
    ]
]

use_custom_titlebar=True

window = sg.Window("Chest Frenzy", layout, finalize=True)

while True:
    event, values = window.read()
    #print(event, values)
    if event == "Exit" or event == sg.WIN_CLOSED:
        #TODO: Add saving here
        do_autosave()
        break


    # -- SAVING -- #
    # When using find, it returns -1 if no substring is present
    if event.find("-MANUAL SAVE-") != -1:
        do_autosave()
        sg.popup("Game saved!")
    
    if event.find("-BASIC HELP-") != -1:
       popups.tutorial(version)
    
    if event.find("-PRESTIGE HELP-") != -1:
       popups.prestige_help()


    # -- TAB UPDATES -- #

    if values["-MENU TABS-"] == "Inventory":
        update_inventory()

    if values["-MENU TABS-"] == "Multipliers":
        update_multipliers()

    if values["-MENU TABS-"] == "Upgrades":
        update_upgrades()

    
    if values["-MENU TABS-"] == "Prestige":
        update_prestige()
        
    if values["-PRESTIGE TABS-"] != "-P TAB-0-":

        match values["-PRESTIGE TABS-"]:
            case "-P TAB-1-":
                update_prestige_tab("I")

            case "-P TAB-0-":
                update_prestige_tab("II")

    # -- UPGRADE BUTTONS
    if event == "-MAX BUY LIMIT INC-":
        price_of_upgrade = upgrade_price("max_buy_limit")

        if money >= price_of_upgrade:
            money -= price_of_upgrade
            upgrades["max_buy_limit_level"] +=1
            update_upgrades()
            update_inventory()
            do_autosave()

    
    if event == "-MAX PAR ROLLS INC-":
        price_of_upgrade = upgrade_price("max_par_rolls")

        if money >= price_of_upgrade:
            money -= price_of_upgrade
            upgrades["max_par_rolls"] +=1

            update_upgrades()
            update_roll_counter()
            update_inventory()
            do_autosave()

    # -- MULTIPLIER BUTTONS

    if event == "-LEGENDARY INC-":

        price_of_upgrade = multiplier_price("legendary")


        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[0] += 1
            update_multipliers()
            update_inventory()
            do_autosave()


    if event == "-MYTHIC INC-":

        price_of_upgrade = multiplier_price("mythic")

        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[1] += 1
            update_multipliers()
            update_inventory()
            do_autosave()
        
        
        
    if event == "-GODLIKE INC-":
          
        price_of_upgrade = multiplier_price("godlike")

        if money >= price_of_upgrade:
            money -= price_of_upgrade
            multipliers[2] += 1
            update_multipliers()
            update_inventory()
            do_autosave()
        
        
    # -- PRESTIGE 1 UPGRADES
    if event == "-EXTRA TOKEN INC-":

        price_str = window["-EXTRA TOKEN PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["extra_AT"] += 1
            
            update_prestige_tab("I")
            update_inventory()
            do_autosave()
    
    if event == "-MULTIPLIER DISCOUNT INC-":

        price_str = window["-MULTIPLIER DISCOUNT PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["multiplier_discount"] += 1
            
            update_prestige_tab("I")
            update_inventory()
            do_autosave()

    if event == "-UPGRADE DISCOUNT INC-":

        price_str = window["-UPGRADE DISCOUNT PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["upgrade_discount"] += 1
            
            update_prestige_tab("I")
            update_inventory()
            do_autosave()


    
    # -- CHEST BUTTONS

    if event == "-STARTER CHEST ROLL-":
        # Handle if it's a letter not int. No need for anything as second test will not roll if it's 0.
        try:
            roll_amount = int(values["-STARTER CHEST AMOUNT-"])
        except:
            window["-STARTER CHEST AMOUNT-"].update(0)

        if(currently_opening + 1 > upgrades["max_par_rolls"]):
            pass 
            # ! This means more are opening that able to, don't want to interupt gameplay buy bad practice!!!

        elif (roll_amount > 0 and money >= roll_amount*10):
            
            if (roll_amount <= upgrade_value_buylimit()):
                chest_options = np.array(["Common", "Uncommon","Rare","Epic","Legendary"])
                chest_chances = [41,30,20,8,1]
            
                money -= roll_amount*10
                total_chest_opened += roll_amount

                #roll_chest("STARTER",chest_options,chest_chances,roll_amount)
                threading.Thread(target=roll_chest, args=("STARTER",chest_options, adjust_weights(chest_options,chest_chances,"Legendary", multipliers[0]), roll_amount), daemon=True).start()

                update_roll_counter(1)
                update_inventory()
                do_autosave()
            else:
                sg.popup("Upgrade your max buy limit!")
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")



    if event == "-LEGENDARY CHEST ROLL-":
        # Same STR test here. ^^
        try:
            roll_amount = int(values["-LEGENDARY CHEST AMOUNT-"])
        except:
            window["-LEGENDARY CHEST AMOUNT-"].update(0)

        if(currently_opening + 1 > upgrades["max_par_rolls"]):
            pass 
            # ! This means more are opening that able to, don't want to interupt gameplay buy bad practice!!!


        elif (roll_amount > 0 and inventory[0] >= roll_amount):

            if (roll_amount <= upgrade_value_buylimit()):
                chest_options = np.array(["Common", "Rare", "Epic", "Mythic", "Secret", "Void"])
                chest_chances = [88.99989, 10, 1, 0.001, 0.0001, 0.00001]
                # 0.0001 = 1/1M
                # 0.00001 = 1/10M
                # 0.000001 = 1/100M
                inventory[0] -= roll_amount
                total_chest_opened += roll_amount
                #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                
                threading.Thread(target=roll_chest, args=("LEGENDARY",chest_options, adjust_weights(chest_options,chest_chances,"Mythic", multipliers[1]), roll_amount), daemon=True).start()

                update_roll_counter(1)
                update_inventory()
                do_autosave()

            else:
                sg.popup("Upgrade your max buy limit!")
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")

    if event == "-MYTHIC CHEST ROLL-":
        # Same STR test here. ^^
        try:
            roll_amount = int(values["-MYTHIC CHEST AMOUNT-"])
        except:
            window["-MYTHIC CHEST AMOUNT-"].update(0)

        if(currently_opening + 1 > upgrades["max_par_rolls"]):
            pass 
            # ! This means more are opening that able to, don't want to interupt gameplay buy bad practice!!!

        elif (roll_amount > 0 and inventory[1] >= roll_amount):
            
            if(roll_amount <= upgrade_value_buylimit()):
                chest_options = np.array(["Common", "Rare", "Epic", "Secret", "Godlike"])
                chest_chances = [89.89989, 10, 0.1, 0.0001, 0.00001]
                # 0.0001 = 1/1M
                # 0.00001 = 1/10M
                # 0.000001 = 1/100M
                inventory[1] -= roll_amount
                total_chest_opened += roll_amount
                #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                
                threading.Thread(target=roll_chest, args=("MYTHIC",chest_options, adjust_weights(chest_options,chest_chances,"Godlike", multipliers[2]), roll_amount), daemon=True).start()

                update_roll_counter(1)
                update_inventory()
                do_autosave()
            else:
                sg.popup("Upgrade your max buy limit!")
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")

    # - INFO

    if event == "-STARTER CHEST INFO-":
        popups.chest_info("Starter")


    if event == "-LEGENDARY CHEST INFO-":
        popups.chest_info("Legendary")

    if event == "-MYTHIC CHEST INFO-":
        popups.chest_info("Mythic")


    # -- REWARD BUTTONS

    if event == "-TIME REWARD-":
        money += 1
        update_inventory()

    if event == "-PRESTIGE-" and inventory[2] >= 1:

        #Confirmations
        confirmation =  sg.popup_yes_no("*WARNING*\nA prestige will reset everything!",  title="Prestige")
        
        if (confirmation == "Yes"):

            # Increase prestige variable, check if prestige tab exists
            # * Only set the buy limit and par rolls to default, the rest are AT permanent upgrades

            ascension_token_gained = 10+upgrades["extra_AT"]

            total_chest_opened = 0
            prestige +=1
            current_prestige_currency = inventory[3]
            inventory = [0,0,0,current_prestige_currency+ascension_token_gained]
            multipliers = [1,1,1]
            money = 1000
            # upgrades = {
            #     "max_buy_limit_level": 1,
            #     "max_buy_limit_cap_increase" : 0,
            #     "max_par_rolls": 1,
            #     "upgrade_discount": 0,
            #     "multiplier_discount": 0
            # }

            upgrades["max_buy_limit_level"] = 1
            upgrades["max_par_rolls"] = 1

            sg.popup(f"You've prestiged!\nPrestige: {prestige} ")
            
            temp_prestige_tab = f"-P TAB-{prestige}-" 
            
            if (temp_prestige_tab in window.AllKeysDict):
                window[temp_prestige_tab].update(f"{roman.toRoman(prestige)}", disabled=False)
            else:
                print("No prestige tab for this prestige!")
            
            # Bring back to show inventory - Hides the rewards tab updating, prevents multi prestige?
            window["-MENU TABS-"].Widget.select(0)

            update_roll_counter()
            do_autosave()
       
window.close()