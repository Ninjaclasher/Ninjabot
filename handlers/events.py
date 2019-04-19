import asyncio
import logging
import random

from handlers.base import BaseEvent
from handlers.registry import register_event

import settings


@register_event('server_leaver')
class ServerLeaver(BaseEvent):
    async def trigger(self):
        return True

    async def respond(self):
        if self.guild.id not in settings.WHITELISTED_SERVERS:
            logging.warn('Left server %s with id %s.', self.guild.name, self.guild.id)
            await self.guild.leave()


@register_event('reaction_adder')
class ReactionAdder(BaseEvent):
    async def trigger(self):
        return random.random() <= 0.005 and len(self.guild.emojis) > 0

    async def respond(self):
        try:
            await self.message.add_reaction(random.choice(self.guild.emojis))
        except Exception:
            logging.warn("Failed to add a reaction to %s (%s)'s message.", self.author, self.author.id)
        else:
            logging.info("Added a reaction to %s (%s)'s message.", self.author, self.author.id)


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
        if message.author != self.author or message.channel != self.channel:
            return False

        content = message.content.strip().lower()
        return (('ninjabot' in content or self.bot.user in message.mentions) and
                ('die' in content or self.has_swear(content)))

    async def trigger(self):
        before = self.kwargs.get('before', None)
        if before is not None and self.has_swear(before.content):
            return False
        return self.has_swear(self.message.content)

    async def respond(self):
        await self.send_message(':x: {}'.format(self.author.mention))
        logging.info('%s (%s) swore, updated counter.', await self.user.discord_user, self.user.id)
        self.user.times_swore += 1
        self.user.save()
        try:
            await self.bot.wait_for('message', check=self.swear_check, timeout=10)
        except asyncio.TimeoutError:
            pass
        else:
            await self.send_message('NO U. Blame <@253354364746334212> for this useless feature.')


@register_event('awake_time_updater')
class AwakeTimeUpdater(BaseEvent):
    async def trigger(self):
        return True

    async def respond(self):
        self.user.update_awake_time()
