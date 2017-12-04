#TODO: Add logging
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFEncryptionError
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from rake_nltk import Rake
from six import StringIO

import re

FILE = './samples/salinger.pdf'
PAGE_DELIMITER = ' '


def _read_pages(interpreter, output, fp, password=None):
    """
    Reads text from pdf into a list of strings, where
    list[i] gives text from the i-1th page.

    :param fp: (str) pointer to open pdf file
    :param password: (str) optional password to open file
    :return: (list) strings corresponding to each page's text
    """
    text = []
    for pageno, page in enumerate(PDFPage.get_pages(fp, password=password)):
        interpreter.process_page(page)
        raw_text = output.getvalue()
        text.append(raw_text)
        _reset_stream(output)
    return text


def _reset_stream(output):
    """
    Clears the output stream and resets pointer to head
    :param output: (StringIO) String I/O stream
    """
    output.truncate(0)
    output.seek(0)
    return


def _get_pages(filename, password=None, codec='utf-8', laparams=None):
    """
    Gets text from
    :param filename: (str) name of pdf file to be read from
    :param password: (str) (optional) password to unlock pdf file
    :param codec: (str) encoding of pdf file
    :param laparams: (obj) layout parameters of the pdf
    :return: (list) strings corresponding to the text of each page
    """
    try:
        fp = open(filename, 'rb')
    except IOError:
        # if file does not exist or similar problems
        raise IOError('Could not open file %s', filename)
    _resources = PDFResourceManager()
    _output = StringIO()
    _device = TextConverter(_resources, _output, codec=codec, laparams=laparams)
    _interpreter = PDFPageInterpreter(_resources, _device)
    try:
        return _read_pages(_interpreter, _output, fp, password=password)
        # TODO: Fix encoding problems
    except PDFEncryptionError:
        # if text is encrypted in a strange way
        raise IOError('Could not read file %s', filename)


def _merge_text(list_of_text):
    return PAGE_DELIMITER.join(list_of_text)


def _get_above_average_keywords(extracter):
    """
    Returns only those keywords that are
    :param extracter:
    :return:
    """
    ranked_phrases = extracter.get_ranked_phrases_with_scores()
    max_score = ranked_phrases[0][0]
    for i, (score,_) in enumerate(ranked_phrases):
        if score < max_score/2:
            return extracter.get_ranked_phrases()[:i]
    raise Exception('Could not find keyphrases')


def _get_keywords_from_text(all_text, metric='average', language=None):
    """
    Makes a list of keywords that are deemed the most
    relevant for being glossed based on specified metric
    :param original: list of original keywords
    :param metric: chosen  metric for 'good' keywords
    :return: (list) chosen keywords
    """
    extracter = Rake(language)
    extracter.extract_keywords_from_text(all_text)
    if metric is 'average':
        return _get_above_average_keywords(extracter)
    elif metric is 'all':
        return extracter.get_ranked_phrases()
    elif metric is 'frequency':
        pass
    else:
        raise Exception('Keyword metric is invalid')


def _get_page_references(keywords, pages):
    """
    Finds the pages in which each keyword in keywords appears
    and returns them.
    :param keywords: list of keywords to search for
    :param pages: list of pages whose text to look through
    :return: dictionary of key: word, value: list of pages
    """
    references = {}
    for word in keywords:
        references[word] = []
        for pageindex, page in enumerate(pages):
            # TODO: find out why some keywords don't get found
            if re.search(re.compile(re.escape(word)), page):
                references[word].append(pageindex+1)
    return references


def get_glossary_items(file):
    """
    Gets relevant words and phrases to put into a glossary
    from a given file
    :param file: file to be glossified
    :return: (dict) keywords and the pages in which the keywords are found
    """
    text_from_pages = _get_pages(file, password=None, codec='utf-8', laparams=None)
    all_text = _merge_text(text_from_pages)
    keywords = _get_keywords_from_text(all_text, metric='average')
    references = _get_page_references(keywords, text_from_pages)
    return references


if __name__ == '__main__':
    glossary_items = get_glossary_items(FILE)
    print(glossary_items)
