from chunnel.socket import Socket
import config
import asyncio
import sqlite3

conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute('create table if not exists challenges (id int, q int, success int)')
c.execute('create table if not exists answers (challenge_id int, a string)')
conn.commit()

async def qa():
    socket = Socket(config.host + '/bots/websocket', params={'token': config.token})
    async with socket:
        channel = socket.channel('bots', {})
        await channel.join()
        incoming = await channel.receive()
        p = incoming.payload
        c.execute('insert ?, ? into challenges', (p['id'], p['q']))
        conn.commit()
        answers = get_answers(p['q'])
        answer_payload = {'answers': [{'a': a} for a in answers]}
        channel.push('a', answer_payload)

loop = asyncio.get_event_loop()
# Blocking call which returns when the display_date() coroutine is done
loop.run_until_complete(qa())
loop.close()
