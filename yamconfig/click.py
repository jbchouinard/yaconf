import click


class ConfigLoader:
    def __init__(self, config_cls):
        self.config_cls = config_cls
        self.args = []
        self.files = []

    def config(self):
        config = self.config_cls()
        for file in self.files:
            config.from_file(file)
        for k, v in self.args:
            config.set(k, v)
        return config


class KeyValueParamType(click.ParamType):
    name = "key=value"

    def convert(self, value, param, ctx):
        try:
            k, v = value.split("=")
            return (k, v)
        except ValueError:
            self.fail("Expected an option in key=value format", param, ctx)


KEYVALUE = KeyValueParamType()


def add_options(config_cls):
    def opt_callback(ctx, _, value):
        ctx.get_loader(config_cls).args.extend(value)

    def file_callback(ctx, _, value):
        ctx.get_loader(config_cls).files.extend(value)

    def decorator(command):
        command = click.option(
            "--config",
            "-c",
            callback=file_callback,
            multiple=True,
            type=click.Path(exists=True, dir_okay=False),
            expose_value=False,
        )(command)
        command = click.option(
            "--option",
            "-o",
            callback=opt_callback,
            multiple=True,
            type=KEYVALUE,
            expose_value=False,
        )(command)
        return command

    return decorator


def get_loader(ctx, config_cls):
    if "yaconf.config_loader" not in ctx.meta:
        ctx.meta["yaconf.config_loader"] = ConfigLoader(config_cls)
    return ctx.meta["yaconf.config_loader"]


def get_config(ctx):
    return ctx.meta["yaconf.config_loader"].config()


click.Context.get_config = get_config
click.Context.get_loader = get_loader
