import asyncio
import getopt
import logging
import os.path
import sqlite3
import sys
import uvicorn
from bilibili_api import comment
from bilibili_api.user import User
from bilibili_api.comment import OrderType

uids = [672328094, 672353429, 672346917, 672342685, 351609538]
logging.basicConfig(level=logging.DEBUG, filename=".fetch.log", filemode="a",
                    format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s@%(lineno)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


async def getFullCommentsFromDynamic(oid: int) -> list:
    comments = []
    page = 1
    commentCount = 0
    while True:
        await asyncio.sleep(1)
        tmp = await comment.get_comments(oid, comment.ResourceType.DYNAMIC, page)
        for _tmp in tmp['replies']:
            _tmp['oid'] = oid
            for _stmp in _tmp['replies']:
                _stmp['oid'] = oid
        comments.extend(tmp['replies'])
        commentCount += tmp['page']['size']
        page += 1
        if commentCount >= tmp['page']['acount']:
            break
    return comments


async def getFullCommentsFromVideo(avid: int) -> list:
    comments = []
    page = 1
    commentCount = 0
    while True:
        await asyncio.sleep(1)
        tmp = await comment.get_comments(avid, comment.ResourceType.VIDEO, page)
        for _tmp in tmp['replies']:
            _tmp['vid'] = avid
            for _stmp in _tmp['replies']:
                _stmp['vid'] = avid
        comments.extend(tmp['replies'])
        commentCount += tmp['page']['size']
        page += 1
        if commentCount >= tmp['page']['acount']:
            break
    return comments


async def getVideoList(_user: User) -> list:
    page = 1
    videos = []
    while True:
        await asyncio.sleep(1)
        tmp = await _user.get_videos(page)
        videos.extend(tmp['list']['vlist'])
        if page * 30 >= tmp['page']['count']:
            break
        page += 1
    return videos


async def getDynamicList(_user: User) -> list:
    offset = 0
    dynamics = []
    while True:
        page = await _user.get_dynamics(offset)
        if 'cards' in page:
            dynamics.extend(page['cards'])
        if page['has_more'] != 1:
            break
        offset = page['next_offset']
    return dynamics


def createDatabase():
    database_location = os.path.abspath(os.path.join("..", "storage.db"))
    if os.path.exists(database_location):
        raise FileExistsError("storage.db already exists")
    database = sqlite3.connect(database_location)
    cursor = database.cursor()
    cursor.execute('''CREATE TABLE VIDEOS
                (ID INT PRIMARY KEY NOT NULL,
                 AVID INT NOT NULL,
                 TITLE TEXT,
                 COVERIMG TEXT,
                 VIEW INT,
                 DATE INT);''')
    cursor.execute('''CREATE TABLE COMMENTS
                (ID INT PRIMARY KEY NOT NULL,
                 AVID INT NOT NULL,
                 USERNAME TEXT NOT NULL,
                 USERID INT NOT NULL,
                 DATE INT,
                 LIKE INT,
                 FAN_TYPE TXT,
                 FAN_LEVEL INT,
                 CONTENT TEXT NOT NULL,
                 CONTENTTYPE INT);''')
    cursor.execute('''CREATE TABLE DYNAMICS
                    (ID INT PRIMARY KEY NOT NULL,
                     OID INT NOT NULL,
                     CONTENT TEXT,
                     DATE INT);''')
    database.commit()
    cursor.close()


def removeDatabase():
    database_location = os.path.abspath(os.path.join("..", "storage.db"))
    if not os.path.exists(database_location):
        raise FileNotFoundError("storage.db don't exist")
    os.remove(database_location)


def updateDatabaseFull():
    database_location = os.path.abspath(os.path.join("..", "storage.db"))
    if not os.path.exists(database_location):
        createDatabase()
    database = sqlite3.connect(database_location)
    cursor = database.cursor()

    loop = asyncio.get_event_loop()

    videos = []
    dynamics = []

    for uid in uids:
        tmp = loop.create_task(getVideoList(User(uid)))
        loop.run_until_complete(tmp)
        videos.extend(tmp.result())

        tmp = loop.create_task(getDynamicList(User(uid)))
        loop.run_until_complete(tmp)
        dynamics.extend(tmp.result())

    for video in videos:
        cursor.execute(f"SELECT * FROM VIDEOS WHERE ID={video['created']}")
        if len(cursor.fetchall()):
            continue
        else:
            cursor.execute(f"INSERT INTO VIDEOS (ID,AVID,TITLE,COVERIMG,VIEW,DATE)\
                    VALUES (?,?,?,?,?,?)", (
                video['created'], video['aid'], video['title'], video['pic'], video['play'], video['created']))

    for dynamic in dynamics:
        cursor.execute(f"SELECT * FROM DYNAMICS WHERE ID={dynamic['desc']['timestamp']}")
        if (len(cursor.fetchall())):
            continue
        else:
            if 'title' in dynamic['card']:
                content = dynamic['card']['title']
            elif 'content' in dynamic['card']['item']:
                content = dynamic['card']['item']['content']
            else:
                content = dynamic['card']['item']['description']
            cursor.execute(f"INSERT INTO DYNAMICS (ID, OID, CONTENT, DATE)\
                            VALUES (?,?,?,?)", (
                dynamic['desc']['timestamp'], dynamic['desc']['dynamic_id'], content, dynamic['desc']['timestamp']))

    comments = []

    for video in videos[1:2]:
        tmp = loop.create_task(getFullCommentsFromVideo(video['aid']))
        loop.run_until_complete(tmp)
        comments.extend(tmp.result())

    for dynamic in dynamics[1:2]:
        tmp = loop.create_task(getFullCommentsFromDynamic(dynamic['desc']['dynamic_id']))
        loop.run_until_complete(tmp)
        comments.extend(tmp.result())
    pass


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # t = loop.create_task(getDynamicList(User(uids[0])))
    # loop.run_until_complete(t)
    # print(t.result())
    updateDatabaseFull()
