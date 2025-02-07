import os, aiosqlite
from time import strftime
current_directory = os.path.dirname(os.path.abspath(__file__))
MAIN_DATABASE_PATH = f'{current_directory}/data.db'

# Tables
async def create_tables():
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute('''CREATE TABLE IF NOT EXISTS admins 
                            (user_id INTEGER,
                            date TEXT)''')
        await c.execute('''CREATE TABLE IF NOT EXISTS users 
                            (user_id INTEGER,
                            balance INTEGER,
                            date TEXT)''')
        await c.execute('''CREATE TABLE IF NOT EXISTS purchases 
                            (user_id INTEGER,
                            data TEXT,
                            amount INTEGER,
                            date TEXT)''')
        await c.execute('''CREATE TABLE IF NOT EXISTS promocodes 
                            (name INTEGER,
                            amount INTEGER)''')
        await c.execute('''CREATE TABLE IF NOT EXISTS logs 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            website TEXT,
                            login TEXT,
                            password TEXT,
                            date TEXT)''')
        await c.execute('''CREATE TABLE IF NOT EXISTS banlist
                            (user_id INTEGER PRIMARY KEY,
                            ban_reason TEXT,
                            date TEXT)''')
        await db.commit()

async def add_admin(user_id):
    date = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute("INSERT INTO admins VALUES(?,?)",(user_id, date,))
        await db.commit()

async def add_ban(user_id, reason=""):
    date = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute("INSERT INTO banlist VALUES(?,?,?)",(user_id, reason, date,))
        await db.commit()

# Users
async def add_database(message):
    user_id = message.from_user.id
    time = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = await c.fetchall()
        if len(result) == 0:
            await c.execute("INSERT INTO users VALUES(?,?,?)", (user_id, 0, time,))
            await db.commit()

async def check_user(user_id):
    user_check_query = f"SELECT user_id FROM users WHERE user_id = {user_id};"
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as con:
        async with con.cursor() as cur:
            try:
                await cur.execute(user_check_query)
            except:
                pass
            user_check_data = await cur.fetchall()
            if not user_check_data:
                return False
            else:
                return True



async def get_datax_like(database, column, value, all=False):
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM {database} WHERE {column} LIKE ?", ('%' + value + '%',))

        if all:
            records = await cursor.fetchall()
            return [dict(zip([column[0] for column in cursor.description], row)) for row in records]
        else:
            record = await cursor.fetchone()
            return dict(zip([column[0] for column in cursor.description], record)) if record else None


async def update_format_args(sql, parameters: dict):
    if parameters:
        sql = f"{sql} WHERE "
        sql += " AND ".join([f"{item} = ?" for item in parameters])
        return sql, list(parameters.values())
    else:
        return sql, []

async def get_datax(file=MAIN_DATABASE_PATH,database="users", all=False, not_where=False, **kwargs):
    async with aiosqlite.connect(file) as con:
        con.row_factory = aiosqlite.Row
        _sql = f"SELECT * FROM {database}"
        sql, parameters = await update_format_args(_sql, kwargs)
        c = await con.cursor()
        if all:
            if not_where:
                await c.execute(_sql)
            else:
                await c.execute(sql, parameters)
            rows = await c.fetchall()
            return [{key: row[key] for key in row.keys()} for row in rows]
        else:
            if not_where:
                await c.execute(_sql)
            else:
                await c.execute(sql, parameters)
            row = await c.fetchone()
            return {key: row[key] for key in row.keys()} if row else ''
    
			
async def update_datax(update_parameters: dict, where_parameters: dict, database="users"):
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as con:
        con.row_factory = aiosqlite.Row
        sql = f"UPDATE {database} SET "
        set_clause = ', '.join([f'{key} = ?' for key in update_parameters.keys()])
        sql += set_clause
        sql += ' WHERE '
        where_clause = " AND ".join([f"{item} = ?" for item in where_parameters.keys()])
        sql += where_clause
        await con.execute(sql, list(update_parameters.values()) + list(where_parameters.values()))
        await con.commit()
	


async def drop_column(table, **kwargs):
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as con:
        sql, parameters = await update_format_args(f"DELETE FROM {table}", kwargs)
        c = await con.cursor()
        await c.execute(sql, parameters)
        await con.commit()

async def add_purchases(user_id, data, amount):
    date = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute("INSERT INTO purchases VALUES(?,?,?,?)",(user_id, data, amount, date,))
        await db.commit()



async def add_promo(name, amount):
    date = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute("INSERT INTO promocodes VALUES(?,?)",(name, amount,))
        await db.commit()

async def add_logs(website, login, password):
    date = strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as db:
        c = await db.cursor()
        await c.execute("INSERT INTO logs VALUES(?,?,?,?,?)",(None,website, login, password,date,))
        await db.commit()