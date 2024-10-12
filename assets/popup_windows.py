import PySimpleGUI as sg


def tutorial(version):

    # Show tutorial
    info = f'''
    Welcome to Chest Frenzy! V{version}
    -------------------------------
    This is a "cookie clicker" type game, but with chests!

    Your main objectives are to:
    1) earn money
    2) open chests 
    3) upgrade luck multipliers
    4) buy unlocks 
    5) prestige! 
    6) repeat!!!!

    ------
    You can always manually save by clicking "Save" found in settings. 
    - If you exit mid-roll, you won't get the rewards from said roll 

    The tabs on the right "I, II, III" etc are Prestige tabs.
    Certain prestiges you unlock have a reward tab, drastically changing the game!

    The parallel open ugprade allows multiple batches of chests to be opened simultaneously. 

    '''

    sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))
    
def prestige_help():
    # Show tutorial
    info = f'''
    Prestige information!
    -------------------------------
    With each prestige:
    1. Gain +10 Ascension Tokens 
    2. Gain +Amount of extra AT upgrade (eg.: 10 = +10 tokens)
    3. Increased prestige requirements:
        I. Increased "Total chest opened this prestige" requirement
        II. Increased Godlike key requirement
    
    After certain prestige limits, requirements increase drastically:
        - Prestige 10
        - Prestige 25

    Certain prestiges unlock "Prestige tabs" which can be seen on the right side.
    Not every prestige unlocks a tab. 

    Prestiges with rewards:
        - I
        - II
        - III
        - VI
        - X
        - XX
    
    Prestige upgrades bought using Ascension Tokens are permanent and save even after a prestige.
    

    '''

    sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

def chest_info(chest):
    match chest:
        case "Starter":
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

        case "Legendary":
            info = '''
            Legendary Chest: (No multipliers) 
            -------------------------------
            Common:\t\t\t88% = $10
            Rare:\t\t\t10% = $20
            Epic:\t\t\t 1% = 1x Legendary key
            Mythic:\t\t\t0.001% = 1x Mythic key
            VOID:\t\t\t 0.00001% = -1% of all money (1/10M)
            \n\n\n\n
            *SECRET*:\t\t\t 0.0001% = $10M (1/1M)
            '''
            sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

        case "Mythic":
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