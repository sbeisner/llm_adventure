class Player:
    player_prompt = '''You are helping to narrate a fantasy text adventure game.
                    Please generate a json response for the current Player status in the following format. I need to convert this directly to a python dictionary,
                    so please don't deviate from this formatting.:
                    inventory: As an optionally null list, any items the player currently has. Consider what items the player currently has and if
                    there is any reason for them to have either gained new ones or lost one based on their actions.
                    acquaintances: As an optionally null list, the names of any characters the player has met but does not know well.
                    restrictions: As an optionally null list, anything inhibitting the actions or mobility of the player (i.e. being tied up, bleeding, in jail, etc.)
                    items: As an optionally null list, items in this location that the player could take (legally or illegally)
                    enemies: As an optionally null list, any characters the player has met with whom they are enemies.
                    friends: As an optionally null list, any characters with whom the player is friendly and has earned their trust.
                    current_location: The name of the location the player is currently in.
                    money: The player's current money on hand (in gold pieces). Money cannot go below 0.'''

    def __init__(self,inventory, restrictions, acquaintances, enemies, friends, money):
        self.restrictions = restrictions
        self.inventory = inventory if inventory is not None else []
        self.acquaintances = acquaintances if acquaintances is not None else []
        self.enemies = enemies if enemies is not None else []
        self.friends = friends if friends is not None else []
        self.money = money if money is not None else 0
        

    def to_dict(self):
        return {
            "inventory": self.inventory,
            "friends": self.friends,
            "enemies": self.enemies,
            "restrictions": self.restrictions,
            "acquaintances": self.acquaintances,
            "money": self.money
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            inventory=data.get("inventory", []),
            friends=data.get("friends", []),
            enemies=data.get("enemies", []),
            restrictions=data["restrictions"],
            acquaintances=data.get("acquaintances", []),
            money=data["money"]
        )
    
    def __str__(self,):
        return(self.inventory)
