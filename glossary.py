from operator import itemgetter
from itertools import groupby


def build_glossary(key_terms, delimiter=', '):
    """
    Builds a glossary using the target key terms and their page numbers from the raker.

    :param key_terms: dict of the key term and a list of pages where it is found
    :return: dict of the key term and a prettified string with page ranges
    """
    glossary = {}
    for key_term in key_terms:
        page_ranges = collapse_pages(key_terms[key_term])
        glossary[key_term] = prettify_pages(page_ranges, delimiter)
    return glossary


def collapse_pages(page_list):
    """
    Collapses a list of numbers into range tuples (start, end).

    Example: [1, 2, 3, 10, 4, 61, 63, 62] --> [(1, 4), (10, 10), (61, 63)]

    :param page_list: list of page numbers
    :return: list of tuples (start, end) of each sub-range of consecutive page numbers
    """
    ranges = []
    for k, g in groupby(enumerate(sorted(page_list)), lambda x: x[0]-x[1]):
        group = list(map(itemgetter(1), g))
        ranges.append((group[0], group[-1]))
    return ranges


def prettify_pages(page_ranges, delimiter):
    """
    Prettifies the page ranges into a nice, easy to read string.

    :param page_ranges: list of page range tuples
    :param delimiter: delimiter for consecutive groups of pages in the prettified string
    :return:
    """
    page_strings = []
    for page_range in page_ranges:
        start, end = page_range
        if start is end:
            # lone page
            page_strings.append('%s' % start)
        else:
            # range of pages
            page_strings.append('%s-%s' % (start, end))
    return delimiter.join(page_strings)
