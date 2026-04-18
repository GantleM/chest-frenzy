import json
import numpy as np
import hashlib
import os

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        # Add more custom conversions if needed
        return super(NumpyEncoder, self).default(obj)


# Function to compute the hash for the data
def generate_hash(data):
    serialized_data = json.dumps(data, cls=NumpyEncoder)
    return hashlib.sha256(serialized_data.encode()).hexdigest()

#! Save version handling
current_save_version = 2

def migrate_v1_to_v2(data):
    data["upgrades"]["exchange_rate_increase"] = 1
    return data

migrations = {
    1: migrate_v1_to_v2
}


def write_save(total_chest_opened_value,current_theme_value,owned_themes_value,multipliers_value,equipped_item_value, collection_data_value, inventory_value,prestige_value,money_value, upgrades_value, used_codes_value):
 
    # Data to be written
    data = {
        "total_chest_opened": total_chest_opened_value,
        "theme":current_theme_value,
        "owned_themes": owned_themes_value,
        "multipliers": multipliers_value,
        "equipped_item": equipped_item_value,
        "collection_data": collection_data_value,
        "inventory": inventory_value,
        "prestige": prestige_value,
        "money": money_value,
        "upgrades": upgrades_value,
        "used_codes": used_codes_value
    }
 
    # Serializing json
    data_hash = generate_hash(data)

    save_content = {
        "version": current_save_version,
        "data": data,
        "hash": data_hash
    }

    json_object = json.dumps(save_content, indent=4, cls=NumpyEncoder)

    os.makedirs("saves", exist_ok=True)
    # Writing to sample.json
    with open("saves/save1.json", "w") as outfile:
        outfile.write(json_object)


def migrate_save(save):
    version = save.get("version", 1)
    data = save["data"]

    while version < current_save_version:
        if version in migrations:
            print(f"Migrating save v{version} → v{version+1}")
            data = migrations[version](data)
            version += 1
        else:
            raise Exception(f"No migration path for version {version}")

    save["version"] = current_save_version
    save["data"] = data
    save["hash"] = generate_hash(data)
    return save


def read_save():
    # Opening JSON file
    with open('saves/save1.json', 'r') as openfile:
        # Reading from json file
        save_content = json.load(openfile)
    
     # Run migrations if needed
    if save_content.get("version", 1) < current_save_version:
        save_content = migrate_save(save_content)
       
        # Write updated save back to disk
        with open("saves/save1.json", "w") as outfile:
            json.dump(save_content, outfile, indent=4, cls=NumpyEncoder)

    # print(save_content)
    data = save_content["data"]
    stored_hash = save_content["hash"]

    if data and stored_hash:
        computed_hash = generate_hash(data)
        if computed_hash == stored_hash:
            print("Data verified.")
            return(data)
        else:
            #os.remove("saves/save1.json")
            print("Game file corrupted!")
            
    #! REMOVE WHEN GAME COMES OUT!!!!!!!!
    #! LINE BELOW ALLOWS IT TO CONTINUE!
    return(data)
