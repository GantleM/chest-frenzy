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
        - VIII
        - X
        - XX
    
    Prestige upgrades bought using Ascension Tokens are permanent and save even after a prestige.
    

    '''

    sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

def item_help():

    info = f'''
    Item information!
    -------------------------------
    Each item has 3 modifiers on them. 
    eg.: Golden Fortune Cookie [0.5]

    Golden: effect
    Fortune Cookie: What chest/action it is used at
    [0.5]: Float number, how effective the effect is.

    Below are all the effects you can get:

    Tier 1
    ------
    1- Paper (money) (2x multiplier)
    2- Metal (keys)  (2x multiplier)

    Tier 2
    ------
    3- Emerald (money)(3x multiplier)
    4- Ruby (keys)    (3x multiplier)

    Tier 3
    ------
    5- Gold (money)   (4x multiplier)
    6- Diamond (keys) (4x multiplier)

    The following relate to each chest/action:

    Fortune Cookie - Starter chest
    Metal Detector - Legendary chest
    X-Ray Goggles - Mythic chest

    --------------
    The float then determines how effective the multiplier is.
    A golden fortune cookie [0.5] gives the following effect:

    - Increases money gain
    - 1x multiplier (2*0.5 = 1)
    - Applies only for starter chest
    ---------------

    A perfect float [1.0] gives 2x effects:

    eg.: 2x multiplier with perfect float => 4x


    '''


    sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

def chest_info(chest):
    match chest:
        case "Starter":
            info = '''
            Starter Chest: (Stats shown with no multipliers) 
            Affected by: Fortune Cookie
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
            Legendary Chest: (Stats shown with no multipliers) 
            Affected by: Metal Detector
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
            Mythic Chest: (Stats shown with no multipliers) 
            Affected by: X-Ray Goggles
            -------------------------------
            Common:\t\t\t90% = $1K
            Rare:\t\t\t10% = $1.5K
            Epic:\t\t\t 1% = $3K
            Godlike:\t\t\t 0.00001% = 1x Godlike key (1/10M)
            \n\n\n\n
            *SECRET*:\t\t\t 0.0001% = $1T (1/1M)
            '''

            sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))

        case "Ascension":
            # ["Common", "Rare", "Very rare", "Epic", "JACKPOT"]
            # [54, 30, 10, 5, 1]
            info = '''
            Ascension Chest: (Stats shown with no multipliers) 
            -------------------------------
            Common:\t\t\t54% = $10K
            Rare:\t\t\t30% = $15K
            Very rare:\t\t\t 10% = $25K
            Epic:\t\t\t 5% = $100k
            JACKPOT:\t\t\t 1% = $1M
            '''

            sg.popup_scrolled(info, title="Information", font=("Arial Bold", 11), size=(60,10))