import datetime
import random

from handlers.base import BaseHandler
from handlers.registry import register_handler


EPOCH = datetime.datetime(1970, 1, 1)


@register_handler('ratespice')
class RateSpice(BaseHandler):
    async def respond(self):
        user = self.discord_user
        if len(self.message.mentions) == 1:
            user = self.message.mentions[0]
        rng = random.Random()
        rng.seed(int(user.id) * (datetime.datetime.now() - EPOCH).days)
        # Temporary spice formula
        spice = int(rng.lognormvariate(0, 4)*300)
        await self.send_message(spice)
