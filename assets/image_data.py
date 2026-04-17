import pybase64
import os

def getBase64(img):
    with open(img, "rb") as img_file:
        my_string = pybase64.b64encode(img_file.read()).decode('utf-8')
    return my_string

base = os.path.join("assets", "images")

legendary_key_img    = getBase64(os.path.join(base, "legendary_key.png"))
mythic_key_img       = getBase64(os.path.join(base, "mythic_key.png"))
godlike_key_img      = getBase64(os.path.join(base, "godlike_key.png"))
ascension_token_img  = getBase64(os.path.join(base, "ascension_token.png"))
chest_img            = getBase64(os.path.join(base, "chest.png"))
item_chest_img       = getBase64(os.path.join(base, "item_chest.png"))
ascension_chest_img  = getBase64(os.path.join(base, "ascension_chest.png"))
devil_img            = getBase64(os.path.join(base, "devil.png"))
