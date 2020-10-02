class Model1:
    def __call__(self, text):
        return 'Translation 1'

class Model2:
    def __call__(self, text):
        return 'Translation 2'

class BadModel:
    def __call__(self, text):
        raise Exception('Failed')


ACTIVE = Model1
