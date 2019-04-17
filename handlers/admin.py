import logging

from handlers.base import BaseHandler
from handlers.mixins import AdminRequiredMixin, NonemptyMessageMixin
from handlers.registry import register_handler

import database
import settings
from util import admin_help_list


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

    async def respond(self):
        database.add_quote(' '.join(self.content), len(self.quote_type) - 1)
        await self.send_message('{} quote added!'.format(self.quote_type))


@register_handler('add ?')
class AdminSingleQuote(AdminQuoteBase):
    quote_type = '?'


@register_handler('add ??')
class AdminDoubleQuote(AdminQuoteBase):
    quote_type = '??'


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
        logging.info("{} updated {}'s number of times swore to {}.".format(self.discord_user,
                                                                           await user.discord_user, user.times_swore))
        user.save()
