import requests
import os
import json
from model.location import Location
from model.player import Player
# Define the initial game state
default_game_state = {
    "location": "a dark forest",
    "inventory": ["lantern", "rusty key"],
    "current_loc_desc": "You are in a dark forest with a narrow path leading north and a cave entrance to the east."
}
game_state_path = 'resources/game_state.json'

def load_game_state():
    if os.path.exists(game_state_path):
        with open(game_state_path, 'r') as f:
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
    cleaned = cleaned.replace('None','null')
    return cleaned

def save_game_state(game_state):
    with open(game_state_path, 'w') as f:
        json.dump(game_state, f, indent=4)

def update_map(location):
    # Load the current game state
    with open(game_state_path, 'r') as f:
        game_state = json.load(f)

    # Check if the location already exists in the map
    location_exists = False
    for i, loc in enumerate(game_state['map']):
        if loc['name'] == location.name:
            game_state['map'][i] = location.to_dict()
            location_exists = True
            break
    game_state['player']['current_location'] = location.name
    # If the location does not exist, add it to the map
    if not location_exists:
        game_state['map'].append(location.to_dict())

    # Save the updated game state back to the file
    with open(game_state_path, 'w') as f:
        json.dump(game_state, f, indent=4)

def update_player(new_player):
    # Load the current game state
    with open(game_state_path, 'r') as f:
        game_state = json.load(f)

    # Replace the 'player' section with the new Player object's dictionary
    game_state['player'] = new_player.to_dict()

    # Save the updated game state back to the file
    with open(game_state_path, 'w') as f:
        json.dump(game_state, f, indent=4)


# Function to generate prompt based on game state and player input
def generate_prompt(game_state, player_input, prompt_format):
   # print(game_state)
    current_location = [game_state['map'][i]
                    if game_state['map'][i]['name'] == game_state['player']['current_location']
                    else Location(name=game_state['player']['current_location'])
                    for i in range(len(game_state['map']))
                    ]
    prompt = f"""You are the narrator of a text adventure game.
The player is carrying {', '.join(game_state['player']['inventory'])}.
Current Location: {current_location}
Current scene: {game_state['current scene']['description']}

Player input: "{player_input}"

{prompt_format}
"""
    return prompt

# Main game loop
def game_loop():
    game_state = load_game_state()
    print(game_state["current scene"]["description"])
    while True:
        player_input = input("What do you want to do?\n")

        if player_input.lower() in ["quit", "exit"]:
            print("Thanks for playing!")
            break

        loc_prompt = generate_prompt(game_state, player_input, Location.loc_prompt)
        llm_response_loc = clean_llm_json_response(get_llm_response(loc_prompt))
        location_dict = json.loads(llm_response_loc)
        location = Location.from_dict(location_dict)
        print(location)
        update_map(location)

        player_prompt = generate_prompt(game_state, player_input, Player.player_prompt)
        llm_response_player = clean_llm_json_response(get_llm_response(player_prompt))
        player_dict = json.loads(llm_response_player)
        player = Player.from_dict(player_dict)
        print('Inventory: ' + player.inventory)
        update_player(player)

if __name__ == "__main__":
    game_loop()

