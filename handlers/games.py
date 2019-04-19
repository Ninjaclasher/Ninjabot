import random

from handlers.base import BaseHandler
from handlers.registry import register_handler


@register_handler('minesweeper')
class Minesweeper(BaseHandler):
    def sanitize(self, value):
        value = int(value)
        if not 2 <= value <= 11:
            raise ValueError
        return value

    async def respond(self):
        try:
            height = self.sanitize(self.content[0])
        except (IndexError, ValueError):
            height = 8
        try:
            length = self.sanitize(self.content[1])
        except (IndexError, ValueError):
            length = 8

        grid = [[0 for x in range(length)] for y in range(height)]
        bombs = random.randint(1, max(1, height*length // 4))
        for i in range(bombs):
            x = random.randint(0, height-1)
            y = random.randint(0, length-1)
            grid[x][y] = None
        for x in range(height):
            for y in range(length):
                if grid[x][y] is None:
                    continue
                for xx in range(-1, 2):
                    for yy in range(-1, 2):
                        if 0 <= x+xx < height and 0 <= y+yy < length and grid[x+xx][y+yy] is None:
                            grid[x][y] += 1
        emoji_convert = {
            None: 'bomb',
            0: 'zero',
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
            7: 'seven',
            8: 'eight',
        }
        msg = [':arrow_down_small:' * length]
        for x in range(height):
            msg.append('')
            for y in range(length):
                msg[-1] += '||:{}:||'.format(emoji_convert[grid[x][y]])
        msg.append(':arrow_up_small:' * length)
        await self.send_message('\n'.join(msg))
