import json
import uuid
import os

def set_username(username):
    if username and username.strip():
        print(f"Setting username to {username}")
        # Create a Json file for the user
        import json
        import uuid
        import os

        # Generate unique ID
        user_id = str(uuid.uuid4())
        
        # Create user data dictionary
        user_data = {
            "user_id": user_id,
            "username": username.strip()
        }

        # Ensure directory exists
        os.makedirs("db", exist_ok=True)

        # Create a directory for the user
        os.makedirs(f"db/users/", exist_ok=True)
        
        # Save to JSON file
        filename = f"db/users/{user_id}.json"
        with open(filename, "w") as f:
            json.dump(user_data, f, indent=4)
        return True, user_id
    else:
        return False, ""

def set_value(user_id, value, key):
    # Get the user data
    filename = f"db/users/{user_id}.json"
    with open(filename, "r") as f:
        user_data = json.load(f)
    # Add the score to the user data
    user_data[key] = value
    # Save the user data back to the file
    with open(filename, "w") as f:
        json.dump(user_data, f, indent=4)

def get_clothing_items():
    filename = f"db/clothing/items.json"
    with open(filename, "r") as f:
        clothing_items = json.load(f)
    return clothing_items