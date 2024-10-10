import json
import numpy as np
 
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        # Add more custom conversions if needed
        return super(NumpyEncoder, self).default(obj)

def write_save(total_chest_opened_value,multipliers_value,inventory_value,prestige_value,money_value, upgrades_value):
 
    # Data to be written
    data = {
        "total_chest_opened": total_chest_opened_value,
        "multipliers": multipliers_value,
        "inventory": inventory_value,
        "prestige": prestige_value,
        "money": money_value,
        "upgrades": upgrades_value
    }
 
    # Serializing json
    json_object = json.dumps(data, indent=4, cls=NumpyEncoder)
    
    # Writing to sample.json
    with open("saves/save1.json", "w") as outfile:
        outfile.write(json_object)


def read_save():
    # Opening JSON file
    with open('saves/save1.json', 'r') as openfile:
    
        # Reading from json file
        data = json.load(openfile)
    
    return(data)