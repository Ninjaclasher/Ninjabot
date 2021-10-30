import logging

from handlers.base import BaseHandler
from handlers.mixins import AdminRequiredMixin, NonemptyMessageMixin
from handlers.registry import register_handler

import database
import settings
from util import admin_help_list


logger = logging.getLogger('ninjabot.handler')


@register_handler('adminhelp')
class AdminHelp(AdminRequiredMixin, BaseHandler):
    async def respond(self):
        commands, arguments = zip(*admin_help_list.items())

        em = self.create_embed('{} Admin Help'.format(settings.BOT_NAME),
                               'Available admin commands from {}'.format(settings.BOT_NAME))
        em.add_field(name='Command', value='\n'.join(settings.COMMAND_PREFIX + x for x in commands))
        em.add_field(name='Arguments', value='\n'.join(x or 'No Arguments' for x in arguments))
        await self.send_message(embed=em)


class AdminQuoteBase(AdminRequiredMixin, NonemptyMessageMixin, BaseHandler):
    argument_name = 'quote'
    quote_type = ''

    def sanitize(self, content):
        for x in {'“', '”', '‘', '’'}:
            if x in content:
                raise ValueError('disallowed unicode {} detected.'.format(x))
        return content

    async def respond(self):
        try:
            quote = self.sanitize(' '.join(self.content))
        except ValueError as e:
            await self.send_message('Failed to add quote: {}'.format(e))
            return

        database.add_quote(quote, len(self.quote_type) - 1, self.guild.id)
        logger.info(
            '%s added the quote "%s" for guild %d',
            self.discord_user,
            quote,
            self.guild.id,
        )
        await self.send_message('{} quote added!'.format(self.quote_type))


@register_handler('add ?')
class AdminSingleQuote(AdminQuoteBase):
    quote_type = '?'

    def sanitize(self, content):
        content = super().sanitize(content)
        quote, dash, context = content.rpartition('-')

        if len(quote) == 0:
            raise ValueError('no quote detected.')
        if len(dash) == 0 or len(context) == 0:
            raise ValueError('no context detected.')

        if not quote.endswith(' '):
            quote += ' '
        if not context.startswith(' '):
            context = ' ' + context

        return quote.capitalize() + dash + context.capitalize()


@register_handler('add ??')
class AdminDoubleQuote(AdminQuoteBase):
    quote_type = '??'

    def sanitize(self, content):
        content = super().sanitize(content)

        lines = []
        for i, line in enumerate(content.strip('\n').split('\n'), 1):
            context, colon, quote = line.partition(':')

            if len(context) == 0:
                raise ValueError('no context detected on line {}.'.format(i))
            if len(colon) == 0 or len(quote) == 0:
                raise ValueError('no quote detected on line {}.'.format(i))

            if not quote.startswith(' '):
                quote = ' ' + quote
            if not context.endswith(' '):
                context += ' '

            lines.append(context.capitalize() + colon + quote.capitalize())

        return '\n'.join(lines)


@register_handler('changeprofanity')
class AdminProfanity(AdminRequiredMixin, BaseHandler):
    async def respond(self):
        try:
            user = await database.load_user(self.message.mentions[0].id)
        except IndexError:
            user = self.user
        try:
            user.times_swore = int(self.content[0])
        except (ValueError, IndexError):
            user.times_swore = 0
        logger.info("%s updated %s's number of times swore to %s.",
                    self.discord_user, await user.discord_user, user.times_swore)
        user.save()
