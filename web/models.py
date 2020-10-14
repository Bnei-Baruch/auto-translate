import time

class Model1:
    def __call__(self, mimetype, text):
        time.sleep(2)

        if mimetype.startswith("text"):
            return {'en': 'Translation 1', 'he': text.decode()}
        return {'en': 'Translation 1', 'he': 'המקור אינו קובץ טקסט'}

class Model2:
    def __call__(self, mimetype, text):
        return {'en': 'Translation 2', 'he': 'מקור'}

class BadModel:
    def __call__(self, text):
        raise Exception('Failed')

ACTIVE = Model1
