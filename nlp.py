import re
import sqlite3

blanketMatch = re.compile(r'(\[.*?])')
linkMatch = re.compile(
    r'((((ht|f)tp(s?))\://)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\;\?\'\\\+&%\$#\=~_\-]+))*)')
faceMatch = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9\s:-@]+")

database = sqlite3.connect("storage.db", check_same_thread=False)
c = database.cursor()


def filterComment(input: str):
    # this function intends to delete the following things:
    # 1. All strings inside (including) [,] blankets
    # 2. All links starting with https:// ftp:// or http:// that ends with a space
    input = blanketMatch.sub(" ", input)
    input = linkMatch.sub(" ", input)
    input = faceMatch.sub("", input)
    return input


if __name__ == "__main__":
    c.execute("SELECT ID,CONTENT FROM COMMENTS WHERE length(CONTENT)>40")
    result = c.fetchall()
    for _result in result:
        c.execute(f"INSERT INTO DCOMMENTS (ID,CONTENT)\
                  VALUES (?,?)", (_result[0], filterComment(_result[1])))
    database.commit()
