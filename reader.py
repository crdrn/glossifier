from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from six import StringIO

FILE = './samples/salinger.pdf'


def _read_pages(interpreter, output, fp, password=None):
    """
    Reads text from pdf into a list of strings, where
    list[i] gives text from the i-1th page.

    :param fp: pointer to open pdf file
    :param password: (optional) password to open file
    :return: list of strings corresponding to each page's text
    """

    text = []
    for pageno, page in enumerate(PDFPage.get_pages(fp, password=password)):
        interpreter.process_page(page)
        text.append(output.getvalue())
        reset_stream(output)
    return text

def reset_stream(output):
    output.truncate(0)
    output.seek(0)
    return


def _get_pages(filename, password=None, codec='utf-8', laparams=None):
    try:
        fp = open(filename, 'rb')
    except IOError:
        # if file does not exist or similar problems
        pass
    _resources = PDFResourceManager()
    _output = StringIO()
    _device = TextConverter(_resources, _output, codec=codec, laparams=laparams)
    _interpreter = PDFPageInterpreter(_resources, _device)
    pages = _read_pages(_interpreter, _output, fp)


def main():
    _get_pages(FILE)


if __name__ == '__main__':
    main()
