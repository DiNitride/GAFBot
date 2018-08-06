from discord.ext import commands
import asyncio

DIGITS = ('\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{DIGIT NINE}\N{COMBINING ENCLOSING KEYCAP}',
          '\N{KEYCAP TEN}')
ARROWS = ('\N{LEFTWARDS BLACK ARROW}',
          '\N{BLACK RIGHTWARDS ARROW}')
CANCEL = '\N{CROSS MARK}'
UNDO = '\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}'  # :arrows_counterclockwise:
DONE = '\N{WHITE HEAVY CHECK MARK}'

# async def reaction_prompt(self, message, user, destination, *, timeout=60):
#     msg = await self.bot.send_message(destination, message)
#     for e in (DONE, CANCEL):
#         await self.bot.add_reaction(msg, e)
#     res = await self.bot.wait_for_reaction([DONE, CANCEL], message=msg,
#                                            user=user, timeout=timeout)
#     return res is not None and res.reaction.emoji == DONE


async def start_reaction_menu(bot, options, user, destination, count=1, *, timeout=60, per_page=10, header='', return_from=None, allow_none=False):
    """Create a reaction menu from a list of options.

    Arguments:
    options: list of options to choose from
    user   : the user using the menu
    count  : the number of choices that can be made (negative value for manual stop,
                                                     0 for no selections)
    timeout: timeout for each page
    code   : whether each page should be in a codeblock
    header : str shown above each page
    return_from: list `options` is derived from, if any. must be same length as `options`
    allow_none : allow selecting no options

    Returns:
    None : if return_from and options lengths don't match
    list : of selected options

    ignore return value if you set count=0
    """

    def check(_, u):
        return u == user

    if return_from is None:
        return_from = options
    elif len(return_from) != len(options):
        return None

    if count:
        reactions = (*DIGITS, *ARROWS, CANCEL, UNDO, DONE)
        if count > len(options):
            count = len(options)
        per_page = 10
    else:
        reactions = (*ARROWS, CANCEL, UNDO, DONE)

    pag = commands.Paginator(prefix='', suffix='')
    page_len = 0
    for ind, line in enumerate(options):
        # If it a menu with selection, number the options
        if count:
            pag.add_line('{}. {}'.format(ind % 10 + 1, line))
        else:
            pag.add_line(line)
        page_len += 1
        if page_len == per_page:
            pag.close_page()
            page_len = 0
    pages = pag.pages
    page = 0
    header = header + '\n'
    choices = []
    msg = await destination.send("{}{}".format(header, pages[page]))
    while True:
        if page:
            await msg.add_reaction(ARROWS[0])
        if count:
            for r in DIGITS[:pages[page].count('\n') - 1]:
                await msg.add_reaction(r)
        if page != len(pages) - 1:
            await msg.add_reaction(ARROWS[1])
        if choices:
            await msg.add_reaction(UNDO)
        if choices or allow_none:
            await msg.add_reaction(DONE)
        await msg.add_reaction(CANCEL)
        try:
            res, r_user = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await msg.delete()
            return None
        if res.emoji == CANCEL:
            await msg.delete()
            return None
        elif res.emoji in DIGITS:
            choice = page * 10 + DIGITS.index(res.emoji)
            if choice not in choices:
                choices.append(choice)
                if len(choices) == count:
                    break
            else:
                choice.remove(choice)
        elif res.emoji == ARROWS[0]:
            page -= 1
        elif res.emoji == ARROWS[1]:
            page += 1
        elif res.emoji == UNDO:
            choices.pop()
        elif res.emoji == DONE:
            break
        await msg.remove_reaction(res, r_user)
        if choices:
            head = "{}{}".format(header, pages[page])
            head += '\n' + 'Selected: ' + ', '.join(map(str, [options[ind] for ind in choices]))
        else:
            head = "{}\n{}".format(header, pages[page])
        if page == len(pages) - 1:
            await msg.remove_reaction(ARROWS[1], bot.user)
        await msg.edit(content=head)
        if page == 0:
            await msg.remove_reaction(ARROWS[0], bot.user)
    await msg.delete()
    return [return_from[ind] for ind in choices]
