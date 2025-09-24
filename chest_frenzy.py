# import PySimpleGUI as sg
import FreeSimpleGUI as sg
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


'''
IDEAS:
- Daily shop of items random.seed, use custom generator of random
- lower item chest prestige requirement to hook users
- prestige 10 upgrade: "Larger collection space"
--> Default 10
--> Max 30
--> 1 new = 2 AT
'''


def do_autosave():
    save_game.write_save(total_chest_opened,current_theme,owned_themes,multipliers,equipped_item, collection_data,inventory,prestige,money,upgrades,used_codes)


# * IMORTANT VARIABLES
version = 4.05
currently_opening = 0
daily_shop_items = ["Loading"]

    # Can use uuid to generate cooler id 
    #import uuid  # To generate unique IDs for each item
    #{"id": str(uuid.uuid4()), "rarity": 2, "name": "Fortune Cookie", "damage": 0.234, "display": "Golden ⭐ Fortune Cookie [0.234]"},
    #{"id": "21321seew", "rarity":2, "name":"Fortune Cookie", "float":0.324, "display": "Golden ⭐ Fortune Cookie [0.234]"},
# collection_data = [
#     {"id": "21321seew", "rarity":2, "name":"Fortune Cookie", "float":0.324, "display": "Golden ⭐ Fortune Cookie [0.234]"},
#     {"id": "49jdccea1", "rarity":2, "name":"Fortune Cookie", "float":0.934, "display": "Golden ⭐ Fortune Cookie [0.934]"},
#     {"id": "iwx334212", "rarity":2, "name":"Fortune Cookie", "float":0.234, "display": "Golden ⭐ Fortune Cookie [0.834]"},
# ]
# equipped_item = {"display":"None","id":"None"}  # Stores the currently equipped item (by ID)
def get_collection_list(raw_collection):
    """Creates a list of item display names (non-stacking)."""
    return [f"{item['display']} (ID: {item['id']})" for item in raw_collection]  # Shortened ID for UI


#! Make it save a theme in the save file, when loading in
#! It would check for equipped themes, to change you select
#! Then restart the game to apply 
#? Below are good looking themes
# sg.theme("Black")
# sg.theme("DarkTeal10")
# sg.theme("DarkAmber")
# sg.theme("DarkBlue9")
# sg.theme("DarkBlue")

if(os.path.isfile("saves/save1.json")):
    saved_data = save_game.read_save()

    total_chest_opened = saved_data["total_chest_opened"]
    current_theme = saved_data["theme"]
    owned_themes = saved_data["owned_themes"]
    multipliers = saved_data["multipliers"]
    equipped_item = saved_data["equipped_item"]
    collection_data = saved_data["collection_data"]
    inventory = saved_data["inventory"]
    prestige = saved_data["prestige"]
    money = saved_data["money"]
    upgrades = saved_data["upgrades"]
    used_codes = saved_data["used_codes"]
    
else:

    popups.tutorial(version)

    # * Player data setup
    total_chest_opened = 0
    current_theme = "DarkBlue"
    owned_themes = ["DarkBlue"]
    multipliers = [1,1,1]
    equipped_item = {"display":"None","id":"None", "name":"None"}
    #equipped_item = {"id": "21321seew", "rarity":2, "name":"Fortune Cookie", "float":0.324, "display": "Golden ⭐ Fortune Cookie [0.234]"}
    #{"id": "21321seew", "rarity":"Golden", "name":"Fortune Cookie", "float":1.0, "display": "Golden ⭐ Fortune Cookie [1.000]", "shop_bought": True},
    #{"id": "7921s5ew", "rarity":"Golden", "name":"X-Ray Goggles", "float":0.5, "display": "Golden X-Ray Goggles [0.5]", "shop_bought": True}
    collection_data = [
        
    ]
    inventory = [0,0,0,0]
    prestige = 0
    money = 1000
    upgrades = {
        "max_buy_limit_level": 1,
        "max_buy_limit_cap_increase" : 0,
        "max_par_rolls": 1,
        "upgrade_discount": 0,
        "multiplier_discount": 0,
        "extra_AT": 0,
        "starter_money_increase": 0,
        "collection_space_increase": 0,
        "vow_of_sacrifice" : False
    }
    used_codes = []

    do_autosave()





#1_000_000_000_000
# * IMPORTANT
sg.theme(current_theme)


# * Prices setup
# multiplier_price_legendary      = lambda: round(3.5**(2 * multipliers[0]))

exchange_rate_legendary = 35
exchange_rate_mythic = 100_000
exchange_rate_godlike = 25_000_000_000_000



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

