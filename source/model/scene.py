class Scene:
    def __init__(self, description, location, characters, heat):
        self.location = location
        self.characters = characters if characters is not None else []
        self.description = description
        self.heat = heat