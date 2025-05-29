class Location:
    def __init__(self, name, description, items=None, characters=None,
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
            "north": self.north.name if self.north else None,
            "south": self.south.name if self.south else None,
            "east": self.east.name if self.east else None,
            "west": self.west.name if self.west else None,
            "up": self.up.name if self.up else None,
            "down": self.down.name if self.down else None,
            "parent": self.parent.name if self.parent else None,
            "sub_locations": [loc.name for loc in self.sub_locations]
        }

    @classmethod
    def from_dict(cls, data, locations=None):
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
