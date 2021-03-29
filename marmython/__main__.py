import requests

from marmython.parser import RecipeParser
from marmython.serialize.toml import dumps, loads


class MarmitonSession(requests.Session):
    url = "https://www.marmiton.org/%s"
    random = "recettes/recette-hasard.aspx"

    def __init__(self):
        super().__init__()
        self.headers.update(
            {
                "Host": "www.marmiton.org",
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-GPC": "1",
            }
        )

    def get_random(self) -> requests.Response:
        req = requests.Request("GET", self.url % self.random)
        return self.send(self.prepare_request(req))

    pass


def fmtprint(recipe):
    print(f"{recipe.title.upper()} ({recipe.note}/5)")
    print(f"by {recipe.author}")
    print(f"for {recipe.people} people\n")

    print("--- USTENSILES")
    for utensil in recipe.utensils:
        print(f"{utensil.name} ({utensil.quantity})")

    print("--- INGREDIENTS")
    for ingredient in recipe.ingredients:
        print(f"{ingredient.name} ({str(ingredient.quantity) + ingredient.unit})")

    print("\n")
    for step in recipe.steps:
        print(f"({step.num}) {step.name}\n{step.content}\n")


def main():
    parser = RecipeParser()
    session = MarmitonSession()
    parser.feed(session.get_random().text)
    print(parser.recipe)


def test():
    parser = RecipeParser()
    with open("samples/saladehomard.html", "r") as f:
        parser.feed(f.read())
    fmtprint(parser.recipe)
    print(dumps(parser.recipe))


if __name__ == "__main__":
    main()
    # test()
