from handlers.base import BaseHandler
from handlers.registry import register_handler

import database


@register_handler('user')
class UserInfo(BaseHandler):
    async def respond(self):
        try:
            user = await database.load_user(self.message.mentions[0].id)
        except IndexError:
            user = self.user
        else:
            user.update_awake_time()

        em = self.create_embed('{} Info'.format(await user.discord_user))
        em.add_field(name='Times Swore', value='{}'.format(user.times_swore))
        em.add_field(name='Maximum Awake Time', value='{:.1f} Hours'.format(user.max_awake_time))
        em.add_field(name='Current Awake Time', value='{:.1f} Hours'.format(user.awake_time))

        await self.send_message(embed=em)


class RankingBase(BaseHandler):
    empty_queryset_message = ''
    ranking_size = 10

    def queryset_filter(self, obj):
        raise NotImplementedError()

    def queryset_sort(self, obj):
        raise NotImplementedError()

    async def get_display_row(self, obj):
        raise NotImplementedError()

    async def get_title(self):
        return ''

    async def get_queryset(self):
        return list(filter(self.queryset_filter, database.users.values()))

    async def get_sorted_queryset(self):
        queryset = await self.get_queryset()
        queryset.sort(key=self.queryset_sort, reverse=True)
        return queryset

    async def respond(self):
        queryset = (await self.get_sorted_queryset())[:self.ranking_size]
        queryset = [await self.get_display_row(rank, obj) for rank, obj in enumerate(queryset, 1)]

        if len(queryset) == 0:
            await self.send_message(self.empty_queryset_message)
            return

        await self.send_message(embed=self.create_embed(await self.get_title(), '\n'.join(queryset)))


@register_handler('awakelb')
class UserAwakeRanking(RankingBase):
    empty_queryset_message = 'No one is awake. :thinking:'

    def queryset_filter(self, user):
        return user.max_awake_time > 0

    def queryset_sort(self, user):
        return user.max_awake_time

    async def get_title(self):
        return 'Who is awake the longest'

    async def get_display_row(self, rank, user):
        return '{:.1f} Hours - {}'.format(user.max_awake_time, await user.discord_user)


@register_handler('profanitylb')
class UserProfanityRanking(RankingBase):
    empty_queryset_message = 'No one has sworn yet.'

    def queryset_filter(self, user):
        return user.times_swore > 0

    def queryset_sort(self, user):
        return user.times_swore

    async def get_title(self):
        return 'Who swears the most'

    async def get_display_row(self, rank, user):
        return '{} - {}'.format(user.times_swore, await user.discord_user)
