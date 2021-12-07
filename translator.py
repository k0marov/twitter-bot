from deep_translator import MyMemoryTranslator, GoogleTranslator

_translator = GoogleTranslator(source="auto", target="ru")
def translate(text):
    return _translator.translate(text=text)
