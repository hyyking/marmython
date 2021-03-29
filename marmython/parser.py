from html.parser import HTMLParser
from typing import List, Tuple, Optional, Dict
import json

from .recipe import Ingredient, IngredientFlags, Utensil, Recipe, Step


def parse_utensils(data) -> List[Utensil]:
    ustensils = []
    for ustensil in data:
        name = ustensil.get("name", "...")
        qty = ustensil.get("quantity", "0")
        ustensils.append(Utensil(name, qty))

        


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

def get_json(content, threshold) -> str:
    brackets = 0
    subgroup = ""
    for char in content:
        if char == "{":
            brackets += 1
        if brackets > threshold and char != ";" and char != "(" and char != ")":
            subgroup += char
        if char == "}":
            brackets -= 1
    return subgroup


def parse_ingredients_utensils(data) -> Tuple[List[Ingredient], List[Utensil]]:
    subgroup = get_json(data, 1)
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

def parse_recipes_data(data) -> Tuple[int, int]:
    valid = json.loads(get_json(data, 0)[2:])
    note = valid["recipes"][0]["note"]
    nb_pers = valid["recipes"][0].get("nb_pers", 0)
    return note, nb_pers


def parse_content_info(data) -> Tuple[str, str, str]:
    brackets = 0
    subgroup = ""
    for char in data:
        if char == "{":
            brackets += 1
        if brackets > 0 and char != ";" and char != "(" and char != ")":
            subgroup += char
        if subgroup[-8:] == "userInfo":
            subgroup = subgroup[:-9].strip()[:-1]
            subgroup += "}"
            break
        if char == "}":
            brackets -= 1

    subgroup = subgroup.replace("\'", "\"").replace("\"vuid\": af_guid,", "")
    valid = json.loads(subgroup)["contentInfo"]
    recipe_type = valid.get("recipeType", "")
    recipe_difficulty = valid.get("recipeDifficulty", "")
    recipe_cost = valid.get("recipeCost", "")
    return recipe_type, recipe_difficulty, recipe_cost

Attributes = List[Tuple[str, Optional[str]]]

class RecipeParser(HTMLParser):
    recipe: Recipe = Recipe()

    __parsing_step = False
    __possible_items = False

    def handle_starttag(self, tag: str, a: Attributes):
        attrs: Dict[str, Optional[str]] = dict(a)
        
        if tag == "script" and "text/javascript" == attrs.get("type", ""):
            self.__possible_items = True
            return

        if "recipe-step-list__container" in attrs.get("class", ""):
            self.__parsing_step = True
            self.recipe.steps.append(Step(len(self.recipe.steps)))
            return
    
    def handle_startendtag(self, _: str, a: Attributes) -> None:
        attrs = dict(a)
        
        if "recipeTitle" == attrs.get("name", ""):
            self.recipe.title = str(attrs.get("value", ""))
            return
        
        if "author" == attrs.get("name", ""):
            self.recipe.author = str(attrs.get("content", ""))
            return

    def handle_data(self, data: str):
        data = data.strip()
        if not data:
            return

        if self.__possible_items:
            if "ingredientsUtensils" in data:
                ing, ut = parse_ingredients_utensils(data)
                self.recipe.utensils = ut
                self.recipe.ingredients = ing
            
            if "recipesData" in data:
                note, nb_pers = parse_recipes_data(data)
                self.recipe.note = note
                self.recipe.people = nb_pers
            
            if "contentInfo" in data:
                rtype, rdif, rcost = parse_content_info(data)
                self.recipe.description = rtype
                self.recipe.difficulty = rdif
                self.recipe.cost = rcost

        if self.__parsing_step:
            if not self.recipe.steps[-1].name:
                self.recipe.steps[-1].name = data
                return
            if not self.recipe.steps[-1].content:
                self.recipe.steps[-1].content = data
            else:
                self.__parsing_step = False
            return

    def handle_endtag(self, tag: str):
        if tag == "script":
            self.__possible_items = False
