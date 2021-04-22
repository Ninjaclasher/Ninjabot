import asyncio
import logging
import random

from functools import cached_property

from handlers.base import BaseEvent
from handlers.registry import register_event

import settings


logger = logging.getLogger('ninjabot.handler')


@register_event('server_leaver')
class ServerLeaver(BaseEvent):
    async def trigger(self):
        return True

    async def respond(self):
        if self.guild.id not in settings.WHITELISTED_SERVERS:
            logger.warn('Left guild %s with id %s.', self.guild.name, self.guild.id)
            await self.guild.leave()


@register_event('reaction_adder')
class ReactionAdder(BaseEvent):
    async def trigger(self):
        return random.random() <= 0.005 and len(self.guild.emojis) > 0

    async def respond(self):
        try:
            await self.message.add_reaction(random.choice(self.guild.emojis))
        except Exception:
            logger.warn("Failed to add a reaction to %s (%s)'s message.", self.author, self.author.id)
        else:
            logger.info("Added a reaction to %s (%s)'s message.", self.author, self.author.id)


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

    @cached_property
    def response_type(self):
        return settings.SWEAR_USER_CUSTOM_TYPE.get(
            self.user.id,
            settings.SWEAR_GUILD_CUSTOM_TYPE.get(
                self.guild.id,
                settings.SWEAR_DEFAULT_TYPE,
            ),
        )

    async def create_response(self):
        if self.response_type == 'message':
            await self.send_message(':x: {}'.format(self.author.mention))
        elif self.response_type == 'react':
            await self.message.add_reaction('\u274c')

    async def respond(self):
        await self.create_response()
        logger.info('%s (%s) swore, updated counter.', await self.user.discord_user, self.user.id)
        self.user.times_swore += 1
        self.user.save()
        if self.response_type == 'none':
            return
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