def prestige_number(prestige_value):

    if prestige_value <= 4999:
        return(roman.toRoman(prestige_value))
    if prestige_value == 5000:
        return("MAX")
    return(f"MAX (+{prestige_value-5000})")

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

def item_multiplier_effect(chest, current_item):
    '''
        Tier 1
        ------
        1- Paper (money)
        2- Iron (keys)

        Tier 2
        ------
        3- Emerald (money)
        4- Ruby (keys)

        Tier 3
        ------
        5- Gold (money)
        6- Diamond (keys)
    '''

    
    #Since all have the same effects, if the chest rolles has a multi
    #Then it will do the calculations for it
    do_effect = False

    if chest == "STARTER" and current_item["name"] == "Fortune Cookie":
        print("BOOSTER FOR THIS CHEST")
        do_effect = True

    elif chest == "LEGENDARY" and current_item["name"] == "Metal Detector":
        print("BOOSTER FOR THIS CHEST")
        do_effect = True

    elif chest == "MYTHIC" and current_item["name"] == "X-Ray Goggles":
        print("BOOSTER FOR THIS CHEST")
        do_effect = True
        

    if do_effect:
        #! TECHNICALLY EACH IS +1 as base multiplier is 1x then 
        #! These are added onto it, eg.: 2x here means 3x in mathematically
        rarity_effects = {
            "Paper":["money", 2],
            "Iron":["key", 2],

            "Emerald":["money", 3], 
            "Ruby":["key", 3],

            "Golden":["money", 4], 
            "Diamond":["key", 4]
        }
        
        
        effects_returned = rarity_effects[current_item["rarity"]]

        #? If perfect float, then 2x effects so 2x -> 4x

        if current_item["float"] == 1.0:
            effects_returned[1] *= 2.0
        else:
            effects_returned[1] *= current_item["float"]

        # By default it's multiplied by 1 (no change, but needed to be adder here)
        effects_returned[1] += 1
        effects_returned[1] = round(effects_returned[1],3)

        # print(effects_returned)
        return(effects_returned)
    
    else:
        print("NO BOOSTER")
        return(["None","None"])
        


        

 
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
        sg.Text(f"Prestige: {prestige_number(prestige)}", key="-PRESTIGE DISPLAY-")
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
       sg.Image(data=imgD.ascension_token_img, subsample=20, visible=prestige>0, key="-ASCENSION TOKEN IMG-"),  
       sg.Text("Ascension Token: ", size=(15, 1), visible=prestige>0, key="-ASCENSION TOKEN TEXT-"), 
       sg.Text(f"{nf.sizeof_number(inventory[3])}", justification="right", visible=prestige>0 ,key="-ASCENSION TOKEN-")
    ]
]


