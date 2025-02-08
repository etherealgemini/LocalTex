import PIL.Image


class BaseModel(object):
    def __init__(self):
        pass

    def load(self):
        pass

    def process(self, image: PIL.Image.Image) -> str:
        pass
