import discord

import database
import settings


class BaseHandler:
    user = None
    content = ''
    message = None

    async def respond(self):
        raise NotImplementedError()

    async def initialize(self):
        await self.respond()

    async def dispatch(self, **kwargs):
        self.message = kwargs.pop('message', None)
        self.content = kwargs.pop('content', None)
        self.user = kwargs.pop('user', await database.load_user(self.message.author.id))
        self.discord_user = await self.user.discord_user
        self.kwargs = kwargs

        await self.initialize()

    @property
    def content_str(self):
        return ' '.join(self.content)

    @property
    def channel(self):
        return getattr(self.message, 'channel', None)

    @property
    def server(self):
        return getattr(self.message, 'server', None)

    @property
    def bot(self):
        return database.bot

    @classmethod
    def create_embed(cls, title=None, description=None, colour=settings.BOT_COLOUR):
        return discord.Embed(title=title, description=description, colour=colour)

    async def send_message(self, content=None, embed=None):
        if self.user.id not in settings.BANNED_USERS:
            return await self.bot.send_message(self.channel, content=content, embed=embed)
        return None

    async def send_file(self, location):
        if self.user.id not in settings.BANNED_USERS:
            return await self.bot.send_file(self.channel, location)
        return None

    async def delete_message(self, message):
        await self.bot.delete_message(message)


class BaseEvent(BaseHandler):
    async def trigger(self):
        raise NotImplementedError()

    async def initialize(self):
        if await self.trigger():
            await self.respond()