multipliers_col = [
    [
        sg.Text("These upgrades increase the chance of key drops.")
    ],
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

collection_col = [
    [
        sg.Text(f"Equipped: {equipped_item["display"]}", key="-COLLECTION EQUIPPED-")
    ],
    [
        sg.Listbox(get_collection_list(collection_data), size=(40, 5), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key="-COLLECTION LB-")
    ],
    [
        sg.Button("Equip", key="-COLLECTION EQUIP-"), 
        sg.Button("Delete", key="-COLLECTION DELETE-"),
        sg.Text(f"{len(collection_data)}/{30+upgrades["collection_space_increase"]} total items", key="-COLLECTION COUNTER-")
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

collection_tab = [
    [
        sg.Column(collection_col)
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

        sg.Text("5x", size=(3,1), pad=((16, 0), 6), key="-EXTRA TOKEN PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Multiplier discount: ", size=(16, 1)), 
        sg.Text(f"{upgrades["multiplier_discount"]}%", size=(4, 1), justification="right", key="-MULTIPLIER DISCOUNT VALUE-"), 
        sg.Button("+", tooltip="+1%", key="-MULTIPLIER DISCOUNT INC-"),

        sg.Text("2x", size=(3,1), pad=((15, 0), 6), key="-MULTIPLIER DISCOUNT PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Upgrade discount: ", size=(16, 1)), 
        sg.Text(f"{upgrades["upgrade_discount"]}%", size=(4, 1), justification="right", key="-UPGRADE DISCOUNT VALUE-"), 
        sg.Button("+", tooltip="+1%", key="-UPGRADE DISCOUNT INC-"),

        sg.Text("5x", size=(3,1), pad=((15, 0), 6), key="-UPGRADE DISCOUNT PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    # [
    #     sg.Text("Multi-Prestige: ", size=(16, 1)), 
    #     sg.Text(f"N/A", size=(4, 1), justification="right", key="-VALUE-"), 
    #     sg.Button("+", key="-INC-"),

    #     sg.Text("???", size=(3,1), pad=((15, 0), 6), key="-PRICE-"),
    #     sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    # ]
]

prestige2_tab = [
    [
        sg.Text("Exchange key / money")
    ],
    [  
        sg.Image(data=imgD.legendary_key_img, subsample=20), sg.Text(f"--> {nf.sizeof_number(exchange_rate_legendary,"$")}", size=(12,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-EXCHANGE LEGENDARY AMOUNT-"), 
        sg.Button("Exchange", key="-EXCHANGE LEGENDARY-")
    ],
    [  
        sg.Image(data=imgD.mythic_key_img, subsample=20), sg.Text(f"--> {nf.sizeof_number(exchange_rate_mythic,"$")}", size=(12,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-EXCHANGE MYTHIC AMOUNT-"), 
        sg.Button("Exchange", key="-EXCHANGE MYTHIC-")
    ],
    [  
        sg.Image(data=imgD.godlike_key_img, subsample=20), sg.Text(f"--> {nf.sizeof_number(exchange_rate_godlike,"$")}", size=(12,1)),
        sg.Spin([i for i in range(10001)], size=(10, 1), key="-EXCHANGE GODLIKE AMOUNT-"), 
        sg.Button("Exchange", key="-EXCHANGE GODLIKE-")
    ]
]



# sg.theme("Black")
# sg.theme("DarkTeal10")
# sg.theme("DarkAmber")
# sg.theme("DarkBlue9")
# sg.theme("DarkBlue")

prestige3_tab = [
    [
        sg.Text("Buy themes ||"), 
        sg.Button("Reset", tooltip="Restart to apply", key="-THEME DEFAULT-"),
        sg.Text("|| Restart to apply theme"), 
    ],
    [
        sg.Text("DarkBlue9", size=(16, 1)), 
        sg.Button("Buy", size=(7,1), tooltip="Restart to apply", key="-THEME DARKBLUE9-"),

        sg.Text("5x", size=(3,1), pad=((15, 0), 6), key="-THEME DARKBLUE9 PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("DarkAmber", size=(16, 1)), 
        sg.Button("Buy", size=(7,1), tooltip="Restart to apply", key="-THEME DARKAMBER-"),

        sg.Text("5x", size=(3,1), pad=((15, 0), 6), key="-THEME DARKAMBER PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Black", size=(16, 1)), 
        sg.Button("Buy", size=(7,1), tooltip="Restart to apply", key="-THEME BLACK-"),

        sg.Text("5x", size=(3,1), pad=((15, 0), 6), key="-THEME BLACK PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
]

prestige6_tab = [
    [
        sg.Push(),
        sg.Button("?", tooltip="Information", size=(1,1), pad=(0,3), button_color="white on blue" , key="-ASCENSION CHEST INFO-"),
        sg.Text("Ascension chest", justification="center"),
        
        sg.Push()
    ],
    [   
        sg.Image(data=imgD.ascension_chest_img, subsample=8,expand_x=True ,pad=(0, 0)),
        
    ],
    [
        # sg.Push(),
        # sg.Text("5x", size=(2,1), pad=((0, 0), 6), key="-X PRICE-"),
        # sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0)),
        # sg.Push()
    ],
    [  
        sg.Push(),
        sg.Button("Buy", size=(9,1), pad=((0,3), 3), tooltip="1x Chest", key="-ASCENSION CHEST ROLL-"),

        sg.VSeparator(),
        sg.Text("5x", size=(2,1), pad=((0, 0), 6), key="-ASCENSION CHEST PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0)),
        sg.Push()
    ]
]


prestige8_tab = [
    [
        sg.Push(),
        sg.Button("?", tooltip="Information", size=(1,1), pad=(0,3), button_color="white on blue" , key="-ITEM CHEST INFO-"),
        sg.Text("Booster item chest", justification="center"),
        
        sg.Push()
    ],
    [   
        sg.Image(data=imgD.item_chest_img, subsample=8,expand_x=True ,pad=(0, 0)),
        
    ],
    [
        # sg.Push(),
        # sg.Text("5x", size=(2,1), pad=((0, 0), 6), key="-X PRICE-"),
        # sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0)),
        # sg.Push()
    ],
    [  
        sg.Push(),
        sg.Button("Buy", size=(9,1), pad=((0,3), 3), tooltip="1x Chest", key="-ITEM CHEST ROLL-"),

        sg.VSeparator(),
        sg.Text("1x", size=(2,1), pad=((0, 0), 6), key="-ITEM CHEST PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0)),
        sg.Push()
    ]
]




prestige10_tab = [
    # [
    #     sg.Text("10B max buy limit\n10 Max par open limit")
    # ],
    [
        sg.Text("Max buy limit level cap:", size=(17, 1)), 
        sg.Text(f"+{upgrades["max_buy_limit_cap_increase"]} lvl", size=(7, 1), justification="right", key="-BUY LIMIT CAP INCREASE VALUE-"), 
        sg.Button("+", tooltip="+1 level", key="-BUY LIMIT CAP INCREASE INC-"),

        sg.Text("100x", size=(4,1), pad=((15, 0), 6), key="-BUY LIMIT CAP INCREASE PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Starter money increase:", size=(17, 1)), 
        sg.Text(f"+{nf.sizeof_number(upgrades["starter_money_increase"], "$")}", size=(7, 1), justification="right", key="-STARTER MONEY INCREASE VALUE-"), 
        sg.Button("+", tooltip="+1K", key="-STARTER MONEY INCREASE INC-"),

        sg.Text("20x", size=(4,1), pad=((15, 0), 6), key="-STARTER MONEY INCREASE PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ],
    [
        sg.Text("Max collection size:", size=(17, 1)), 
        sg.Text(f"+{upgrades["collection_space_increase"]}", size=(7, 1), justification="right", key="-COLLECTION SPACE INCREASE VALUE-"), 
        sg.Button("+", tooltip="+10", key="-COLLECTION SPACE INCREASE INC-"),

        sg.Text("5x", size=(4,1), pad=((15, 0), 6), key="-COLLECTION SPACE INCREASE PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0))
    ]
]

prestige12_tab = [
    [
        sg.Text(f"Daily shop:")
    ],
    [
        sg.Listbox([], size=(40, 4), select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, key="-DAILY SHOP LB-")
    ],
    [
        sg.Button("Buy selected", key="-DAILY SHOP BUY-"),
        sg.VSeparator(),
        sg.Text("20x", size=(4,1), pad=((15, 0), 5), key="-DAILY SHOP PRICE-"),
        sg.Image(data=imgD.ascension_token_img, subsample=20, pad=(0, 0)), 
        
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
        8: ["VIII", prestige8_tab, current_prestige< 8],
        10: ["X", prestige10_tab, current_prestige < 10],
        12: ["XII", prestige12_tab, current_prestige < 12]
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
    window["-PRESTIGE DISPLAY-"].update(f"Prestige: {prestige_number(prestige)}")


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

def update_collection():
    window["-COLLECTION EQUIPPED-"].update(f"Equipped: {equipped_item["display"]}")
    window["-COLLECTION LB-"].update(get_collection_list(collection_data))
    window["-COLLECTION COUNTER-"].update(f"{len(collection_data)}/{30+upgrades["collection_space_increase"]} total items")

def update_prestige():

    # Each prestige +5% is needed to prestige
    # After prestige 10, it all increases to %15
    # BIG JUMP -> previously 9x5% but jumps to 10x15% added!!
    if (prestige < 10): 
        prestige_difficulty = 100 + (5*prestige)
    elif (prestige < 50):
        prestige_difficulty = 100 + (15*prestige)
    elif (prestige < 1000):
        prestige_difficulty = 100 + (200*prestige)
    else:
        prestige_difficulty = 100 + (500*prestige)

    # Set up key requirements
    if (prestige < 10):
        key_requirement = 1*prestige
    elif (prestige < 25):
        key_requirement = 10*prestige
    elif (prestige < 100):
        key_requirement = 50*prestige
    elif (prestige < 1000):
        key_requirement = 200*prestige
    else:
        key_requirement = 300*prestige

    current_open_goal = (1_000_000_000_000/100) * prestige_difficulty

    window["-TOTAL OPENED-"].update(f"{nf.sizeof_number(total_chest_opened)}/{nf.sizeof_number(current_open_goal)}")
    window["-PROGRESS BAR-"].update((total_chest_opened/current_open_goal)*100)

    window["-PRESTIGE KEY REQUIREMENT-"].update(f"x{nf.sizeof_number(key_requirement)}")

    # If has godlike key AND met requirements

    met_Requirement = inventory[2] >= key_requirement and total_chest_opened >= current_open_goal
    update_button("-PRESTIGE-", met_Requirement)
    

def update_prestige_tab(tab_name):

    global daily_shop_items

    match tab_name:
        case "I":

            # IF max level, disable.
        
            window["-EXTRA TOKEN VALUE-"].update(upgrades["extra_AT"])
            update_button("-EXTRA TOKEN INC-", upgrades["extra_AT"] < 20)
            
            
            window["-MULTIPLIER DISCOUNT VALUE-"].update(f"{upgrades["multiplier_discount"]}%")
            update_button("-MULTIPLIER DISCOUNT INC-", upgrades["multiplier_discount"] < 50)

            window["-UPGRADE DISCOUNT VALUE-"].update(f"{upgrades["upgrade_discount"]}%")
            update_button("-UPGRADE DISCOUNT INC-", upgrades["upgrade_discount"] < 50)
        
        case "III":
            if ("DarkBlue9" in owned_themes):
                window["-THEME DARKBLUE9-"].update("Equip")
                update_button("-THEME DARKBLUE9-", True)

                if (current_theme == "DarkBlue9"):
                    window["-THEME DARKBLUE9-"].update("Equipped")
                    update_button("-THEME DARKBLUE9-", False)

            if ("DarkAmber" in owned_themes):
                window["-THEME DARKAMBER-"].update("Equip")
                update_button("-THEME DARKAMBER-", True)

                if (current_theme == "DarkAmber"):
                    window["-THEME DARKAMBER-"].update("Equipped")
                    update_button("-THEME DARKAMBER-", False)

            if ("Black" in owned_themes):
                window["-THEME BLACK-"].update("Equip")
                update_button("-THEME BLACK-", True)

                if (current_theme == "Black"):
                    window["-THEME BLACK-"].update("Equipped")
                    update_button("-THEME BLACK-", False)
            
                
        
        case "VI":
            pass
            # NOTHING NEEDS UPDATING

        case "VIII":
            pass
            # NOTHING NEEDS UPDATING

        case "X":
            window["-BUY LIMIT CAP INCREASE VALUE-"].update(f"+{upgrades["max_buy_limit_cap_increase"]} lvl")
            update_button("-BUY LIMIT CAP INCREASE INC-", upgrades["max_buy_limit_cap_increase"] < 5)

            window["-STARTER MONEY INCREASE VALUE-"].update(f"+{nf.sizeof_number(upgrades["starter_money_increase"],"$")}")
            update_button("-STARTER MONEY INCREASE INC-", upgrades["starter_money_increase"] < 10000)

            window["-COLLECTION SPACE INCREASE VALUE-"].update(f"+{upgrades["collection_space_increase"]}")
            update_button("-COLLECTION SPACE INCREASE INC-", upgrades["collection_space_increase"] < 70)


        case "XII":

            # If not yet loaded, then load the items
            if daily_shop_items and daily_shop_items[0] == "Loading":

                weights=[1,15,35,49]
                floatChances = [i/100 for i in weights]

                weights=[30,50,20]
                itemChances = [i/100 for i in weights]

                weights=[39,39, 10,10 , 1, 1]
                rarityChances = [i/100 for i in weights]

                result = roll.item_chest_roll(floatChances, itemChances, rarityChances, True)


                #Re-write results
                #if not any --> any means if any are true 
                result = [
                    item for item in result  if not any(item["id"] == owned_items["id"] for owned_items in collection_data)
                ]
    
                if not result:
                    print("All daily items bought")
                    daily_shop_items = []

                else:
                    daily_shop_items = result
            
            #After checking if list already is loaded, just update display
            if daily_shop_items:
                update_button("-DAILY SHOP BUY-", True)
                window["-DAILY SHOP LB-"].update(get_collection_list(daily_shop_items))
            else:
                update_button("-DAILY SHOP BUY-", False)
                window["-DAILY SHOP LB-"].update(["All items bought. Come back tomorrow!"])

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
def roll_chest(chest, options, chances, amount, item_bonus=["None",1]):
    global upgrades
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

    hasVow = upgrades["vow_of_sacrifice"]
    roll_result = roll.roll(chest, options, chances, amount, item_bonus, hasVow)  

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
            
def chest_roll_items(floatChances, itemChances, rarityChances):
    global log_text
    global collection_data

    result = roll.item_chest_roll(floatChances, itemChances, rarityChances, False)

    item_rolled = result[0]

    window['-LOG-'].update(f"\n{result[1][0]}", append=True, text_color_for_value=result[1][1])

    collection_data.append(item_rolled)

    update_roll_counter(-1)
    do_autosave()
    update_inventory()
    update_collection()

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
        sg.TabGroup([[sg.Tab("Inventory", inventory_tab ), sg.Tab("Multipliers", multiplier_tab),  sg.Tab("Upgrades", upgrades_tab), sg.Tab("Collection", collection_tab), sg.Tab("Prestige", prestige_progression_tab)]], enable_events=True,key="-MENU TABS-")
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
    ["Help",["Basic::-BASIC HELP-", "Prestige info::-PRESTIGE HELP-", "Item info::-ITEM HELP-" ]],
    ["Extras",["Redeem codes::-REDEEM CODES-"]]
]

 #bar_background_color=sg.theme_background_color()
layout = [
    [
        sg.MenubarCustom(menu_def, pad=(0,0), bar_text_color=sg.theme_input_text_color() , bar_background_color=sg.theme_input_background_color())
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

#use_custom_titlebar=True
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

    if event.find("-ITEM HELP-") != -1:
        popups.item_help()

    if event.find("-REDEEM CODES-") != -1:
        
        result_of_code = popups.redeem_codes()
        if result_of_code == "Error":
            sg.popup("Error occured, try again later..")
        else:
            #print(result_of_code)

            if result_of_code["result"] == "found":
                if result_of_code["reward"][-1] not in used_codes:
                    used_codes.append(result_of_code["reward"][-1])
                    inventory = [inventory[i] + result_of_code["reward"][0][i] for i in range(len(inventory))]
                    
                    code_items = result_of_code["reward"][1]
                    if len(code_items) >= 1:
                        for item in code_items:
                            collection_data.append(item)


                    # RESULT MESSAGE:
                    msg = "You got:"

                    currency_rewards = result_of_code["reward"][0]
                    currency_names = ["Legendary keys", "Mythic keys", "Godlike keys", "Ascention tokens"]
                    item_rewards = result_of_code["reward"][1]


                    for count, name in zip(currency_rewards, currency_names):
                        if count > 0:
                            msg += f"\n- {count} {name}"

                    if item_rewards != []:
                        for item in item_rewards:
                            msg += f"\n- 1x {item["display"]}"

                    sg.popup(msg)
    
                    do_autosave()
                    update_inventory()
                    update_collection()
                else:
                    sg.popup("Code already redeemed.")
            else:
                    sg.popup("Code not found/expired..")



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

            case "-P TAB-3-":
                update_prestige_tab("III")

            case "-P TAB-6-":
                update_prestige_tab("VI")

            case "-P TAB-8-":
                update_prestige_tab("VIII") 

            case "-P TAB-10-":
                update_prestige_tab("X")

            case "-P TAB-12-":
                update_prestige_tab("XII")

    # -- COLLECTION BUTTONS
    if event == "-COLLECTION EQUIP-":
        selected_items = values["-COLLECTION LB-"]

        #If the list of selected items is not empty
        if selected_items:
            item_to_equip = selected_items[0]

            for item in collection_data:
                if item_to_equip.endswith(f"(ID: {item['id']})"):
                    equipped_item = item
                    print(equipped_item)
                    update_collection()

    if event == "-COLLECTION DELETE-":
        selected_items = values["-COLLECTION LB-"]

        confirmation =  sg.popup_yes_no("*WARNING*\nItems selected will be GONE FOREVER!",  title="Delete items")
        
        if (confirmation == "Yes"):
            #If the list of selected items is not empty
            if selected_items:
                items_to_delete = selected_items


                #IF the item deleted is equipped then reset to none
                for i in items_to_delete:

                    if i.endswith(f"(ID: {equipped_item["id"]})"):
                        equipped_item = {"display":"None","id":"None", "name":"None"}

                    for item in collection_data:
                        if i.endswith((f"(ID: {item['id']})")):
                            collection_data.remove(item)


                update_collection()
                do_autosave()



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



    if event == "-BUY LIMIT CAP INCREASE INC-":
        price_str = window["-BUY LIMIT CAP INCREASE PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["max_buy_limit_cap_increase"] += 1
            
            update_prestige_tab("X")
            update_upgrades()
            update_inventory()
            do_autosave()
    
    if event == "-STARTER MONEY INCREASE INC-":
        price_str = window["-STARTER MONEY INCREASE PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["starter_money_increase"] += 1000
            
            update_prestige_tab("X")
            update_inventory()
            do_autosave()


    if event == "-COLLECTION SPACE INCREASE INC-":
        price_str = window["-COLLECTION SPACE INCREASE PRICE-"].get()
        price_of_upgrade = int(price_str[:-1])

        if inventory[3] >= price_of_upgrade:
            inventory[3] -= price_of_upgrade
            upgrades["collection_space_increase"] += 10
            
            update_prestige_tab("X")
            update_collection()
            update_inventory()
            do_autosave()

    # -- EXCHANGE 

    if event == "-EXCHANGE LEGENDARY-":
        try:
            exchange_amount = int(values["-EXCHANGE LEGENDARY AMOUNT-"])
        except:
            window["-EXCHANGE LEGENDARY AMOUNT--"].update(0)
        
        if (inventory[0] >= exchange_amount):
            inventory[0] -= exchange_amount

            gained = exchange_rate_legendary * exchange_amount
            money += gained
            update_inventory()
            window['-LOG-'].update(f"\nYou've gained ${gained:,}", append=True, text_color_for_value="light gray")
        else:
            sg.popup("Error, not enough keys!", title="Error!")
    

    if event == "-EXCHANGE MYTHIC-":
        try:
            exchange_amount = int(values["-EXCHANGE MYTHIC AMOUNT-"])
        except:
            window["-EXCHANGE MYTHIC AMOUNT--"].update(0)
        
        if (inventory[1] >= exchange_amount):
            inventory[1] -= exchange_amount
            gained = exchange_rate_mythic * exchange_amount
            money += gained
            update_inventory()
            window['-LOG-'].update(f"\nYou've gained ${gained:,}", append=True, text_color_for_value="light gray")

        else:
            sg.popup("Error, not enough keys!", title="Error!")


    if event == "-EXCHANGE GODLIKE-":
        try:
            exchange_amount = int(values["-EXCHANGE GODLIKE AMOUNT-"])
        except:
            window["-EXCHANGE GODLIKE AMOUNT--"].update(0)
        
        if (inventory[2] >= exchange_amount):
            inventory[2] -= exchange_amount
            gained = exchange_rate_godlike * exchange_amount
            money += gained
            update_inventory()
            window['-LOG-'].update(f"\nYou've gained ${gained:,}", append=True, text_color_for_value="light gray")
        else:
            sg.popup("Error, not enough keys!", title="Error!")

    # -- THEME SELECT    

    if event == "-THEME DEFAULT-":
        current_theme = "DarkBlue"
        update_prestige_tab("III")
        do_autosave()

    if event == "-THEME DARKAMBER-":
        if window["-THEME DARKAMBER-"].ButtonText == "Buy":
            price_str = window["-THEME DARKAMBER PRICE-"].get()
            price_of_theme = int(price_str[:-1])
            if (inventory[3] >= price_of_theme):
                inventory[3] -= price_of_theme
                owned_themes.append("DarkAmber")

                update_prestige_tab("III")
                update_inventory()
                do_autosave()

        elif window["-THEME DARKAMBER-"].ButtonText == "Equip":
            current_theme = "DarkAmber"
            update_prestige_tab("III")
            do_autosave()

    if event == "-THEME BLACK-":
        if window["-THEME BLACK-"].ButtonText == "Buy":
            price_str = window["-THEME BLACK PRICE-"].get()
            price_of_theme = int(price_str[:-1])
            if (inventory[3] >= price_of_theme):
                inventory[3] -= price_of_theme
                owned_themes.append("Black")

                update_prestige_tab("III")
                update_inventory()
                do_autosave()

        elif window["-THEME BLACK-"].ButtonText == "Equip":
            current_theme = "Black"
            update_prestige_tab("III")
            do_autosave()
            
    if event == "-THEME DARKBLUE9-":
        if window["-THEME DARKBLUE9-"].ButtonText == "Buy":
            price_str = window["-THEME DARKBLUE9 PRICE-"].get()
            price_of_theme = int(price_str[:-1])
            if (inventory[3] >= price_of_theme):
                inventory[3] -= price_of_theme
                owned_themes.append("DarkBlue9")

                update_prestige_tab("III")
                update_inventory()
                do_autosave()

        elif window["-THEME DARKBLUE9-"].ButtonText == "Equip":
            current_theme = "DarkBlue9"
            update_prestige_tab("III")
            do_autosave()

    # -- DAILY ITEM SHOP
    if event == "-DAILY SHOP BUY-":
        price_str = window["-DAILY SHOP PRICE-"].get()
        price_of_item = int(price_str[:-1])
        if (inventory[3] >= price_of_item):
            inventory[3] -= price_of_item
            selected_items = values["-DAILY SHOP LB-"]

            if selected_items:
                item_to_buy = selected_items[0]
                for item in daily_shop_items:
                    if item_to_buy.endswith(f"(ID: {item['id']})"):
                        daily_shop_items.remove(item)
                        collection_data.append(item)
                # DOES NOT WORK- need the item stats/object - returns the string to display
                # collection_data.append(item_to_buy)

            do_autosave()
            update_prestige_tab("XII")
            update_inventory()
            update_collection()

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
                
                item_multiplier = item_multiplier_effect("STARTER", equipped_item)


                money -= roll_amount*10
                total_chest_opened += roll_amount

                #roll_chest("STARTER",chest_options,chest_chances,roll_amount)
                threading.Thread(target=roll_chest, args=("STARTER",chest_options, adjust_weights(chest_options,chest_chances,"Legendary", multipliers[0]), roll_amount, item_multiplier), daemon=True).start()

                update_roll_counter(1)
                update_prestige()
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

                item_multiplier = item_multiplier_effect("LEGENDARY", equipped_item)
                # 0.0001 = 1/1M
                # 0.00001 = 1/10M
                # 0.000001 = 1/100M
                inventory[0] -= roll_amount
                total_chest_opened += roll_amount
                #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                
                threading.Thread(target=roll_chest, args=("LEGENDARY",chest_options, adjust_weights(chest_options,chest_chances,"Mythic", multipliers[1]), roll_amount, item_multiplier), daemon=True).start()

                update_roll_counter(1)
                update_prestige()
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

                item_multiplier = item_multiplier_effect("MYTHIC", equipped_item)

                # 0.0001 = 1/1M
                # 0.00001 = 1/10M
                # 0.000001 = 1/100M
                inventory[1] -= roll_amount
                total_chest_opened += roll_amount
                #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                
                threading.Thread(target=roll_chest, args=("MYTHIC",chest_options, adjust_weights(chest_options,chest_chances,"Godlike", multipliers[2]), roll_amount, item_multiplier), daemon=True).start()

                update_roll_counter(1)
                update_prestige()
                update_inventory()
                do_autosave()
            else:
                sg.popup("Upgrade your max buy limit!")
        else:
            sg.popup("Insufficient funds or invalid roll amount!",title="Error!")


    if event == "-ASCENSION CHEST ROLL-":
        # Same STR test here. ^^
        
        roll_amount = 1
        price_str = window["-ASCENSION CHEST PRICE-"].get()
        price_of_roll = int(price_str[:-1])


        if(currently_opening + 1 > upgrades["max_par_rolls"]):
            pass 
            # ! This means more are opening that able to, don't want to interupt gameplay buy bad practice!!!

        elif (inventory[3] >= price_of_roll):
            
            if(roll_amount <= upgrade_value_buylimit()):
                chest_options = np.array(["Common", "Rare", "Very rare", "Epic", "JACKPOT"])
                chest_chances = [54, 30, 10, 5, 1]
                # 0.0001 = 1/1M
                # 0.00001 = 1/10M
                # 0.000001 = 1/100M
                inventory[3] -= price_of_roll
                total_chest_opened += 1
                #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                
                threading.Thread(target=roll_chest, args=("ASCENSION",chest_options, adjust_weights(chest_options,chest_chances, "JACKPOT", 1), roll_amount), daemon=True).start()

                update_roll_counter(1)
                update_prestige()
                update_inventory()
                do_autosave()
            else:
                sg.popup("Upgrade your max buy limit!")
        else:
            sg.popup("Insufficient funds!",title="Error!")
    
    if event == "-ITEM CHEST ROLL-":
        #Same STR test here. ^^
        
        roll_amount = 1
        price_str = window["-ITEM CHEST PRICE-"].get()
        price_of_roll = int(price_str[:-1])


        if(currently_opening + 1 > upgrades["max_par_rolls"]):
            pass 
            # ! This means more are opening that able to, don't want to interupt gameplay buy bad practice!!!

        elif (inventory[3] >= price_of_roll):
            if(len(collection_data) < 30+upgrades["collection_space_increase"]):
                if(roll_amount <= upgrade_value_buylimit()):
                    weights=[1,15,35,49]
                    floatChances = [i/100 for i in weights]

                    weights=[30,50,20]
                    itemChances = [i/100 for i in weights]

                    weights=[39,39, 10,10 , 1, 1]
                    rarityChances = [i/100 for i in weights]


                    inventory[3] -= price_of_roll
                    total_chest_opened += 1
                    #roll_chest("LEGENDARY",chest_options,chest_chances,roll_amount)
                    
                    threading.Thread(target=chest_roll_items, args=(floatChances, itemChances, rarityChances), daemon=True).start()

                    update_roll_counter(1)
                    update_prestige()
                    update_inventory()
                    do_autosave()
                else:
                    sg.popup("Upgrade your max buy limit!")
            else:
                    sg.popup("You have a full collection.",title="You need an upgrade!")
        else:
            sg.popup("Insufficient funds!",title="Error!")
    # - INFO

    if event == "-STARTER CHEST INFO-":
        popups.chest_info("Starter")


    if event == "-LEGENDARY CHEST INFO-":
        popups.chest_info("Legendary")

    if event == "-MYTHIC CHEST INFO-":
        popups.chest_info("Mythic")

    if event == "-ASCENSION CHEST INFO-":
        popups.chest_info("Ascension")


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
            money = 1000 + upgrades["starter_money_increase"]
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
                window[temp_prestige_tab].update(f"{prestige_number(prestige)}", disabled=False)
            else:
                print("No prestige tab for this prestige!")
            
            # Bring back to show inventory - Hides the rewards tab updating, prevents multi prestige?
            window["-MENU TABS-"].Widget.select(0)

            update_roll_counter()
            do_autosave()
       
window.close()