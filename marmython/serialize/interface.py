import abc

from ..recipe import Recipe

class Serializer(abc.ABC):
    @abc.abstractstaticmethod
    def dump(self, path: str, recipe: Recipe):
        pass

    @abc.abstractstaticmethod
    def dumps(self, recipe: Recipe) -> str:
        pass

class Deserializer(abc.ABC):
    @abc.abstractstaticmethod
    def load(self, path: str) -> Recipe:
        pass
    
    @abc.abstractstaticmethod
    def loads(self, inp: str):
        pass
