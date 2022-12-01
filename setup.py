from sqlite3 import connect

def setup():
    con = connect("db.sqlite")
    cur = con.cursor()

    cur.execute("CREATE TABLE friends (user_id, name, game_id, sk, pk)")
    cur.execute("CREATE TABLE likes (user_id, user_like_id, description)")
    cur.execute("CREATE TABLE dislikes (user_id, user_dislike_id, description)")

    con.commit()

if __name__ == "__main__":
    setup()