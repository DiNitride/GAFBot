import inspect
import itertools

import discord
from discord.ext import commands


class HelpFormatter(commands.HelpFormatter):

    async def format_help_for(self, context, command_or_bot):
        """Formats the help page and handles the actual heavy lifting of how
        the help command looks like. To change the behaviour, override the
        :meth:`format` method.
        Parameters
        -----------
        context : :class:`Context`
            The context of the invoked help command.
        command_or_bot : :class:`Command` or :class:`Bot`
            The bot or command that we are getting the help of.
        Returns
        --------
        list
            A paginated output of the help command.
        """
        self.context = context
        return await self.format(command_or_bot)

    def is_bot(self, command):
        """bool : Specifies if the command being formatted is the bot itself."""
        return command is self.context.bot

    def is_cog(self, command):
        """bool : Specifies if the command being formatted is actually a cog."""
        return not self.is_bot(command) and not isinstance(command, commands.Command)

    async def format(self, command):
        """Handles the actual behaviour involved with formatting.
        To change the behaviour, this method should be overridden.
        Returns
        --------
        list
            A paginated output of the help command.
        """
        self._paginator = commands.Paginator()

        # we need a padding of ~80 or so

        description = command.description if not self.is_cog(command) else inspect.getdoc(command)

        if description:
            # <description> portion
            self._paginator.add_line(description, empty=True)

        if isinstance(command, commands.Command):
            # <signature portion>
            signature = self.get_command_signature(command)
            self._paginator.add_line(signature, empty=True)

            # <long doc> section
            if command.help:
                self._paginator.add_line(command.help, empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands(command):
                self._paginator.close_page()
                return self._paginator.pages

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return cog + ':' if cog is not None else '\u200bNo Category:'

        lines = {}
        filtered = await self.filter_command_list(command)
        if self.is_bot(command):
            data = sorted(filtered, key=category)
            for category, bot_commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                bot_commands = sorted(bot_commands)
                if len(bot_commands) > 0:
                    lines[category] = await self._add_subcommands_to_page(bot_commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                cmd = command
                parents = []
                if isinstance(cmd, commands.Command):
                    while cmd and cmd is not self.context.bot:
                        parents.append(cmd.name)
                        cmd = cmd.parent
                lines['Commands:'] = await self._add_subcommands_to_page(filtered, parent=' '.join(reversed(parents)))

        max_width = max((len(cmd) for cmds in lines.values() for cmd, desc in cmds), default=80)

        for cat, cmds in sorted(lines.items()):
            self._paginator.add_line(cat)
            for cmd, desc in cmds:
                self._paginator.add_line(self.shorten('{:<{width}} {}'.format(cmd, desc, width=max_width)))

        # add the ending note
        self._paginator.add_line()
        ending_note = self.get_ending_note()
        self._paginator.add_line(ending_note)
        return self._paginator.pages

    async def filter_command_list(self, command):
        """Returns a filtered list of commands based on the two attributes
        provided, :attr:`show_check_failure` and :attr:`show_hidden`. Also
        filters based on if :meth:`is_cog` is valid.
        Returns
        --------
        iterable
            An iterable with the filter being applied. The resulting value is
            a (key, value) tuple of the command name and the command itself.
        """

        def sane_no_suspension_point_predicate(tup):
            cmd = tup[1]
            if self.is_cog(command):
                # filter commands that don't exist to this cog.
                if cmd.instance is not command:
                    return False

            if cmd.hidden and not self.show_hidden:
                return False

            return True

        async def predicate(tup):
            if sane_no_suspension_point_predicate(tup) is False:
                return False

            cmd = tup[1]
            try:
                return await cmd.can_run(self.context)
            except commands.CommandError:
                return False

        iterator = command.all_commands.items() if not self.is_cog(command) else self.context.bot.all_commands.items()
        if self.show_check_failure:
            return filter(sane_no_suspension_point_predicate, iterator)

        # Gotta run every check and verify it
        ret = []
        for elem in iterator:
            valid = await predicate(elem)
            if valid:
                ret.append(elem)

        return ret

    def get_command_signature(self, command):
        """Retrieves the signature portion of the help page."""
        prefix = self.clean_prefix
        return prefix + command.signature

    def max_name_size(self, command):
        """int : Returns the largest name length of a command or if it has subcommands
        the largest subcommand name."""
        try:
            bot_commands = command.all_commands if not self.is_cog(command) else self.context.bot.all_commands
            if bot_commands:
                return max(map(lambda c: len(c.name) if self.show_hidden or not c.hidden else 0, bot_commands.values()))
            return 0
        except AttributeError:
            return len(command.name)

    def has_subcommands(self, command):
        """bool : Specifies if the command has subcommands."""
        return isinstance(command, commands.GroupMixin)

    async def _add_subcommands_to_page(self, bot_commands, parent=''):
        lines = []
        parent = (parent + ' ') if parent else parent
        for name, command in bot_commands:
            if name in command.aliases:
                # skip aliases
                continue
            entry = '  {prefix}{parent}{0}'.format(
                name, prefix=self.clean_prefix, parent=parent
            )
            lines.append((entry, command.short_doc))
            if self.has_subcommands(command):
                cmds = sorted(await self.filter_command_list(command))
                sub_lines = await self._add_subcommands_to_page(cmds, parent=parent + name)
                lines.extend(sub_lines)
        return lines