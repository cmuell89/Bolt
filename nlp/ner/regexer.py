import re


class Regexer:
    def __init__(self, regex_list):
        self.regex_list = regex_list

    def get_matches(self, query):
        """
        Searches a query for regex matches against the passed in regex list
        :param query: query to be searched
        :return: the first match that occurs else None
        """
        if self.regex_list is not None:
            for pattern in self.regex_list:
                regex = re.compile(pattern)
                result = regex.search(query)
                if result is not None:
                    match = result.group(0)
                    return match
        return None
