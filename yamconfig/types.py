class List:
    def __init__(self, type):
        self.type = type

    def __call__(self, value):
        if isinstance(value, str):
            value = value.split(',')
        return [self.type(v) for v in value]