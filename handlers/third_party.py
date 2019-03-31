import asyncio
import logging
import os
import re
import threading

from hashlib import sha512
from operator import itemgetter

from handlers.base import BaseHandler
from handlers.mixins import NonemptyMessageMixin, RateLimitMixin
from handlers.registry import register_handler

import settings
from mcstatus import MinecraftServer


"""
Source: https://github.com/ivanseidel/Is-Now-Illegal
"""
@register_handler('illegal')
class IllegalGIF(NonemptyMessageMixin, RateLimitMixin, BaseHandler):
    @classmethod
    def escape(cls, s):
        return s.replace('"', '\\"').replace('`', '\\`')

    @classmethod
    def has_file(cls, filename):
        return filename in os.listdir(os.path.join(settings.ILLEGAL_DIR, 'illegal_gifs'))

    async def wait_generation(self, filename, thread=None):
        while True:
            if thread is None or not thread.is_alive():
                if self.has_file(filename):
                    await self.send_file(os.path.join(settings.ILLEGAL_DIR, 'illegal_gifs', filename))
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
            except:
                break

        if len(gif_message) >= 15:
            await self.send_message('Only sentences less than 15 characters are allowed.')
            return

        logging.info('Generating illegal GIF with message "{}"'.format(gif_message))

        filename = sha512(gif_message.encode('utf-8')).hexdigest() + '.gif'
        filename = filename.strip()
        if self.has_file(filename):
            logging.info('Illegal GIF with message "{}" already exists. Sending and returning.'.format(gif_message))
            await self.bot.loop.create_task(self.wait_generation(filename))
            return
        msg = await self.send_message(self.discord_user.mention + ', please wait while the GIF is generated.')
        try:
            command = 'cd {directory} && python3 rotoscope/generate.py "{content}" GIF/Trump/ "../illegal_gifs/{filename}"'
            t = threading.Thread(target=os.system,
                                 args=(command.format(directory=settings.ILLEGAL_DIR,
                                                      content=self.escape(gif_message),
                                                      filename=filename
                                                     ),
                                ))
            t.start()
            await self.bot.loop.create_task(self.wait_generation(filename, t))
        except:
            logging.error('Failed to generate illegal GIF with message "{}".'.format(gif_message))
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
        logging.info('Querying minecraft server with IP {}.'.format(address))
        try:
            status = server.status().raw
            
            try:
                name = status['description']['text']
            except:
                name = status['description']

            online_players = status['players']['online']
            max_players = status['players']['max']

            em = self.create_embed('Minecraft Server Status', 'Server query to {}'.format(address), colour=0xFF630A)
            em.add_field(name='Name', value=name)
            em.add_field(name='Version', value=status['version']['name'])
            em.add_field(name='Ping', value=str(server.ping()))

            players = ['No one is online right now.']
            if online_players > 0:
                players = list(map(itemgetter('name'), status['players']['sample']))


            em.add_field(name='Online Players ({}/{})'.format(online_players, max_players), value='\n'.join(players))
            await self.send_message(embed=em)
        except:
            await self.send_message('Could not query the server. Please check that the address is correct.')
