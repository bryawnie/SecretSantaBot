from sqlite3 import connect

def setup():
    con = connect("db.sqlite")
    cur = con.cursor()

    cur.execute("CREATE TABLE friends (user_id, name, game_id, ready)")
    cur.execute("CREATE TABLE likes (user_id, user_like_id, description)")
    cur.execute("CREATE TABLE dislikes (user_id, user_dislike_id, description)")
    cur.execute("CREATE TABLE games (game_id, title)")

    cur.execute(f"INSERT INTO games VALUES(0, 'Juego de Prueba')")

    con.commit()

if __name__ == "__main__":
    setup()