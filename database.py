import pymysql
import threading

from collections import defaultdict

import settings


discord_users_list = {}
users = {}
bot = None
loading = True


class DatabaseManager:
    def __init__(self):
        self.db = pymysql.connect(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_DATABASE)
        self.lock = defaultdict(lambda: threading.RLock())

    @classmethod
    def sql_format(cls, arr):
        return ', '.join(['%s']*len(arr))

    @classmethod
    def parse_args(cls, *args):
        return tuple(x for x in args if x is not None)

    def insert(self, table, values):
        with self.lock['read'] and self.lock['write'], self.db.cursor() as cursor:
            cursor.execute("""\
                INSERT INTO {0} VALUES ({1})
            """.format(table, self.sql_format(values)), values
            )
            self.db.commit()
            return cursor.lastrowid

    def select(self, table, where_condition='', values=(), extra=''):
        with self.lock['read'], self.db.cursor() as cursor:
            cursor.execute("""\
                SELECT *
                FROM {0}
                    {1}
                    {2}
            """.format(table, 'WHERE ' + where_condition if where_condition != '' else '', extra), values
            )
            return cursor.fetchall()

    def update(self, table, id, field, value):
        with self.lock['read'] and self.lock['write'], self.db.cursor() as cursor:
            cursor.execute("""\
                UPDATE {0}
                SET {1} = %s
                WHERE id = %s
            """.format(table, field), (value, id)
            )
            self.db.commit()

mgr = DatabaseManager()

def get_quote(typ):
    return mgr.select('ninjabot_quote', 'type = %s', (typ,))

def add_quote(quote, typ):
    mgr.insert('ninjabot_quote', values=(None, quote, typ))

def save_user(user):
    mgr.update('ninjabot_user', user.id, 'username', user.username)
    mgr.update('ninjabot_user', user.id, 'times_swore', user.times_swore)
    mgr.update('ninjabot_user', user.id, 'awake_time_start', user.awake_time_start)
    mgr.update('ninjabot_user', user.id, 'awake_time_current', user.awake_time_current)
    mgr.update('ninjabot_user', user.id, 'max_awake_time', user.max_awake_time)

async def load_discord_user(id):
    if id not in discord_users_list.keys():
        discord_users_list[id] = await bot.fetch_user(id)
    return discord_users_list[id]

async def load_users():
    from models import User
    for x in mgr.select('ninjabot_user'):
        users[x[0]] = User(*x)

async def load_user(id):
    global users
    if id not in users.keys():
        from models import User
        users[id] = User(id=id, username=str(await load_discord_user(id)))
        mgr.insert('ninjabot_user', users[id].db_save)
    return users[id]

async def load_db():
    global loading
    await load_users()
    loading = False

