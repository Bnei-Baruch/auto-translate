class Model1:
    def __call__(self, text):
        return 'Translation 1'

class Model2:
    def __call__(self, text):
        return 'Translation 2'

ACTIVE = Model1
