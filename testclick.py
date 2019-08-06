from pprint import pprint

import click
import yamconfig.click
from yamconfig import Config, Option
from yamconfig.types import Choice, List, LogLevel, Optional


class LoggingConfig(Config):
    level = Option("log level", type=LogLevel(), default="INFO")
    mode = Option("log mode", type=Choice("file", "syslog"), default="file")


class SubConfig(Config):
    foo = Option("foo", type=int, default=0)
    bar = Option("bar", type=int, default=0)


class AppConfig(Config):
    x = Option("x", type=int, default=0)
    y = Option("y", type=int, default=0)
    ts = Option("ts", type=List(int), default=[])
    o = Option("o", type=Optional(int), default=None)
    s1 = Option("s1", type=SubConfig)
    s2 = Option("s2", type=SubConfig)
    logging = Option("logging", type=LoggingConfig)


@click.command()
@yamconfig.click.add_options(AppConfig)
@click.pass_context
def cli(ctx):
    config = ctx.get_config()
    config.validate()
    pprint(config.to_dict())


if __name__ == "__main__":
    cli(obj={})
