class Character:
    def __init__(self, name, home, occupation, enemies, description, friends):
        self.name = name
        self.home = home
        self.occupation = occupation
        self.enemies = enemies if enemies is not None else []
        self.friends = friends if friends is not None else []
        self.description = description