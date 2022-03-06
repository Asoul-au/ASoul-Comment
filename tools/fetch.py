import asyncio
import logging
import os.path
import sqlite3
import time
from bilibili_api import comment
from bilibili_api.user import User

uids = [672328094, 672353429, 672346917, 672342685, 351609538]
database = None
cursor = None

if __name__ == '__main__':
    database_location = os.path.abspath(os.path.join("..", "storage.db"))
    log_location = os.path.abspath(os.path.join("..", "logs", ".fetch.log"))
else:
    database_location = os.path.abspath("storage.db")
    log_location = os.path.abspath(os.path.join("logs", ".fetch.log"))

logging.basicConfig(level=logging.DEBUG, filename=log_location, filemode="a",
                    format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s@%(lineno)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


async def getFullCommentsFromDynamic(oid: int) -> list:
    try:
        comments = []
        page = 1
        commentCount = 0
        while True:
            await asyncio.sleep(0.5)
            tmp = await comment.get_comments(oid, comment.ResourceType.DYNAMIC, page)
            for _tmp in tmp['replies']:
                _tmp['oid'] = oid
                for _stmp in _tmp['replies']:
                    _stmp['oid'] = oid
            comments.extend(tmp['replies'])
            logging.info(f"getFullCommentsFromDynamic({oid}): page={page} fetched, +={len(tmp['replies'])}")
            commentCount += tmp['page']['size']
            page += 1
            if commentCount >= tmp['page']['acount'] or len(tmp['replies']) == 0:
                break
        logging.info(f"getFullCommentsFromDynamic({oid}): Done.")
        return comments
    except BaseException:
        logging.error(f"getFullCommentsFromDynamic({oid}): Error.")
        return []


async def getFullCommentsFromVideo(avid: int) -> list:
    try:
        comments = []
        page = 1
        commentCount = 0
        while True:
            await asyncio.sleep(0.5)
            tmp = await comment.get_comments(avid, comment.ResourceType.VIDEO, page)
            for _tmp in tmp['replies']:
                _tmp['vid'] = avid
                for _stmp in _tmp['replies']:
                    _stmp['vid'] = avid
            comments.extend(tmp['replies'])
            logging.info(f"getFullCommentsFromVideo({avid}): page={page} fetched, +={len(tmp['replies'])}")
            commentCount += tmp['page']['size']
            page += 1
            if commentCount >= tmp['page']['acount'] or len(tmp['replies']) == 0:
                break
        logging.info(f"getFullCommentsFromVideo({avid}): Done.")
        return comments
    except BaseException:
        logging.error(f"getFullCommentsFromVideo({avid}): Done.")
        return []


async def getVideoList(_user: User) -> list:
    page = 1
    videos = []
    while True:
        await asyncio.sleep(0.5)
        tmp = await _user.get_videos(pn=page)
        videos.extend(tmp['list']['vlist'])
        if page * 30 >= tmp['page']['count']:
            break
        page += 1
    logging.info(f"getVideoList(uid={_user.uid}): Done")
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
    logging.info(f"getDynamicList(uid={_user.uid}): Done")
    return dynamics


def createDatabase():
    global database, cursor
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
                 DATE INT,
                 LAST_SEARCHED INT);''')
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
                     DATE INT,
                     LAST_SEARCHED INT);''')
    database.commit()
    cursor.close()


def removeDatabase():
    if not os.path.exists(database_location):
        raise FileNotFoundError("storage.db don't exist")
    os.remove(database_location)


def commitCommentToDatabase(comments: list):
    global database, cursor
    database = sqlite3.connect(database_location, check_same_thread=False)
    cursor = database.cursor()
    for _comment in comments:
        if 'replies' in _comment and _comment['replies'] is not None:
            commitCommentToDatabase(_comment['replies'])
        cursor.execute(f"SELECT * FROM COMMENTS WHERE ID={_comment['rpid']}")
        if len(cursor.fetchall()):
            continue
        elif 'vid' in _comment:
            if not _comment['member']['fans_detail']:
                cursor.execute(
                    f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FAN_TYPE,FAN_LEVEL,CONTENT,CONTENTTYPE)\
                 VALUES (?,?,?,?,?,?,?,?,?,?)", (
                        _comment['rpid'], _comment['vid'], _comment['member']['uname'], _comment['member']['mid'],
                        _comment['ctime'], _comment['like'], "None", 0, _comment['content']['message'], 0))
            else:
                cursor.execute(
                    f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FAN_TYPE,FAN_LEVEL,CONTENT,CONTENTTYPE) \
                VALUES (?,?,?,?,?,?,?,?,?,?)", (
                        _comment['rpid'], _comment['vid'], _comment['member']['uname'], _comment['member']['mid'],
                        _comment['ctime'], _comment['like'], _comment['member']['fans_detail']['medal_name'],
                        _comment['member']['fans_detail']['level'], _comment['content']['message'], 0))
        else:
            if not _comment['member']['fans_detail']:
                cursor.execute(
                    f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FAN_TYPE,FAN_LEVEL,CONTENT,CONTENTTYPE)\
                 VALUES (?,?,?,?,?,?,?,?,?,?)", (
                        _comment['rpid'], _comment['oid'], _comment['member']['uname'], _comment['member']['mid'],
                        _comment['ctime'], _comment['like'], "None", 0, _comment['content']['message'], 1))
            else:
                cursor.execute(
                    f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FAN_TYPE,FAN_LEVEL,CONTENT,CONTENTTYPE) \
                VALUES (?,?,?,?,?,?,?,?,?,?)", (
                        _comment['rpid'], _comment['oid'], _comment['member']['uname'], _comment['member']['mid'],
                        _comment['ctime'], _comment['like'], _comment['member']['fans_detail']['medal_name'],
                        _comment['member']['fans_detail']['level'], _comment['content']['message'], 1))
    database.commit()


def updateDatabase(full=False):
    if not os.path.exists(database_location):
        createDatabase()
    global database, cursor
    database = sqlite3.connect(database_location, check_same_thread=False)
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
    database.commit()

    for dynamic in dynamics:
        cursor.execute(f"SELECT * FROM DYNAMICS WHERE ID={dynamic['desc']['timestamp']}")
        if len(cursor.fetchall()):
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
    database.commit()

    for video in videos:
        if full or (time.time() - video['created']) < 604800:
            cursor.execute(f"SELECT * FROM VIDEOS WHERE ID={video['created']}")
            if cursor.fetchall()[0][6] is not None:
                continue
            tmp = loop.create_task(getFullCommentsFromVideo(video['aid']))
            loop.run_until_complete(tmp)
            commitCommentToDatabase(tmp.result())
            cursor.execute(f"UPDATE VIDEOS SET LAST_SEARCHED={int(time.time())} WHERE ID={video['created']}")
            database.commit()

    for dynamic in dynamics:
        if full or (time.time() - dynamic['desc']['timestamp']) < 604800:
            cursor.execute(f"SELECT * FROM DYNAMICS WHERE ID={dynamic['desc']['timestamp']}")
            if cursor.fetchall()[0][4] is not None:
                continue
            tmp = loop.create_task(getFullCommentsFromDynamic(dynamic['desc']['dynamic_id']))
            loop.run_until_complete(tmp)
            commitCommentToDatabase(tmp.result())
            cursor.execute(
                f"UPDATE DYNAMICS SET LAST_SEARCHED={int(time.time())} WHERE ID={dynamic['desc']['timestamp']}")
            database.commit()


if __name__ == "__main__":
    updateDatabase(full=True)
