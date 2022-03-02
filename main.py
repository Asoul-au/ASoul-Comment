# This is a python file that retrieves all the comments from A-Soul comment

import asyncio
import getopt
import logging
import sqlite3
import sys

import uvicorn
from bilibili_api import comment, user
from bilibili_api.comment import OrderType


# logging module setup:
def logSetup():
    logging.basicConfig(level=logging.INFO,
                        filename="main.log",
                        filemode="a",
                        format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s@%(lineno)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")


# ALL uids needed to be searched, raise an issue on GitHub in case you got any suggestions.
uids = [672328094, 672353429, 672346917, 672342685, 351609538]


async def getComments(vid):
    logging.info(f"trying to get comments from id={vid}")
    if vid == 233:
        # Test id, won't give out any response.
        return
    comments = []
    page = 1
    commentCount = 0
    while True:
        logging.info(f"trying to get comments from id={vid}, pn={page}")
        await asyncio.sleep(1)  # sleep for a while in case reach bilibili's limit.
        tmp = await comment.get_comments(vid, comment.ResourceType.VIDEO, page)
        for _tmp in tmp['replies']:
            # this is to add up the missing id in every <video> type... to point to AV number of the video
            _tmp['vid'] = vid
            for _stmp in _tmp['replies']:
                # execute the same process for the sub-replies
                _stmp['vid'] = vid
        comments.extend(tmp['replies'])
        commentCount += tmp['page']['size']
        page += 1
        # There might be something wrong with this function (or the end judgement)
        # while using this returns fewer results than expected...
        if commentCount >= tmp['page']['count']:
            break
    logging.info(f"A total of {commentCount} loaded from id={vid}")
    return comments


async def getHotComments(vid):
    logging.info(f"trying to get HOT comments from id={vid}")
    if vid == 233:
        # Test id, won't give out any response.
        return
    await asyncio.sleep(1)  # sleep for a while in case reach bilibili's limit.
    c = await comment.get_comments(vid, comment.ResourceType.VIDEO, order=OrderType.LIKE)  # sorting by like numbers
    tmp = c['replies']
    # TODO: this might need to change somehow to fast speed up :(
    for _tmp in tmp:
        # this is to add up the missing id in every <video> type... to point to AV number of the video
        _tmp['vid'] = vid
        for _stmp in _tmp['replies']:
            # execute the same process for the sub-replies
            _stmp['vid'] = vid
    return tmp


async def getVideoList(uid):
    logging.info(f"trying to get video list of id={uid}")
    pn = 1
    videos = []
    while True:
        await asyncio.sleep(1)  # sleep for a while in case reach bilibili's limit.
        tmp = await uid.get_videos(pn=pn)
        videos.extend(tmp['list']['vlist'])
        if pn * 30 >= tmp['page']['count']:
            # if all videos are loaded ...
            break
        pn += 1
    return videos


def printHelpLine():
    print("main.py ['help', 'create', 'run', 'update']")
    # TODO: More help message is needed, but I don't want to waste my time on it...
    # And btw, this should not appear in logging.


def createDataBase():
    # Um, this is ignoring the database that might already exist, a notice msg is printed:
    logSetup()
    print('''[Note]:DO NOT RUN THIS COMMAND if the storage.db already exists...
       IF you want to do a reset, remove the storage.db file first''')
    database = sqlite3.connect("storage.db")
    c = database.cursor()
    logging.info("storage.db loaded, init starting")
    c.execute('''CREATE TABLE VIDEOS
                (ID INT PRIMARY KEY NOT NULL,
                 AVID INT NOT NULL,
                 TITLE TEXT,
                 COVERIMG TEXT,
                 VIEW INT,
                 DATE INT);''')
    logging.info("Videos table created")
    c.execute('''CREATE TABLE COMMENTS
                (ID INT PRIMARY KEY NOT NULL,
                 AVID INT NOT NULL,
                 USERNAME TEXT NOT NULL,
                 USERID INT NOT NULL,
                 DATE INT,
                 LIKE INT,
                 FANTYPE TXT,
                 FANLEVEL INT,
                 CONTENT TEXT NOT NULL,
                 CONTENTTYPE INT);''')
    c.execute('''CREATE TABLE DCOMMENTS
                (ID INT PRIMARY KEY NOT NULL,
                 CONTENT TEXT);''')
    logging.info("Comments table created")
    logging.info("Database created, testing...")
    c.execute("INSERT INTO VIDEOS (ID,AVID,TITLE,COVERIMG,VIEW,DATE)\
                VALUES (233,233,'TEST','233',233,233)")
    c.execute("INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,CONTENT)\
                    VALUES (233,233,'TEST',233,'TEST')")
    database.commit()
    logging.info("Database created successful")
    c.close()
    pass  # endpoint, reserved for debug purposes.


def runServer():
    uvicorn.run(app="server:server", host="127.0.0.1", port=8080, reload=True)


def updateDataBase():
    logSetup()
    database = sqlite3.connect("storage.db")
    c = database.cursor()
    logging.info("Database loaded successful")
    # now, by updating the database, I would suggest a rule-based update.
    # updating all comments might be a little unrealistic...
    # the current setup for this is only fetching the hot comments,
    # which are defined as the first page of comments (sort with descending like numbers)
    videos = []
    loop = asyncio.get_event_loop()
    # Update video list
    logging.info("Updating video list")
    tasklist = []
    for uid in uids:
        tasklist.append(loop.create_task(getVideoList(user.User(uid))))
    for task in tasklist:
        loop.run_until_complete(task)
        videos.extend(task.result())
    logging.info("Up-to-date video list is now in the memory.")

    for _v in videos:
        c.execute(f"SELECT * FROM VIDEOS WHERE ID={_v['created']}")
        if len(c.fetchall()):
            # this means that the video have is already in the table.
            continue
        c.execute(f"INSERT INTO VIDEOS (ID,AVID,TITLE,COVERIMG,VIEW,DATE)\
                    VALUES (?,?,?,?,?,?)",
                  (_v['created'], _v['aid'], _v['title'], _v['pic'], _v['play'], _v['created']))
    database.commit()
    logging.info("Video list is synced in database")
    tasklist = []  # memory clear

    logging.info("Updating comment list")
    comments = []
    c.execute("SELECT AVID FROM VIDEOS")
    for _c in c:
        # Now _c[0] is a 'avid'.
        tasklist.append(loop.create_task(getHotComments(_c[0])))
    for task in tasklist:
        loop.run_until_complete(task)
        tmp = task.result()
        if tmp:
            comments.extend(tmp)
            for _tmp in tmp:
                comments.extend(_tmp['replies'])  # sub-comment
    logging.info("Up-to-date comment list is now in the memory.")

    for cmt in comments:
        c.execute(f"SELECT * FROM COMMENTS WHERE ID={cmt['rpid']}")
        if len(c.fetchall()):
            # this means that the comment is already in the database.
            continue
        if not cmt['member']['fans_detail']:
            c.execute(
                f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FANTYPE,FANLEVEL,CONTENT,CONTENTTYPE)\
                 VALUES (?,?,?,?,?,?,?,?,?,?)",
                (cmt['rpid'], cmt['vid'], cmt['member']['uname'],
                 cmt['member']['mid'], cmt['ctime'], cmt['like'],
                 "None", 0,
                 cmt['content']['message'], 0))
        else:
            c.execute(
                f"INSERT INTO COMMENTS (ID,AVID,USERNAME,USERID,DATE,LIKE,FANTYPE,FANLEVEL,CONTENT,CONTENTTYPE) \
                VALUES (?,?,?,?,?,?,?,?,?,?)",
                (cmt['rpid'], cmt['vid'], cmt['member']['uname'],
                 cmt['member']['mid'], cmt['ctime'], cmt['like'],
                 cmt['member']['fans_detail']['medal_name'],
                 cmt['member']['fans_detail']['level'],
                 cmt['content']['message'], 0))
    database.commit()
    logging.info("Up-to-date comments are synced up with database")


if __name__ == "__main__":
    # analyze the command line option:
    try:
        options, args = getopt.getopt(args=sys.argv[1:], shortopts="hcru",
                                      longopts=["help", "create", "run", "update"])
    except getopt.GetoptError:
        print("[Err]:Wrong parameters found.")
        printHelpLine()
        sys.exit(2)
    for opt, args in options:
        if opt in ('-h', '--help'):
            printHelpLine()
            sys.exit()
        elif opt in ('-c', '--create'):
            logSetup()
            logging.info("create new database requested")
            createDataBase()
            sys.exit()
        elif opt in ('-r', '--run'):
            logging.info("run server requested")
            runServer()
            sys.exit(2)
        elif opt in ('-u', "--update"):
            logSetup()
            logging.info("update database requested")
            updateDataBase()
            sys.exit()
