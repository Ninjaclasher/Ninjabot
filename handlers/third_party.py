import asyncio
import logging
import os
import re
import requests
import subprocess
import sys
import threading

from hashlib import sha512
from operator import itemgetter

from handlers.base import BaseHandler
from handlers.mixins import NonemptyMessageMixin, RateLimitMixin
from handlers.registry import register_handler

import settings
from mcstatus import MinecraftServer


logger = logging.getLogger('ninjabot.handler')


"""
Source: https://github.com/ivanseidel/Is-Now-Illegal
"""
@register_handler('illegal')
class IllegalGIF(NonemptyMessageMixin, RateLimitMixin, BaseHandler):
    async def wait_generation(self, file_location, thread=None):
        while True:
            if thread is None or not thread.is_alive():
                if os.path.isfile(file_location):
                    await self.send_file(file_location)
                    return
                else:
                    raise OSError
            await asyncio.sleep(0.4)

    async def respond(self):
        gif_message = self.content_str
        while True:
            match = re.search('<(:[A-Z]+:)[0-9]+>', gif_message)
            try:
                gif_message = gif_message.replace(match.group(0), match.group(1))
            except Exception:
                break

        if len(gif_message) >= 15:
            await self.send_message('Only sentences less than 15 characters are allowed.')
            return

        logger.info('Generating illegal GIF with message "%s"', gif_message)

        filename = sha512(gif_message.encode('utf-8')).hexdigest() + '.gif'
        file_location = os.path.join(settings.ILLEGAL_CACHE, filename)

        if os.path.isfile(file_location):
            logger.info('Illegal GIF with message "%s" already exists. Sending and returning.', gif_message)
            await self.bot.loop.create_task(self.wait_generation(file_location))
            return
        msg = await self.send_message(self.discord_user.mention + ', please wait while the GIF is generated.')
        try:
            t = threading.Thread(
                target=subprocess.run,
                args=([
                    sys.executable, os.path.join(settings.ILLEGAL_DIR, 'rotoscope', 'generate.py'),
                    gif_message, os.path.join(settings.ILLEGAL_DIR, 'rotoscope', 'GIF', 'Trump'),
                    file_location,
                ],),
            )
            t.start()
            await self.bot.loop.create_task(self.wait_generation(file_location, t))
        except Exception:
            logger.error('Failed to generate illegal GIF with message "%s".', gif_message)
            await self.send_message('Generation of the GIF failed for an unknown reason...')
        await self.delete_message(msg)


"""
Source: https://github.com/Dinnerbone/mcstatus
"""
@register_handler('mcstatus')
class MCStatus(NonemptyMessageMixin, RateLimitMixin, BaseHandler):
    argument_name = 'address'

    async def respond(self):
        address = self.content[0].strip()
        server = MinecraftServer.lookup(address)
        logger.info('Querying minecraft server with IP %s.', address)
        try:
            status = server.status().raw

            if isinstance(status['description'], dict):
                name = status['description']['text']
            else:
                name = status['description']

            online_players = status['players']['online']
            max_players = status['players']['max']

            em = self.create_embed('Minecraft Server Status', 'Server query to {}'.format(address), colour=0xFF630A)
            if name:
                em.add_field(name='Name', value=name)
            em.add_field(name='Version', value=status['version']['name'])
            em.add_field(name='Ping', value=str(server.ping()))

            players = ['No one is online right now.']
            if online_players > 0:
                players = list(map(itemgetter('name'), status['players']['sample']))

            em.add_field(name='Online Players ({}/{})'.format(online_players, max_players), value='\n'.join(players))
            await self.send_message(embed=em)
        except Exception as e:
            logger.warn('Failed to query %s. %s', address, e)
            await self.send_message('Could not query the server. Please check that the address is correct.')


@register_handler('inspire')
class Inspire(RateLimitMixin, BaseHandler):
    limit_seconds = 1

    async def respond(self):
        await self.send_message(requests.get('http://inspirobot.me/api?generate=true').text)
