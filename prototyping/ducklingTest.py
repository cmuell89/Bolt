from duckling import Duckling, DucklingWrapper
import pprint

pp = pprint.PrettyPrinter(indent=4)
duck = Duckling(minimum_heap_size='64m', maximum_heap_size='128m')
duck.load()


if __name__ == '__main__':
    query = ''
    while query != 'exit':
        query = input("Enter query:\n")
        print("duckling parse")
        pp.pprint(duck.parse(query, dim_filter='time'))
