import json
import os

import yaml


class ConfigError(Exception):
    pass


_NO_DEFAULT = object()


class Option:
    def __init__(self, description, default=_NO_DEFAULT, type=None):
        self.description = description
        self.default = default
        self.type = type

    def __str__(self):
        parts = [self.description]
        if self.default is not _NO_DEFAULT:
            parts.append("default: {!r}".format(self.default))
        if self.type is not None:
            parts.append("type: {!s}".format(self.type))
        return ", ".join(parts)

    def convert(self, x):
        if self.type is None:
            return x
        return self.type(x)

    def get(self, key, data):
        try:
            x = data[key]
        except KeyError as e:
            if self.default is _NO_DEFAULT:
                raise ConfigError("Missing value for option {!s}".format(key)) from e
            x = self.default
        try:
            return self.convert(x)
        except (TypeError, ValueError) as e:
            raise ConfigError("Invalid value {!r} for option {!s}".format(x, key))

    def make_property(self, key):
        @property
        def prop(config):
            return self.get(key, config._data)

        prop.__doc__ = str(self)
        return prop


class ConfigMeta(type):
    def __new__(metacls, cls, bases, dct):
        options = dct.get("_options", {})
        options.update(metacls.get_options(dct))
        dct["_options"] = options
        dct.update(metacls.make_properties(options))
        return type.__new__(metacls, cls, bases, dct)

    @staticmethod
    def get_options(dct):
        return {k: v for k, v in dct.items() if isinstance(v, Option)}

    @staticmethod
    def make_properties(options):
        return {k: v.make_property(k) for k, v in options.items()}


class Config(metaclass=ConfigMeta):
    def __init__(self, data=None):
        if data is None:
            self._data = {}
        else:
            self._data = dict(data)

    def set(self, keys, value):
        if isinstance(keys, str):
            keys = keys.split(".")

        current = self._data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def validate(self):
        for k, v in self._options.items():
            if isinstance(v.type, Config):
                v.validate()
            else:
                getattr(self, k)

    def from_mapping(self, mapping):
        deep_merge(self._data, mapping)

    def from_yaml(self, yaml_stream):
        self.from_mapping(yaml.safe_load(yaml_stream))

    def from_json(self, json_str):
        self.from_mapping(json.loads(json_str))

    def from_file(self, filepath):
        _, ext = os.path.splitext(filepath)
        extensions = {
            ".json": self.from_json,
            ".yml": self.from_yaml,
            ".yaml": self.from_yaml,
        }
        if ext not in extensions:
            raise ConfigError("Unsupported file type {}".format(ext))
        with open(filepath, "r") as f:
            extensions[ext](f.read())


def deep_merge(dict_1, dict_2):
    for k, v2 in dict_2.items():
        if k in dict_1:
            v1 = dict_1[k]
            if isinstance(v2, dict):
                assert isinstance(v1, dict)
                deep_merge(v1, v2)
            else:
                assert not isinstance(v1, dict)
                dict_1[k] = v2
        else:
            dict_1[k] = v2
