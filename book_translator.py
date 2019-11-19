from constants import *


class BookTranslator:
    def __init__(self):
        self.title = ''
        self.text = ''
        self.book_opened = False
        self.book = None

    def load_book(self, path):
        pass

    def translate(self):
        pass


class TXTTranslator(BookTranslator):
    def load_book(self, path, encoding=DEFAULT_ENCODING):
        self.book_opened = True
        self.title = ''
        with open(path, 'r', encoding=encoding) as book:
            self.text = book.read()

    def translate(self):
        return self.text


class UniversalTranslator(BookTranslator):
    translators_list = [
        ("txt", TXTTranslator)
    ]

    def __init__(self):
        self.translator = None

    def load_book(self, path):
        file_extension = path.split('.')[-1]
        for (translator_extension, translator) in self.translators_list:
            if translator_extension == file_extension:
                self.translator = translator()
        if self.translator is None:
            raise Exception("Translation error: unknown extension")
        self.translator.load_book(path)

    def translate(self):
        if self.translator is None:
            raise Exception("Translation error: translator is emtpy")
        return self.translator.translate()
