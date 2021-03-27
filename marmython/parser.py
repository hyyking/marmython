from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Dict
import json


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


@dataclass
class Ingredient:
    name: str
    quantity: str
    unit: str
    flags: IngredientFlags


@dataclass
class Utensil:
    name: str
    quantity: str


@dataclass
class Step:
    name: str = ""
    content: str = ""


@dataclass
class Recipe:
    title: str = "UNKNOWN"
    steps: List[Step] = field(default_factory=list)
    ingredients: List[Ingredient] = field(default_factory=list)
    utensils: List[Utensil] = field(default_factory=list)


def parse_utensils(data) -> List[Utensil]:
    return [Utensil(ut["utensil_name"], ut["quantity"]) for ut in data]


def parse_ingredients(data) -> List[Ingredient]:
    ingredients = []
    for ingredient in data[0]["ingredient_group_items"]:
        quantity = ingredient.get("quantity", 1)
        unit = ingredient.get("unit", {"name": ""})["name"]
        name = ingredient["ingredient"]["name"]
        flags = IngredientFlags(0)
        if ingredient["ingredient"]["is_gluten"]:
            flags |= IngredientFlags.GLUTEN
        if ingredient["ingredient"]["is_pork"]:
            flags |= IngredientFlags.PORK
        if ingredient["ingredient"]["is_vegan"]:
            flags |= IngredientFlags.VEGAN
        if ingredient["ingredient"]["is_vegetarian"]:
            flags |= IngredientFlags.VEGE
        if ingredient["ingredient"]["is_fish"]:
            flags |= IngredientFlags.FISH
        if ingredient["ingredient"]["is_nuts"]:
            flags |= IngredientFlags.NUTS
        ingredients.append(Ingredient(name, quantity, unit, flags))
    return ingredients


def parse_ingredients_utensils(data) -> Tuple[List[Ingredient], List[Utensil]]:
    brackets = 0
    subgroup = ""
    for char in data:
        if char == "{":
            brackets += 1
        if brackets > 1 and char != ";" and char != "(" and char != ")":
            subgroup += char
        if char == "}":
            brackets -= 1

    valid = subgroup.replace("utensils", '"utensils"').replace(
        "ingredientGroups", '"ingredientGroups"'
    )
    try:
        d = json.loads(valid)
    except json.JSONDecodeError as e:
        with open("decode_error.log", "w") as f:
            f.write(data)
        raise e

    utensils = parse_utensils(d["utensils"])
    ingredients = parse_ingredients(d["ingredientGroups"])
    return ingredients, utensils


class RecipeParser(HTMLParser):
    recipe: Recipe = Recipe()

    parsing_step = False
    parsing_title = False
    possible_items = False

    def handle_starttag(self, tag: str, a: List[Tuple[str, Optional[str]]]):
        attrs: Dict[str, Optional[str]] = dict(a)
        if tag == "h1" and "main-title" in attrs.get("class", ""):
            self.parsing_title = True
            return

        if tag == "script" and "text/javascript" == attrs.get("type", ""):
            self.possible_items = True
            return

        if "recipe-step-list__container" in attrs.get("class", ""):
            self.parsing_step = True
            self.recipe.steps.append(Step())
            return

    def handle_data(self, data: str):
        data = data.strip()
        if not data:
            return
        if self.parsing_title:
            self.recipe.title = data
            self.parsing_title = False

        if self.possible_items:
            if "ingredientsUtensils" in data:
                ing, ut = parse_ingredients_utensils(data)
                self.recipe.utensils = ut
                self.recipe.ingredients = ing

        if self.parsing_step:
            if not self.recipe.steps[-1].name:
                self.recipe.steps[-1].name = data
                return
            if not self.recipe.steps[-1].content:
                self.recipe.steps[-1].content = data
            else:
                self.parsing_step = False
            return

    def handle_endtag(self, tag: str):
        if tag == "script":
            self.possible_items = False
