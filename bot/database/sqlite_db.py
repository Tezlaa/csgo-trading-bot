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
        
    base.execute('CREATE TABLE IF NOT EXISTS profile(\
 user_id TEXT PRIMARY KEY, name TEXT, balance INTEGER, admin INTEGER\
 )')
    base.commit()


async def create_profile(user_id, username):
    user = cur.execute(f'SELECT 1 FROM profile WHERE user_id == {user_id}').fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?, ?, ?, ?)", (user_id, username, 15, 0))
        base.commit()
