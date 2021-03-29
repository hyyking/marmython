from typing import Any

from .interface import Serializer, Deserializer
from ..recipe import Recipe, IngredientFlags, Ingredient, Utensil, Step

import toml


class TomlEncoder(Serializer):
    @staticmethod
    def dump(path: str, recipe: Recipe):
        with open(path, "w") as f:
            f.write(TomlEncoder.dumps(recipe))

    @staticmethod
    def dumps(recipe: Recipe) -> str:
        # don't add the empty elements
        recipedict = dict(filter(lambda x: bool(x[1]), recipe.__dict__.items()))
        output = {"recipe": recipedict}
        
        # marshall the utensils as is
        utensils = [utensil.__dict__ for utensil in recipe.utensils]
        output["recipe"]["utensils"] = utensils
        
        # marshall the ingredients and set the flags to an array
        ingredients = [ingredient.__dict__ for ingredient in recipe.ingredients]
        for ingredient in ingredients:
            ingredient["flags"] = list(map(str.lower, IngredientFlags(ingredient["flags"]).to_list()))
            ingredient["name"] = ingredient["name"].title()
            if not ingredient["unit"]:
                del ingredient["unit"]
            if not ingredient["flags"]:
                del ingredient["flags"]

        output["recipe"]["ingredients"] = ingredients
        
        steps = [step.__dict__ for step in recipe.steps]
        output["recipe"]["steps"] = steps

        return toml.dumps(output)

def get_or_default(inp: Any, attr: str, default: Any) -> Any:
    curr = inp["recipe"]
    for a in attr.split("."):
        curr = curr.get(a, default)
    return curr

class TomlDecoder(Deserializer):
    @staticmethod
    def load(path: str) -> Recipe:
        with open(path, "w") as f:
            return TomlDecoder.loads(f.read())

    @staticmethod
    def loads(inp: str) -> Recipe:
        output = Recipe()
        recipe = toml.loads(inp)
        output.title = get_or_default(recipe, "title", "")
        output.author = get_or_default(recipe, "author", "")
        output.description = get_or_default(recipe, "description", "")
        output.difficulty = get_or_default(recipe, "difficulty", "")
        output.cost = get_or_default(recipe, "cost", "")
        output.time = get_or_default(recipe, "time", "")
        output.people = get_or_default(recipe, "people", 0)
        output.note = get_or_default(recipe, "note", 0)

        output.ingredients = [
                Ingredient(**ingredient) 
                for ingredient in get_or_default(recipe, "ingredients", [])
        ]
        for ingredient in output.ingredients:
            ingredient.flags = IngredientFlags.from_list(ingredient.flags) # type: ignore
        output.utensils = [
                Utensil(**utensil)
                for utensil in get_or_default(recipe, "utensils", [])
        ]
        output.steps = [
                Step(**step)
                for step in get_or_default(recipe, "steps", [])
        ]
        return output


def dumps(recipe: Recipe) -> str:
    return TomlEncoder.dumps(recipe)

def dump(path: str, recipe: Recipe):
    return TomlEncoder.dump(path, recipe)

def loads(inp: str) -> Recipe:
    return TomlDecoder.loads(inp)

def load(path: str) -> Recipe:
    return TomlDecoder.load(path)
