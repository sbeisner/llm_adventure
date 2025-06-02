class Scene:
    scene_prompt = '''You are helping to narrate a fantasy text adventure game.
                    Please generate a json response for the Scene that plays out based on the character's input in the following format.
                    I need to convert this directly to a python dictionary,
                    so please don't deviate from this formatting. Additionally, consider whether the player has any
                    current restrictions before allowing them to do something. As an example, if the player says
                    "I stab them with my sword", consider whether the player actually has a sword in their inventory.:
                    location: The name of the location where the player currently is
                    description: A description of the scene that plays out as a consequence of the player's actions.
                    characters: As an optionally empty list, whatever NPCs there are in the scene.
                    heat: A rating from 0-10, 10 being the most, for how much danger the player is currently in.
                    If a player goes too many turns without resolving high heat, they will die. Please give the player a warning as the heat gets
                    higher inside the description field. Please remember that this is not literally "heat." The temperature will not
                    affect this score (unless the character is literally on fire). 0 heat = the player is completely safe. 10 heat =
                    the player is in imminent risk of death on the next turn.'''
    
    def __init__(self, description, location, characters, heat):
        self.location = location
        self.characters = characters if characters is not None else []
        self.description = description
        self.heat = heat

    def from_dict(cls, data):
        return cls(
            description=data.get("description", ""),
            location=data.get("location", ""),
            characters=data.get("characters", []),
            heat=data.get("heat", 0)
        )
    
    def to_dict(self):
        return {
            "description": self.description,
            "location": self.location,
            "characters": self.characters,
            "heat": self.heat,
        }