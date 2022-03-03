import sqlite3

import nonebot
from nonebot import on_command, CommandSession

import config

database = sqlite3.connect("storage.db", check_same_thread=False)
c = database.cursor()
last = 0


def toUrl(avid: int):
    return f"https://www.bilibili.com/video/av{str(avid)}"


@on_command('查询小作文', only_to_me=False)
async def test(session: CommandSession):
    checked = False
    while not checked:
        c.execute("SELECT * FROM DCOMMENTS ORDER BY random() LIMIT 1")
        res = c.fetchall()
        if (res[0][2] <= 1):
            checked = True
    print(res[0][0])
    c.execute(f"SELECT * FROM COMMENTS WHERE ID={res[0][0]}")
    result = c.fetchall()[0]
    print(result)
    last = result[0]
    await session.send(
        f"已查询到一篇小作文：\n作者：{result[2]} [{result[6]}]:[{result[7]}]\n发表于视频：{toUrl(result[1])}\n全文如下：\n\n{result[8]}")


@on_command('这不是小作文', only_to_me=False)
async def complain(session: CommandSession):
    c.execute(f"UPDATE DCOMMENTS SET CONS=1 WHERE ID={last}")
    database.commit()
    await session.send(f"已收到反馈。")


if __name__ == '__main__':
    nonebot.init(config)
    nonebot.run(host='127.0.0.1', port=3421)
