import click
import yamconfig.click
from yamconfig import Config, Option


class SubConfig(Config):
    z = Option("z", type=int, default=0)


class AppConfig(Config):
    x = Option("x", type=int, default=0)
    y = Option("y", type=int, default=0)
    s = Option("s", type=SubConfig, default=None)


@click.command()
@yamconfig.click.add_options(AppConfig)
@click.pass_context
def cli(ctx):
    config = ctx.get_config()
    config.validate()
    print("x={!r}".format(config.x))
    print("y={!r}".format(config.y))
    print("s.z={!r}".format(config.s.z))


if __name__ == "__main__":
    cli(obj={})
