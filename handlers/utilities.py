import datetime
import logging
import os
import re

from operator import itemgetter

from handlers.base import BaseHandler
from handlers.mixins import NonemptyMessageMixin
from handlers.registry import register_handler

import settings
from util import help_list


@register_handler('help')
class Help(BaseHandler):
    async def respond(self):
        commands, arguments = zip(*help_list.items())
        em = self.create_embed('{} help'.format(settings.BOT_NAME),
                               'Available commands from {}'.format(settings.BOT_NAME))
        em.add_field(name='Command', value='\n'.join(settings.COMMAND_PREFIX + x for x in commands))
        em.add_field(name='Arguments', value='\n'.join(x or 'No Arguments' for x in arguments))
        await self.send_message(embed=em)


@register_handler('everyone')
class Everyone(BaseHandler):
    async def respond(self):
        users = [user.mention for user in self.guild.members if not user.bot]
        await self.send_message('```' + ' '.join(users) + '```')


@register_handler('info')
class Info(BaseHandler):
    async def respond(self):
        users = []
        for user in self.guild.members:
            if user in self.message.mentions or len(self.message.mentions) == 0:
                current_user = [str(user)[:20], str(user.nick)[:20]]
                try:
                    current_user.append(settings.NAMES[user.id])
                except KeyError:
                    current_user.append('Unknown')
                users.append(current_user)

        users.sort(key=itemgetter(-1))
        usernames, nicknames, names = zip(*users)

        em = self.create_embed('Member Names', 'Name of server members.', colour=0xFF630A)
        em.add_field(name='Username', value='\n'.join(usernames))
        em.add_field(name='Nickname', value='\n'.join(nicknames))
        em.add_field(name='Name', value='\n'.join(names))

        await self.send_message(embed=em)


@register_handler('bigmoji')
class Bigmoji(BaseHandler):
    async def respond(self):
        emojis = []
        content = self.content_str
        while True:
            match = re.search('<:[A-Z, a-z]+:([0-9]{18})>', content)
            try:
                emojis.append(match.group(1))
                content = content.reaplce(match.group(0), '')
            except Exception:
                break
        for emoji in emojis[:3]:
            await self.send_message('https://discordapp.com/api/emojis/{}.png'.format(emoji))


@register_handler('emoji')
class Emoji(NonemptyMessageMixin, BaseHandler):
    argument_name = 'emoji'

    async def respond(self):
        emoji = self.content_str
        try:
            await self.send_file(os.path.join(settings.EMOJI_DIR, emoji + '.png'))
        except FileNotFoundError:
            await self.send_message('No emoji named "{}" found.'.format(emoji))


@register_handler('emojilist')
class EmojiList(BaseHandler):
    async def respond(self):
        em = self.create_embed('Emoji List', '\n'.join(emoji.split('.')[0] for emoji in os.listdir(settings.EMOJI_DIR)))
        await self.send_message(embed=em)


@register_handler('clean')
class Clean(BaseHandler):
    def clean_check(self, message):
        _now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return (_now - message.created_at < datetime.timedelta(weeks=2) and
                message.author == self.bot.user)

    async def respond(self):
        deleted = await self.channel.purge(limit=100, check=self.clean_check)
        logging.info('%s deleted %s messages(s) from %s(%s).',
                     self.discord_user, len(deleted), self.channel, self.channel.id)
        await self.send_message(':ok_hand:', delete_after=10)
