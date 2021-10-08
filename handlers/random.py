import math
import random

from handlers.base import BaseHandler
from handlers.mixins import NonemptyMessageMixin, RateLimitMixin
from handlers.registry import register_handler

import database
from util import artfonts
from util import get_closest_user


@register_handler('wiggle')
class Wiggle(NonemptyMessageMixin, BaseHandler):
    wiggle_frequency = 10

    async def respond(self):
        content = self.content_str
        message = []
        num_wiggles = max(2000 // int(self.wiggle_frequency*1.2 + len(content) + 1), 1)
        for i in range(num_wiggles):
            num_space = int((math.sin(i/4.0)+1) * self.wiggle_frequency)
            # num_space = int((abs(math.sin(i/4.0))**0.5 + math.cos(i/4.0)**2 - 1) * 20)
            # num_space = int((abs(math.sin(i/8.0)) + abs(math.cos(i/8.0)) - 1) * 20)
            space = '\t' * (num_space // 4)
            space += ' ' * (num_space % 4)
            message.append(space + content)
        await self.send_message('\n'.join(message))


@register_handler('wall')
class Wall(NonemptyMessageMixin, BaseHandler):
    async def respond(self):
        content = self.content_str
        num = 2000 // len(content)
        await self.send_message(content * num)


@register_handler('stfu')
class STFU(BaseHandler):
    async def respond(self):
        if len(self.message.mentions) > 0:
            if self.bot.user in self.message.mentions:
                await self.send_message('YOU SHUT UP! STOP SHUTTING ME UP ' + self.discord_user.mention)
            else:
                await self.send_message('BI ZUI {}'.format(' '.join(str(user.mention)
                                                                    for user in self.message.mentions)))
        else:
            try:
                await self.send_message('BI ZUI {}'.format(
                                            get_closest_user(self.guild, self.content_str.lower()).mention))
            except AttributeError:
                await self.send_message('There are multiple people whose names are '
                                        'equally similar to "{}"'.format(self.content_str))
        await self.delete_message(self.message)


@register_handler('letter')
class Letter(NonemptyMessageMixin, BaseHandler):
    argument_name = 'word'

    async def respond(self):
        content = self.content_str
        content_len = len(content)
        if content_len > 5:
            await self.send_message('Please enter a word no greater than 5 characters.')
            return

        messages = []
        for i in range(content_len*2 - 1):
            messages.append('')
            for j in range(content_len*2 - 1):
                messages[-1] += content[content_len - max(abs(i-content_len+1), abs(j-content_len+1)) - 1] + ' '
        await self.send_message('```' + '\n'.join(messages) + '```')


@register_handler('roll')
class Roll(NonemptyMessageMixin, BaseHandler):
    argument_name = 'number of times to roll'

    async def respond(self):
        try:
            times = int(self.content[0])
            if not 1 <= times <= 100:
                raise ValueError
        except ValueError:
            await self.send_message('Cannot roll the dice {} times.'.format(self.content[0]))
            return

        message = 'The {} ...\n{}'.format('results are' if times > 1 else 'result is',
                                          ' '.join(str(random.randint(1, 6)) for i in range(times)))
        await self.send_message(message)


class QuoteBase(BaseHandler):
    quote_type = ''

    async def respond(self):
        quotes = database.get_quote(len(self.quote_type) - 1, self.guild.id)
        if len(quotes) == 0:
            await self.send_message('No {} quotes available!'.format(self.quote_type))
            return

        if len(self.content) > 0:
            match_str = self.content_str.lower().strip()
            try:
                idx = int(match_str) % len(quotes)
            except ValueError:
                indices = []
                for i, q in enumerate(quotes):
                    if match_str in q[1].lower():
                        indices.append(i)
                if len(indices) == 0:
                    await self.send_message('No such match.')
                    return
                idx = random.choice(indices)
        else:
            idx = random.randint(0, len(quotes) - 1)

        quote = quotes[idx][1]

        em = self.create_embed(self.quote_type, quote)
        em.set_footer(text='{}/{}'.format(idx + 1, len(quotes)))
        if len(self.quote_type) == 1:
            em.set_author(name=quote.split('-')[-1])
        await self.send_message(embed=em)


@register_handler('?')
class SingleQuote(QuoteBase):
    quote_type = '?'


@register_handler('??')
class DoubleQuote(QuoteBase):
    quote_type = '??'


@register_handler('art')
class Art(BaseHandler):
    background = ' '

    async def respond(self):
        content = ''.join(ch for ch in self.content_str.upper() if ch.isalnum())[:35]
        if len(content) == 0:
            await self.send_message('The art is empty due to a lack of letters and numbers.')
        else:
            count = 0
            ch = list(zip(*[[y.replace('0', x) for y in artfonts.font[x]] for x in content]))
            tmp = '\n'.join(map(''.join, ch))
            message = ''
            for ch in tmp:
                if ch == ' ':
                    message += self.background[count]
                    count = (count + 1) % len(self.background)
                else:
                    message += ch
            await self.send_message('```' + message + '```')


@register_handler('quantum')
class Quantum(NonemptyMessageMixin, BaseHandler):
    async def respond(self):
        await self.send_message('STOP MASTURBATING RANDOM {} HOLY SHIT'.format(self.content_str.upper()))


@register_handler('ping')
class Ping(RateLimitMixin, BaseHandler):
    limit_seconds = 3

    async def respond(self):
        if len(self.content) == 0:
            await self.send_message('By popular request, this feature has been removed.')
        else:
            if len(self.message.mentions) > 1:
                await self.send_message('Only one ping per message!')
            elif len(self.message.mentions) == 1:
                await self.send_message(self.message.mentions[0].mention)
            else:
                try:
                    await self.send_message(get_closest_user(self.guild, self.content_str, include_bots=True).mention)
                except AttributeError:
                    await self.send_message('There are multiple people whose names are '
                                            'equally similar to "{}"'.format(self.content_str))
        await self.delete_message(self.message)
