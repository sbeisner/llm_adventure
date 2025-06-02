import requests
import os
import json

#Import custom models
from model.location import Location
from model.player import Player
from model.scene import Scene

# Define the initial game state
default_game_state = {
    "map": [],  # List of locations (each stored as a dictionary)
    "player": {
        "current_location": "a dark forest",
        "inventory": ["lantern", "rusty key"]
    },
    "current scene": {
        "description": "You are in a dark forest with a narrow path leading north and a cave entrance to the east."
    }
}

game_state_path = 'resources/game_state.json'

def load_game_state():
    if os.path.exists(game_state_path):
        with open(game_state_path, 'r') as f:
            return json.load(f)
    else:
        # Ensure the directory exists.
        os.makedirs(os.path.dirname(game_state_path), exist_ok=True)
        save_game_state(default_game_state)
        return default_game_state


def save_game_state(game_state):
    """Persist the game state to file."""
    with open(game_state_path, 'w') as f:
        json.dump(game_state, f, indent=4)

def update_map(location):
    # Load the current game state
    with open(game_state_path, 'r') as f:
        game_state = json.load(f)

    # Check if the location already exists in the map
    location_exists = False
    for i, loc in enumerate(game_state.get('map', [])):
        if loc['name'] == location.name:
            game_state['map'][i] = location.to_dict()
            location_exists = True
            break
    game_state['player']['current_location'] = location.name
    # If the location does not exist, add it to the map
    if not location_exists:
        game_state.setdefault('map',[]).append(location.to_dict())

    save_game_state(game_state)

def update_player(new_player):
    # Load the current game state
    with open(game_state_path, 'r') as f:
        game_state = json.load(f)
    game_state['player'] = new_player.to_dict()
    save_game_state(game_state)

def update_scene(new_scene, game_state):
    """Update the scene section of the game state."""
    game_state["current scene"] = new_scene.to_dict()
    save_game_state(game_state)

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

# Function to generate prompt based on game state and player input
def generate_prompt(game_state, player_input, prompt_format):
    
    current_location = None
    for loc in game_state.get('map', []):
        if loc['name'] == game_state['current scene']['location']:
            current_location = loc
            break
    # If no location was found, generate a new one.
    if not current_location:
        current_location = Location(name=game_state['current scene']['location']).to_dict()

    prompt = f"""You are the narrator of a text adventure game.
The player is carrying {', '.join(game_state['player']['inventory'])}.
Current Location: {current_location}
Current scene: {game_state['current scene']['description']}

Player input: "{player_input}"

{prompt_format}
"""
    return prompt

# ------------------------------------------------------------------------------
# "Node" Functions (Modular Units of Pipeline Logic)
# ------------------------------------------------------------------------------
def build_location_prompt_node(game_state, player_input):
    """Generate the prompt for a location update using Location.loc_prompt."""
    return generate_prompt(game_state, player_input, Location.loc_prompt)


def llm_response_node(prompt):
    """Get and clean the LLM response given a prompt."""
    response = get_llm_response(prompt)
    return clean_llm_json_response(response)


def update_location_state_node(game_state, llm_response):
    """Convert LLM response into a Location object and update the game map."""
    try:
        location_dict = json.loads(llm_response)
    except Exception as e:
        print("Error decoding location JSON:", e)
        return None
    location = Location.from_dict(location_dict)
    update_map(location)
    # Update in-memory state
    game_state['player']['current_location'] = location.name
    return location


def build_player_prompt_node(game_state, player_input):
    """Generate the prompt for a player update using Player.player_prompt."""
    return generate_prompt(game_state, player_input, Player.player_prompt)


def update_player_state_node(game_state, llm_response):
    """Convert LLM response into a Player object and update the game state."""
    try:
        player_dict = json.loads(llm_response)
    except Exception as e:
        print("Error decoding player JSON:", e)
        return None
    player = Player.from_dict(player_dict)
    update_player(player)
    return player

def build_scene_prompt_node(game_state, player_input):
    """Generate the prompt for a scene update using Scene.scene_prompt."""
    return generate_prompt(game_state, player_input, Scene.scene_prompt)


def update_scene_state_node(game_state, llm_response):
    """Convert LLM response into a Scene object and update the current scene."""
    try:
        scene_dict = json.loads(llm_response)
    except Exception as e:
        print("Error decoding scene JSON:", e)
        return None
    print(scene_dict)
    scene = Scene.from_dict(cls=Scene,data=scene_dict)
    update_scene(scene, game_state)
    return scene

# ------------------------------------------------------------------------------
# Build a Simple Pipeline Graph as a Dictionary Mapping Node Names to Functions
# ------------------------------------------------------------------------------
graph = {
    "build_loc_prompt": build_location_prompt_node,
    "llm_loc_response": llm_response_node,
    "update_loc_state": update_location_state_node,
    "build_player_prompt": build_player_prompt_node,
    "llm_player_response": llm_response_node,  # Reusing the same LLM response function.
    "update_player_state": update_player_state_node,
    "build_scene_prompt": build_scene_prompt_node,
    "llm_scene_response": llm_response_node,    # Reusing the same LLM response function.
    "update_scene_state": update_scene_state_node,
}

# ------------------------------------------------------------------------------
# Main Game Loop
# ------------------------------------------------------------------------------
def game_loop():
    game_state = load_game_state()
    print(game_state["current scene"]["description"])
    
    while True:
        player_input = input("\nWhat do you want to do?\n> ")
        if player_input.lower() in ["quit", "exit"]:
            print("Thanks for playing!")
            break

        # Process the location update pipeline.
        loc_prompt = graph["build_loc_prompt"](game_state, player_input)
        llm_response_loc = graph["llm_loc_response"](loc_prompt)
        location = graph["update_loc_state"](game_state, llm_response_loc)
        if location:
            print("\n[Location Update]")
            print(location)
        else:
            print("Failed to update location.")

        # Process the player update pipeline.
        player_prompt = graph["build_player_prompt"](game_state, player_input)
        llm_response_player = graph["llm_player_response"](player_prompt)
        player = graph["update_player_state"](game_state, llm_response_player)
        if player:
            print("\n[Player Update]")
            print("Inventory: " + ", ".join(player.inventory))
        else:
            print("Failed to update player state.")

        # Process the scene update pipeline.
        scene_prompt = graph["build_scene_prompt"](game_state, player_input)
        llm_scene_response = graph["llm_scene_response"](scene_prompt)
        scene = graph["update_scene_state"](game_state, llm_scene_response)
        if scene:
            print("\n[Scene Update]")
            print(scene.description)
        else:
            print("Failed to update scene.")

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    game_loop()