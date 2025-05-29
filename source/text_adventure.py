import requests
import os
import json
import location as Loc

# Define the initial game state
default_game_state = {
    "location": "a dark forest",
    "inventory": ["lantern", "rusty key"],
    "current_loc_desc": "You are in a dark forest with a narrow path leading north and a cave entrance to the east."
}

def load_game_state():
    if os.path.exists('resources/game_state.json'):
        with open('resources/game_state.json', 'r') as f:
            return json.load(f)
    return default_game_state

# Function to send prompt to Gemma via Ollama

def get_llm_response(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "gemma3:12b-it-qat",  # Updated model name
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    
    try:
        result = response.json()
        if "response" in result:
            return result["response"]
        elif "message" in result:
            return result["message"]
        else:
            print("Unexpected response format:", result)
            return "The narrator is silent... Something went wrong."
    except Exception as e:
        print("Error parsing response:", e)
        return "The narrator is confused and cannot continue the story."

def clean_llm_json_response(response):
    # Remove triple backticks and optional 'json' label
    cleaned = response.strip().strip('`')
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()
    return cleaned

def save_game_state(game_state):
    with open('resources/game_state.json', 'w') as f:
        json.dump(game_state, f, indent=4)

# Function to generate prompt based on game state and player input
def generate_prompt(game_state, player_input):
    prompt = f"""You are the narrator of a text adventure game.
The player is carrying {', '.join(game_state['inventory'])}.

Current scene: {game_state['current_loc_desc']}

Player input: "{player_input}"

Please generate a json response for the Location in the following format. I need to convert this directly to a python dictionary,
so please don't deviate from this formatting:
Scene Description: A description of the current scene in reaction to the most recent player input.
description: A vivid description of the current location including what is in the surrounding area with a focus on interesting details to draw the player in
name: The name of the current location. This could be as simple as a vast desert or as specific as the actual name of a tavern.
inventory: As a list, the items currently in the player's inventory.
items: As an optionally null list, items in this location that the player could take (legally or illegally)
characters: As a list, the characters currently in this location.
north: Location directly to the North (if applicable)
south: Location directly to the South (if applicable)
west: Location directly to the West (if applicable)
east: Location directly to the East (if applicable)
up: Location directly vertical (if applicable)
down: Location directly beneath (if applicable)
parent: The parent location (i.e. if a tavern is in a city or a city is in a kingdom)
subs: As a list, any sub_locations"""
    return prompt

# Main game loop
def game_loop():
    game_state = load_game_state()
    print("\n" + game_state["current_loc_desc"])
    while True:
        player_input = input("What do you want to do?\n")

        if player_input.lower() in ["quit", "exit"]:
            print("Thanks for playing!")
            break

        prompt = generate_prompt(game_state, player_input)
        llm_response = clean_llm_json_response(get_llm_response(prompt))
        location_dict = json.loads(llm_response)
        location = Loc.Location.from_dict(location_dict)
        print(location)
        print()
        print(location_dict['Scene Description'])
        print()
        game_state["current_loc_desc"] = llm_response  # Update scene
        save_game_state(game_state)

if __name__ == "__main__":
    game_loop()

