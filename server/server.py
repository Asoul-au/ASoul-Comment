import asyncio
import logging
import os.path
import os
import sqlite3
import uvicorn
from fastapi import FastAPI, Request

commentReturnList = ['ID', 'AVID', 'USERNAME', 'USERID', 'DATE', 'LIKE', 'FAN_TYPE', 'FAN_LEVEL', 'CONTENT',
                     'CONTENTTYPE']
videoReturnList = ['ID', 'AVID', 'TITLE', 'COVERIMG', 'VIEW', 'DATE', 'LAST_INDEXED']
dynamicsReturnList = ['ID', 'OID', 'CONTENT', 'DATE', 'LAST_INDEXED']

database = None
cursor = None
server = None

# TODO: there's something wrong about the working dir here... fix it someday
# if __name__ == '__main__':
if False:
    database_location = os.path.abspath(os.path.join("..", "storage.db"))
    log_location = os.path.abspath(os.path.join("..", "logs", "server.log"))
    if os.name == 'nt':
        extension_location = os.path.abspath(os.path.join("..", "distlib", "distlib_64.dll"))
    else:
        extension_location = os.path.abspath(os.path.join("..", "distlib", "distlib_64.so"))
else:
    database_location = os.path.abspath("storage.db")
    log_location = os.path.abspath(os.path.join("logs", "server.log"))
    if os.name == 'nt':
        extension_location = os.path.abspath(os.path.join("distlib", "distlib_64.dll"))
    else:
        extension_location = os.path.abspath(os.path.join("distlib", "distlib_64.so"))

logging.basicConfig(level=logging.DEBUG,
                    filename=log_location,
                    filemode="a",
                    format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s:%(lineno)s line-%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

database = sqlite3.connect(database_location, check_same_thread=False)
database.enable_load_extension(True)
database.load_extension(extension_location)
cursor = database.cursor()
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
server = FastAPI()


def startServer():
    loop = asyncio.get_event_loop() or asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    uvicorn.run("server:server", reload=True)


@server.get('/test')
async def returnTest():
    return {'message': 'Success!'}


@server.get('/comment')
async def returnComment(request: Request, cid: int = None, uid: int = None):
    if cid is None and uid is None:
        return {'message': 'Failed!'}
    global cursor
    if uid is not None:
        cursor.execute(f"SELECT * from COMMENTS WHERE USERID={uid}")
    elif cid == 233:
        cursor.execute(f"SELECT * FROM COMMENTS ORDER BY random() LIMIT 1")
    else:
        cursor.execute(f"SELECT * from COMMENTS WHERE ID={cid}")
    tmp = cursor.fetchall()
    if tmp:
        logging.info(f"From:{request.client} | Query on comment id={cid}")
        return {"result": (dict(zip(commentReturnList, _tmp)) for _tmp in tmp)}
    else:
        return {'message': f'id={cid} not found'}


@server.get('/video')
def returnVideo(id: int, request: Request):
    global cursor
    if id == 233:
        cursor.execute(f"SELECT * FROM VIDEOS ORDER BY random() LIMIT 1")
    else:
        cursor.execute(f"SELECT * FROM VIDEOS WHERE ID={id}")
    tmp = cursor.fetchall()[0]
    if tmp:
        logging.info(f"From:{request.client} | Query on comment id={id}")
        return zip(videoReturnList, tmp)
    else:
        return {'message': f'id={id} not found'}


@server.get('/dynamics')
async def returnVideo(id: int, request: Request):
    global cursor
    if id == 233:
        cursor.execute(f"SELECT * FROM DYNAMICS WHERE ID={id}")
    else:
        cursor.execute(f"SELECT * FROM DYNAMICS ORDER BY random() LIMIT 1")
    tmp = cursor.fetchall()[0]
    if tmp:
        logging.info(f"From:{request.client} | Query on comment id={id}")
        return zip(dynamicsReturnList, tmp)
    else:
        return {'message': f'id={id} not found'}
