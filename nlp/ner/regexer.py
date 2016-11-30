import re


class Regexer:
    def __init__(self, regex_list):
        self.regex_list = regex_list

    def get_matches(self, query):
        results = []
        for pattern in self.regex_list:
            regex = re.compile(pattern)
            result = regex.search(query)
            if result is not None:
                match = result.group(0)
                results.append(match)
        return results
