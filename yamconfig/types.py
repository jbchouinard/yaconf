import logging


class List:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return "List({!r})".format(self.type)

    def __call__(self, value):
        if isinstance(value, str):
            value = value.split(",")
        return [self.type(v) for v in value]


class Optional:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return "Optional({!r})".format(self.type)

    def __call__(self, value):
        if value is None:
            return None
        return self.type(value)


class Choice:
    def __init__(self, *choices):
        self.choices = set(choices)

    def __repr__(self):
        return "Choice({!r})".format(", ".join(self.choices))

    def __call__(self, value):
        if value not in self.choices:
            raise ValueError(value)
        return value


class LogLevel:
    def __init__(self):
        pass

    def __repr__(self):
        return "LogLevel()"

    def __call__(self, value):
        if isinstance(value, str):
            value = logging.getLevelName(value)
        return int(value)
