import discord
from discord.ext.commands import DefaultHelpCommand, Group


class Help(DefaultHelpCommand):

    def add_indented_commands(self, commands, *, heading, max_size=None):

        if not commands:
            return

        self.paginator.add_line(heading)
        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))
            entry = '{0}- {1:<{width}} {2}'.format(self.indent * ' ', name, command.short_doc, width=width)
            self.paginator.add_line(self.shorten_text(entry))
            if isinstance(command, Group):
                for subcommand in command.commands:
                    name = subcommand.name
                    width = max_size - (get_width(name) - len(name))
                    entry = '{0}- {1:<{width}} {2}'.format(4 * ' ', name, subcommand.short_doc, width=width)
                    self.paginator.add_line(self.shorten_text(entry))