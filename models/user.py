from collections import defaultdict
import datetime

import database

EPOCH = datetime.datetime(1970, 1, 1)


class User:
    db_fields = ('id', 'username', 'times_swore', 'awake_time_start', 'awake_time_current', 'max_awake_time')

    def __init__(self, id, username='', times_swore=0, awake_time_start=EPOCH,
                 awake_time_current=EPOCH, max_awake_time=0.0):
        self.id = id
        self.username = username
        self.rate_limit = defaultdict(lambda: 0.0)
        self.times_swore = times_swore
        self.awake_time_start = EPOCH if type(awake_time_start) == str else awake_time_start
        self.awake_time_current = EPOCH if type(awake_time_current) == str else awake_time_current
        self.max_awake_time = max_awake_time

    def __eq__(self, other):
        return self.id == other.id

    def save(self):
        database.save_user(self)

    @property
    def db_save(self):
        return tuple(getattr(self, field) for field in self.db_fields)

    @property
    def awake(self):
        return (datetime.datetime.now()-self.awake_time_current).total_seconds() <= 3600

    @property
    def awake_time(self):
        return ((self.awake_time_current - self.awake_time_start).total_seconds()/3598 + 1.0)

    def reset_awake_time(self, new_value=EPOCH):
        self.awake_time_start = new_value
        self.awake_time_current = new_value

    def update_awake_time(self):
        _now = datetime.datetime.now()
        if not self.awake:
            self.reset_awake_time(new_value=_now)
        else:
            self.awake_time_current = _now
        self.max_awake_time = max(self.max_awake_time, self.awake_time)
        self.save()

    @property
    async def discord_user(self):
        user = await database.load_discord_user(self.id)
        if str(user) != self.username:
            self.username = str(user)
            self.save()
        return user
