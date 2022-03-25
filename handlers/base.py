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
        ping_checks = ('everyone', 'here')
        for ping in ping_checks:
            if '@' + ping in self.content_str.lower():
                await self.send_message(':angry: NO MENTIONING {} :angry:'.format(ping.upper()))
                return
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
    def author(self):
        return getattr(self.message, 'author', None)

    @property
    def channel(self):
        return getattr(self.message, 'channel', None)

    @property
    def guild(self):
        return getattr(self.message, 'guild', None)

    @property
    def bot(self):
        return database.bot

    @classmethod
    def create_embed(cls, title='', description='', colour=settings.BOT_COLOUR):
        return discord.Embed(title=title, description=description, colour=colour)

    async def send_message(self, *args, **kwargs):
        if self.user.id not in settings.BANNED_USERS:
            return await self.channel.send(*args, **kwargs)
        return None

    async def send_file(self, location):
        return await self.send_message(file=discord.File(location))

    async def delete_message(self, message):
        await message.delete()


class BaseEvent(BaseHandler):
    async def trigger(self):
        raise NotImplementedError()

    async def initialize(self):
        if await self.trigger():
            await self.respond()
