import logging
import sqlite3

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

commentReturnList = ['ID', 'AVID', 'USERNAME', 'USERID', 'DATE', 'LIKE', 'FANTYPE', 'FANLEVEL', 'CONTENT',
                     'CONTENTTYPE']
videoReturnList = ['ID', 'AVID', 'TITLE', 'COVERIMG', 'VIEW', 'DATE']
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://api.asoul-au.live",
    "https://asoul-au.live",
]

# Log settings:
logging.basicConfig(level=logging.INFO,
                    filename="server.log",
                    filemode="a",
                    format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s:%(lineno)s line-%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

# database setup
database = sqlite3.connect("storage.db", check_same_thread=False)
database.enable_load_extension(True)
database.load_extension("./distlib/distlib_64.dll")
c = database.cursor()
logging.info("storage.db loaded, start serving")

# server setup
server = FastAPI()
server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
logging.info("server started, working")


# access at http://api.asoul-au.live/test
@server.get('/test')
def returnTest():
    return {'message': 'Success!'}


# access at http://api.asoul-au.live/comment/233
@server.get('/comment/{cid}')
def returnComment(cid: int, request: Request):
    # c.execute(f"SELECT ID,AVID,USERNAME,USERID,DATE,CONTENT,CONTENTTYPE from COMMENTS WHERE ID={id}")
    c.execute(f"SELECT * from COMMENTS WHERE ID={cid}")
    tmp = c.fetchall()[0]
    logging.info(f"From IP:{request.client} Query on comment id={cid},result={tmp}")
    return zip(commentReturnList, tmp)


# access at http://api.asoul-au.live/video/233
@server.get('/video/{id}')
def returnVideo(cid: int, request: Request):
    # c.execute(f"SELECT ID,AVID,TITLE,DATE FROM VIDEOS WHERE ID={id}")
    c.execute(f"SELECT * FROM VIDEOS WHERE ID={cid}")
    tmp = c.fetchall()[0]
    logging.info(f"From IP:{request.client} Query on video id={cid},result={tmp}")
    return zip(videoReturnList, tmp)


# access at http://api.asoul-au.live/search?comment=233&full=true
@server.get('/search', response_model=set)
def returnSearch(comment: str, full: bool, request: Request):
    # comment=base64.decode(comment)
    logging.info(f"From IP:{request.client} Query on comment={comment} full?={str(full)}")
    # this is something worth digging...
    # TODO: filter comment, skipping
    c.execute(f"SELECT * FROM COMMENTS WHERE lsim(CONTENT, '{comment}') >0.2")
    res = c.fetchall()
    if full:
        tmp = []
        for _res in res:
            tmp.append(dict(zip(commentReturnList, _res)))
        logging.info(f"From IP:{request.client} Query on comment={id},result={tmp}")
        return tmp
    else:
        tmp = [_res[0] for _res in res]
        logging.info(f"-&From IP:{request.client} Query on comment={id},result={tmp}")
        return {"result": tmp}
        pass
