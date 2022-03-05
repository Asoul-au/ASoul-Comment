import asyncio
import re
import sqlite3

import qqbot


async def formatComment(input: str) -> str:
    linkMatch = re.compile(
        r'((((ht|f)tp(s?))\://)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\;\?\'\\\+&%\$#\=~_\-]+))*)')
    input = linkMatch.sub("[链接已屏蔽]", input)
    formatter = re.compile(r"回复 @.*? :")
    return formatter.sub("", input)


def toUrl(avid: int):
    return f"https://www.bilibili.com/video/av{str(avid)}"


async def _commentToStr(input: tuple):
    tmp = await formatComment(input[8])
    if input[6] != 'None':
        return f"\n|  评论ID：{input[0]}\n|  评论作者：{input[2]} {input[6]}:[{input[7]}]\n|  作者uid：{input[3]}\n|  发表于视频：{'av' + str(input[1])}\n\n全文如下：\n\n{tmp}\n\n======"
    else:
        return f"\n|  评论ID：{input[0]}\n|  评论作者：{input[2]}\n|  作者uid：{input[3]}\n|  发表于视频：{'av' + str(input[1])}\n\n全文如下：\n\n{tmp}\n\n======"


async def _handle_message(event, message: qqbot.Message):
    _re_search = re.compile(r'查询小作文')
    _re_find_comment_all = re.compile(r"查评论成分")
    _re_find_uid_all = re.compile(r"查成分")
    if (_re_search.search(message.content) != None):
        await _search_comment(event, message)
    elif (_re_find_comment_all.search(message.content) != None):
        await _find_comment_all(event, message)
    elif (_re_find_uid_all.search(message.content) != None):
        await _find_uid_all(event, message)
    pass


async def _search_comment(event, message: qqbot.Message):
    checked = False
    while not checked:
        c.execute("SELECT * FROM DCOMMENTS ORDER BY random() LIMIT 1")
        res = c.fetchall()
        if (res[0][2] <= 1):
            checked = True
    c.execute(f"SELECT * FROM COMMENTS WHERE ID={res[0][0]}")
    result = c.fetchall()[0]
    ids[message.channel_id] = result[0]
    reply = f"小作文查询功能：\n {await _commentToStr(result)}"
    await asyncio.sleep(1)
    send = qqbot.MessageSendRequest(f"{reply}", message.id)
    await msg_api.post_message(message.channel_id, send)


async def _find_uid_all(event, message: qqbot.Message, uid=None):
    if (uid == None):
        _find_uid = re.compile(r'\d+')
        uid = _find_uid.findall(message.content)[1]
    c.execute(f"SELECT * FROM COMMENTS WHERE USERID={uid}")
    res = c.fetchall()
    count = 1
    for _res in res:
        print(_res)
        ids[message.channel_id] = _res[0]
        reply = f"查询到第{count}条评论，共{len(res)}条：\n {await _commentToStr(_res)}"
        await asyncio.sleep(1)
        send = qqbot.MessageSendRequest(f"{reply}", message.id)
        await msg_api.post_message(message.channel_id, send)
        count += 1
    pass


async def _find_comment_all(event, message: qqbot.Message):
    _find_comment_id = re.compile(r'\d+')
    comment_id = _find_comment_id.findall(message.content)[1]
    print(message.content, comment_id)
    c.execute(f"SELECT * FROM COMMENTS WHERE ID={comment_id}")
    id = c.fetchall()[0][3]
    print(id)
    await _find_uid_all(event, message, id)


if __name__ == "__main__":
    database = sqlite3.connect("../storage.db", check_same_thread=False)
    c = database.cursor()
    ids = dict()  # the last id queried
    token = qqbot.Token("101994963", "KvvzQ1Yzn5gEMv4WDfDDUCpqA9VXQIhb")
    msg_api = qqbot.AsyncMessageAPI(token, False)
    handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _handle_message)
    qqbot.async_listen_events(token, True, handler)
