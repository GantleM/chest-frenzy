import pybase64
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def getBase64(img):
    img = resource_path(img)
    # Open the image file in binary mode
    with open(img, "rb") as img_file:
        # Read the file's binary content and encode it in base64
        my_string = pybase64.b64encode(img_file.read()).decode('utf-8')
    return my_string

# Call the function for the image
legendary_key_img = getBase64("assets\\images\\legendary_key.png")
mythic_key_img = getBase64("assets\\images\\mythic_key.png")
godlike_key_img = getBase64("assets\\images\\godlike_key.png")
ascension_token_img = getBase64("assets\\images\\ascension_token.png")
chest_img = getBase64("assets\\images\\chest.png")
item_chest_img = getBase64("assets\\images\\item_chest.png")
ascension_chest_img = getBase64("assets\\images\\ascension_chest.png")
# save_img = getBase64("assets\\images\\save.png")