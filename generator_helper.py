
class GeneratorHelper:

    def __init__(self, iterable_object):
        self.obj = iterable_object
        self.gen = self._element_generator()

    def _element_generator(self):
        for x in self.obj:
            yield x

    def get_element(self):
        return next(self.gen, None)