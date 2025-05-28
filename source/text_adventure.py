import requests
import os
import json

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


def save_game_state(game_state):
    with open('resources/game_state.json', 'w') as f:
        json.dump(game_state, f, indent=4)

# Function to generate prompt based on game state and player input
def generate_prompt(game_state, player_input):
    prompt = f"""You are the narrator of a fantasy text adventure game.
The player is currently {game_state['location']}.
They are carrying {', '.join(game_state['inventory'])}.

Current scene: {game_state['current_loc_desc']}

Player input: "{player_input}"

Describe what happens next in vivid detail, including any challenges or discoveries."""
    return prompt

# Main game loop
def game_loop():
    game_state = load_game_state()
    while True:
        print("\n" + game_state["current_loc_desc"])
        player_input = input("What do you want to do?\n")

        if player_input.lower() in ["quit", "exit"]:
            print("Thanks for playing!")
            break

        prompt = generate_prompt(game_state, player_input)
        llm_response = get_llm_response(prompt)

        print("\n" + llm_response)
        game_state["current_loc_desc"] = llm_response  # Update scene
        save_game_state(game_state)

if __name__ == "__main__":
    game_loop()

