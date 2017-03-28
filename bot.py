from chunnel.socket import Socket
import config
import asyncio
import sqlite3
import re

# takes a question and should return a list of 1 to 20 possible answers
def answer(q):
    # while you should do something fancy here,
    # I'm just going try all words in the question
    answers = re.findall("\w+", q)

    return answers

# optional persistent storage of questions and answers
conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute('create table if not exists challenges (id int, q int, success int)')
c.execute('create table if not exists answers (challenge_id int, a string)')
conn.commit()

# this works out of the box
async def qa():
    socket = Socket(config.host + '/bots/websocket', params={'token': config.token})
    async with socket:
        channel = socket.channel('bots', {})
        await channel.join()
        while True:
            incoming = await channel.receive()
            if incoming.event == 'q':
                p = incoming.payload
                c.execute('insert into challenges values(?, ?, ?)', (p['id'], p['q'], None))
                conn.commit()
                answers = answer(p['q'])[0:20]
                answer_payload = {'id': p['id'], 'answers': [{'a': a} for a in answers]}
                ref = await channel.push('a', answer_payload)
                print('hey')
                resp = await ref.response()
                print(resp)

loop = asyncio.get_event_loop()
# this will go on forever
loop.run_until_complete(qa())
loop.close()
