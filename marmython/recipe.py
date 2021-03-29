from dataclasses import dataclass, field
from typing import List

class IngredientFlags(int):
    GLUTEN = 2 ** 0
    PORK = 2 ** 1
    VEGAN = 2 ** 2
    VEGE = 2 ** 3
    FISH = 2 ** 4
    NUTS = 2 ** 5

    def has_gluten(self) -> bool:
        return self & self.GLUTEN != 0

    def has_pork(self) -> bool:
        return self & self.PORK != 0

    def has_vegan(self) -> bool:
        return self & self.VEGAN != 0

    def has_vege(self) -> bool:
        return self & self.VEGE != 0

    def has_fish(self) -> bool:
        return self & self.FISH != 0

    def has_nuts(self) -> bool:
        return self & self.NUTS != 0

    def to_list(self) -> List[str]:
        output = []
        if self.has_gluten():
            output.append("GLUTEN")
        if self.has_pork():
            output.append("PORK")
        if self.has_vegan():
            output.append("VEGAN")
        if self.has_vege():
            output.append("VEGE")
        if self.has_fish():
            output.append("FISH")
        if self.has_nuts():
            output.append("NUTS")
        return output
    
    @classmethod
    def from_list(cls, flags: List[str]) -> "IngredientFlags":
        output = cls(0)
        for flag in flags:
            output |= IngredientFlags.__dict__[flag.upper()]
        return output


@dataclass
class Ingredient:
    name: str = ""
    quantity: str = ""
    unit: str = ""
    flags: IngredientFlags = IngredientFlags(0)


@dataclass
class Utensil:
    name: str
    quantity: str


@dataclass
class Step:
    num: int = 0
    name: str = ""
    content: str = ""


@dataclass
class Recipe:
    title: str = ""
    author: str = ""
    description: str = ""
    difficulty: str = ""
    cost: str = ""
    time: str = ""
    people: int = 0
    note: int = 0

    steps: List[Step] = field(default_factory=list)
    ingredients: List[Ingredient] = field(default_factory=list)
    utensils: List[Utensil] = field(default_factory=list)
