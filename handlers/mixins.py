import settings
import time


class AdminRequiredMixin:
    async def initialize(self):
        if self.user.id not in settings.ADMIN:
            await self.send_message('Only an administrator may use this command.')
            return
        await super(AdminRequiredMixin, self).initialize()


class NonemptyMessageMixin:
    argument_name = 'message'

    async def initialize(self):
        if len(self.content) == 0:
            await self.send_message('Please enter a(n) {}.'.format(self.argument_name))
            return
        await super(NonemptyMessageMixin, self).initialize()


class RateLimitMixin:
    limit_seconds = 5

    async def initialize(self):
        _now = time.time()
        if _now - self.user.rate_limit[self.__class__] < self.limit_seconds:
            await self.send_message('YOU ARE BEING RATE LIMITED! Please wait before using this command.' +
                                    self.discord_user.mention)
            return
        self.user.rate_limit[self.__class__] = _now

        await super(RateLimitMixin, self).initialize()
