import logging
import sqlite3


async def sql_start():
    global base, cur
    
    base = sqlite3.connect("csTraging.db")
    cur = base.cursor()
    
    if base:
        logging.info('Data base connected!')
    else:
        logging.info(base)
        
    base.execute("""CREATE TABLE IF NOT EXISTS profile(
        user_id TEXT PRIMARY KEY,
        name TEXT,
        balance INTEGER,
        all_top_up_balance INTEGER,
        admin INTEGER
        )""")
    base.commit()


async def create_profile(user_id, username):
    user = cur.execute(f'SELECT 1 FROM profile WHERE user_id == {user_id}').fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?, ?, ?, ?, ?)", (user_id, username, 15, 0, 0))
        base.commit()


async def get_admin_id() -> list:
    result = []
    for user in cur.execute(f"SELECT user_id FROM profile WHERE admin = '{1}'"):
        result += user
        
    return result


async def get_balance_user(user_id: str) -> int:
    balance_user = int(cur.execute(f"SELECT balance FROM profile WHERE user_id = {user_id}").fetchone()[0])
    return balance_user


async def get_all_top_up(user_id: str) -> int:
    all_top_up = int(cur.execute(f"SELECT all_top_up_balance FROM profile WHERE user_id = {user_id}").fetchone()[0])
    return all_top_up 
    

async def unbalance(how_much: str, user_id: str):
    balance_user = await get_balance_user(user_id)
    if balance_user > int(how_much):
        cur.execute("UPDATE profile SET balance=? WHERE user_id=?", (str((balance_user - int(how_much))), user_id))
        base.commit()
    else:
        raise ValueError()  # if not enough balance
    

async def top_up_balance(how_much: str, user_id):
    balance_user = await get_balance_user(user_id)
    top_up = str((balance_user + int(how_much)))
    cur.execute("UPDATE profile SET balance=? AND all_top_up_balance=? WHERE user_id=?",
                (top_up, top_up, user_id))
    base.commit()