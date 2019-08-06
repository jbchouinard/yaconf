import json
import os

import yaml


class ConfigError(Exception):
    pass


class ConfigOptionError(ConfigError):
    def __init__(self, keys, reason):
        self.keys = keys
        self.reason = reason
        super().__init__("Config option {}: {}".format(".".join(keys), reason))

    def with_key(self, key):
        return ConfigOptionError((key,) + self.keys, self.reason)


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
                # Let the sub-config handle it's missing values
                if issubclass(self.type, Config):
                    x = {}
                else:
                    raise ConfigOptionError((), "missing value") from e
            else:
                x = self.default
        try:
            return self.convert(x)
        except (TypeError, ValueError) as e:
            raise ConfigOptionError((), "invalid value {!r}".format(x)) from e

    def make_property(self, key):
        @property
        def prop(config):
            try:
                return self.get(key, config._data)
            except ConfigOptionError as e:
                raise e.with_key(key) from e

        prop.__doc__ = str(self)
        return prop


class ConfigMeta(type):
    def __new__(metacls, name, bases, attrs):
        attrs["_options"] = attrs.get("_options", {})
        attrs["_options"].update(metacls.get_options(attrs))
        attrs.update(metacls.make_properties(attrs["_options"]))
        return super().__new__(metacls, name, bases, attrs)

    @staticmethod
    def get_options(dct):
        return {k: v for k, v in dct.items() if isinstance(v, Option)}

    @staticmethod
    def make_properties(options):
        return {k: v.make_property(k) for k, v in options.items()}


class Config(metaclass=ConfigMeta):
    _options = {}

    def __init__(self, data=None):
        self._data = dict(data) if data is not None else {}

    def set(self, keys, value):
        if isinstance(keys, str):
            keys = keys.split(".")

        current = self._data
        for k in keys[:-1]:
            current[k] = current.get(k, {})
            current = current[k]
        current[keys[-1]] = value

    def _is_config_type(self, value):
        return isinstance(value, type) and issubclass(value, Config)

    def validate(self):
        for k, opt in self._options.items():
            v = getattr(self, k)
            if self._is_config_type(opt.type):
                try:
                    v.validate()
                except ConfigOptionError as e:
                    raise e.with_key(k) from e

    def to_dict(self):
        d = {}
        for k, opt in self._options.items():
            v = getattr(self, k)
            if self._is_config_type(opt.type):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

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
