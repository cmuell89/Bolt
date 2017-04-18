import pprint
from duckling import Duckling
loaded_duckling = Duckling(minimum_heap_size='64m', maximum_heap_size='128m')
loaded_duckling.load()


class DucklingFactory:
    def __init__(self):
        global loaded_duckling
        self.duckling = loaded_duckling

    def getDucklingInstance(self):
        return self.duckling


class DucklingDatetimeParser:
    def __init__(self, duckling_instance):
        self.duckling = duckling_instance

    def parse(self, query):
        results = self.duckling.parse(query, dim_filter="time")
        results = list(filter(lambda x: self._latent_filter(x), results))
        values = results[0]['value'] if len(results) > 0 else None
        return values

    def _latent_filter(self, entry):
        if 'latent' in entry.keys():
            if entry['latent'] is not True:
                return True
            else:
                return False
        return True
