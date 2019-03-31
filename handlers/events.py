import logging
import random

from handlers.base import BaseEvent 
from handlers.registry import register_event

import database
import settings


@register_event('server_leaver')
class ServerLeaver(BaseEvent):
    async def trigger(self):
        return True

    async def respond(self):
        if self.server.id not in settings.WHITELISTED_SERVERS:
            logging.warn('Left server %s with id %s.', self.server.name, self.server.id)
            await self.bot.leave_server(self.server)


@register_event('reaction_adder')
class ReactionAdder(BaseEvent):
    async def trigger(self):
        return random.random() <= 0.005 and len(self.server.emojis) > 0

    async def respond(self):
        try:
            await self.bot.add_reaction(self.message, random.choice(self.server.emojis))
        except:
            logging.warn("Failed to add a reaction to %s (%s)'s message.", self.message.author, self.message.author.id)
        else:
            logging.info("Added a reaction to %s (%s)'s message.", self.message.author, self.message.author.id)


@register_event('profanity_checker')
class ProfanityChecker(BaseEvent):
    @classmethod
    def has_swear(cls, content):
        msg = ''.join(x for x in content.lower() if x.isalnum() or x.isspace())
        for x in settings.UNBANNED_WORDS:
            msg = msg.replace(x, '')
        for x in settings.SPECIAL_SWEAR_WORDS:
            if x in msg.split():
                return True
        for x in settings.SWEAR_WORDS:
            if x in msg:
                return True
        return False

    def swear_check(self, message):
        content = message.content.strip().lower()
        return (('ninjabot' in content or self.bot.user in message.mentions) and
                ('die' in content or self.has_swear(content)))

    async def trigger(self):
        before = self.kwargs.get('before', None)
        if before is not None and self.has_swear(before.content):
            return False
        return self.has_swear(self.message.content)

    async def respond(self):
        await self.send_message(':x: {}'.format(self.message.author.mention))
        logging.info('%s (%s) swore, updated counter.', await self.user.discord_user, self.user.id)
        self.user.times_swore += 1
        self.user.save()
        new_message = await self.bot.wait_for_message(timeout=10, author=self.message.author,
                                                      channel=self.channel, check=self.swear_check)
        if new_message is not None:
            await self.send_message('NO U. Blame <@253354364746334212> for this useless feature.')


@register_event('awake_time_updater')
class AwakeTimeUpdater(BaseEvent):
    async def trigger(self):
        return True

    async def respond(self):
        self.user.update_awake_time()

