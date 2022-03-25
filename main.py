import logging

import discord
import database
import settings
from handlers import event_classes, handler_classes


intents = discord.Intents.default()
intents.members = True
database.bot = discord.Client(max_messages=1000, intents=intents)


@database.bot.event
async def on_ready():
    await database.load_db()
    await database.bot.user.edit(username=settings.BOT_NAME)
    logging.basicConfig(format=settings.LOGGER_FORMAT,
                        filename=settings.LOGGER_FILE, level=logging.INFO)

    print('Logged in as')
    print(database.bot.user.name)
    print(database.bot.user.id)
    print('------')


async def process_command(message, content):
    # dirty way of doing this
    for i in range(len(content)):
        command = ' '.join(content[:i+1])
        if command in handler_classes.keys():
            await handler_classes[command]().dispatch(message=message, content=content[i+1:])


@database.bot.event
async def on_message(message):
    if message.author.bot or database.loading:
        return
    await database.load_user(message.author.id)

    for name, event in event_classes.items():
        await event().dispatch(message=message, content=message.content.split(' '))

    if message.author.id in settings.BANNED_USERS:
        return

    if message.type == discord.MessageType.default and message.content.startswith(settings.COMMAND_PREFIX):
        stripped_message = message.content.lstrip(settings.COMMAND_PREFIX).strip().split(' ')
        await process_command(message, stripped_message)


@database.bot.event
async def on_message_edit(before, after):
    if after.author.bot or database.loading:
        return

    for name, event in event_classes.items():
        await event().dispatch(message=after, content=after.content.split(' '), before=before)


def run_bot():
    try:
        database.bot.loop.run_until_complete(database.bot.start(settings.TOKEN))
    except KeyboardInterrupt:
        database.bot.loop.run_until_complete(database.bot.close())
    finally:
        database.bot.loop.close()


if __name__ == '__main__':
    run_bot()
