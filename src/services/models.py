# models.py

class Country:
    def __init__(self, name: str, code: str, homepage: str, inside: str, bottom: str):
        self.name = name
        self.code = code
        self.homepage = homepage
        self.inside = inside
        self.bottom = bottom
    def __str__(self):
        return self.code

