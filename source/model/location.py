class Location:
    loc_prompt = '''You are helping to narrate a fantasy text adventure game.
                    Please generate a json response for the Location in the following format. I need to convert this directly to a python dictionary,
                    so please don't deviate from this formatting. Additionally, consider whether the player has any
                    current restrictions on their movement before allowing them to go somewhere new:
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
                    subs: As a list, any sub_locations'''

    def __init__(self, name, description="", items=None, characters=None,
                 north=None, south=None, east=None, west=None, up=None, down=None,
                 parent=None, sub_locations=None):
        self.name = name
        self.description = description
        self.items = items if items is not None else []
        self.characters = characters if characters is not None else []
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.up = up
        self.down = down
        self.parent = parent
        self.sub_locations = sub_locations if sub_locations is not None else []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "items": self.items,
            "characters": self.characters,
            "north": self.north if self.north else None,
            "south": self.south if self.south else None,
            "east": self.east if self.east else None,
            "west": self.west if self.west else None,
            "up": self.up if self.up else None,
            "down": self.down if self.down else None,
            "parent": self.parent if self.parent else None,
            "sub_locations": [loc for loc in self.sub_locations]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            items=data.get("items", []),
            characters=data.get("characters", []),
            north=data.get("north", []),
            south=data.get("south", []),
            east=data.get("east", []),
            west=data.get("west", []),
            up=data.get("up",[]),
            down=data.get("down",[]),
            parent=data.get("parent",[]),
            sub_locations=data.get("sub_locations", [])
        )
    def __str__(self,):
        return(self.name + ': ' + self.description)
